"""Cuentas y límites de intentos transaccionales en PostgreSQL."""
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from backend.app.persistencia_postgresql.conexion import conectar
from .contrasenas import HASH_SENUELO, hash_password, normalizar_usuario, verificar_password

ROLES = ('Analista', 'Administrador')


class LimiteIntentos(Exception):
    """Límite global por origen sin revelar si una cuenta existe."""

    def __init__(self, retry_after=900):
        self.retry_after = retry_after
        super().__init__('Límite de acceso')


class RepositorioUsuarios:
    def hay_cuentas(self):
        with conectar() as conn:
            return bool(conn.execute('SELECT EXISTS(SELECT 1 FROM usuarios_locales WHERE activo)').fetchone()['exists'])

    def obtener(self, ident):
        with conectar() as conn:
            return conn.execute('SELECT id, nombre, roles, activo, version_sesion FROM usuarios_locales WHERE id=%s',
                                (UUID(str(ident)),)).fetchone()

    def intentar(self, usuario, password, origen_hash):
        limitado = None
        resultado = None
        with conectar() as conn:
            # Serializar por origen; limitar fallos y ráfagas por separado.
            # Los éxitos no consumen la cuota de fallos ni borran fallos anteriores.
            intentos = conn.execute('''INSERT INTO auth_intentos_locales(origen_hash,cantidad,cantidad_total)
                VALUES (%s,0,1)
                ON CONFLICT (origen_hash) DO UPDATE SET
                cantidad=CASE WHEN auth_intentos_locales.inicio < CURRENT_TIMESTAMP-INTERVAL '15 minutes'
                              THEN 0 ELSE auth_intentos_locales.cantidad END,
                inicio=CASE WHEN auth_intentos_locales.inicio < CURRENT_TIMESTAMP-INTERVAL '15 minutes'
                            THEN CURRENT_TIMESTAMP ELSE auth_intentos_locales.inicio END,
                cantidad_total=CASE WHEN auth_intentos_locales.inicio_total < CURRENT_TIMESTAMP-INTERVAL '1 minute'
                                    THEN 1 ELSE LEAST(auth_intentos_locales.cantidad_total+1,1000000) END,
                inicio_total=CASE WHEN auth_intentos_locales.inicio_total < CURRENT_TIMESTAMP-INTERVAL '1 minute'
                                 THEN CURRENT_TIMESTAMP ELSE auth_intentos_locales.inicio_total END
                RETURNING cantidad,cantidad_total''', (origen_hash,)).fetchone()
            if intentos['cantidad'] >= 20:
                limitado = 900
            elif intentos['cantidad_total'] > 60:
                limitado = 60
            else:
                user = conn.execute('SELECT * FROM usuarios_locales WHERE usuario=%s FOR UPDATE',
                                    (usuario,)).fetchone()
                ahora = datetime.now(timezone.utc)
                if user is None or not user['activo'] or (user['bloqueado_hasta'] and user['bloqueado_hasta'] > ahora):
                    verificar_password(password, HASH_SENUELO)
                elif verificar_password(password, user['password_hash']):
                    conn.execute('''UPDATE usuarios_locales SET intentos_fallidos=0,
                        inicio_intentos=NULL, bloqueado_hasta=NULL WHERE id=%s''', (user['id'],))
                    resultado = user
                else:
                    inicio = user['inicio_intentos']
                    fallos = user['intentos_fallidos']
                    if inicio is None or inicio <= ahora-timedelta(minutes=15):
                        inicio, fallos = ahora, 0
                    fallos += 1
                    bloqueo = ahora+timedelta(minutes=15) if fallos >= 5 else None
                    conn.execute('''UPDATE usuarios_locales SET intentos_fallidos=%s,
                        inicio_intentos=%s, bloqueado_hasta=%s WHERE id=%s''',
                                 (fallos, inicio, bloqueo, user['id']))
                if resultado is None:
                    conn.execute('UPDATE auth_intentos_locales SET cantidad=LEAST(cantidad+1,1000000) WHERE origen_hash=%s',
                                 (origen_hash,))
        if limitado is not None:
            raise LimiteIntentos(limitado)
        return resultado

    def guardar(self, usuario, nombre, password, roles, actualizar=False):
        usuario = normalizar_usuario(usuario)
        if (not isinstance(nombre, str) or not 3 <= len(nombre.strip()) <= 70
                or any(ord(c) < 32 for c in nombre)):
            raise ValueError('El nombre debe tener de 3 a 70 caracteres sin caracteres de control.')
        if not isinstance(roles, list) or not roles or any(r not in ROLES for r in roles):
            raise ValueError('Selecciona únicamente los roles Analista o Administrador.')
        roles = list(dict.fromkeys(roles))
        hashed = hash_password(password)
        with conectar() as conn:
            # El bloqueo consultivo evita carreras crear/actualizar sin exponer SQL.
            conn.execute('SELECT pg_advisory_xact_lock(72618402)')
            actual = conn.execute('SELECT id FROM usuarios_locales WHERE usuario=%s FOR UPDATE',
                                  (usuario,)).fetchone()
            if actual and not actualizar:
                raise ValueError('La cuenta ya existe. Usa --actualizar expresamente para cambiarla.')
            if actualizar and not actual:
                raise ValueError('La cuenta no existe; omite --actualizar para crearla.')
            if actual:
                ident = actual['id']
                conn.execute('''UPDATE usuarios_locales SET nombre=%s, password_hash=%s, roles=%s,
                    activo=TRUE, version_sesion=version_sesion+1, intentos_fallidos=0,
                    inicio_intentos=NULL, bloqueado_hasta=NULL, actualizado=CURRENT_TIMESTAMP WHERE id=%s''',
                             (nombre.strip(), hashed, roles, ident))
            else:
                ident = uuid4()
                conn.execute('INSERT INTO usuarios_locales(id, usuario, nombre, password_hash, roles) VALUES (%s,%s,%s,%s,%s)',
                             (ident, usuario, nombre.strip(), hashed, roles))
            return str(ident)

    def desactivar(self, usuario):
        usuario = normalizar_usuario(usuario)
        with conectar() as conn:
            row = conn.execute('''UPDATE usuarios_locales SET activo=FALSE,
                version_sesion=version_sesion+1, actualizado=CURRENT_TIMESTAMP WHERE usuario=%s RETURNING id''',
                               (usuario,)).fetchone()
            if not row:
                raise ValueError('La cuenta no existe.')
