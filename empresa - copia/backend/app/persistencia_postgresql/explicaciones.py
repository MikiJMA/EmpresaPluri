"""Caché privada y cuotas compartidas entre procesos, sin RFC ni clave de proveedor."""
from hashlib import sha256
from fastapi import HTTPException
from psycopg.types.json import Jsonb
from .conexion import conectar, database_url


class CacheExplicaciones:
    def obtener_o_generar(self, evaluacion, clave, usuario, generar):
        user_hash = sha256(usuario.encode('utf-8')).hexdigest()
        error = None
        with conectar() as conn:
            # Locks de sesión sobreviven al commit de la reserva. conectar() abre
            # una conexión dedicada, no pooled; al cerrarse libera ambos locks.
            if not conn.execute('SELECT pg_try_advisory_lock(72618403,hashtext(%s)) AS ok',
                                (str(evaluacion)+clave,)).fetchone()['ok']:
                raise HTTPException(429, 'La explicación ya se está generando. Espera antes de consultar.', headers={'Retry-After': '10'})
            cached = conn.execute('SELECT *, vence>CURRENT_TIMESTAMP AS vigente FROM cache_explicaciones WHERE evaluacion_id=%s AND clave=%s',
                                  (evaluacion, clave)).fetchone()
            if cached and cached['vigente']:
                if cached['error_http']:
                    raise HTTPException(cached['error_http'], cached['error_detalle'])
                return cached['respuesta']
            if not conn.execute('SELECT pg_try_advisory_lock(72618404,hashtext(%s)) AS ok', (user_hash,)).fetchone()['ok']:
                raise HTTPException(429, 'Ya hay una generación en curso para tu cuenta.', headers={'Retry-After': '10'})
            cantidad = conn.execute('''INSERT INTO cuotas_explicaciones(usuario_hash,cantidad) VALUES (%s,1)
                ON CONFLICT(usuario_hash) DO UPDATE SET
                cantidad=CASE WHEN cuotas_explicaciones.inicio<CURRENT_TIMESTAMP-INTERVAL '1 hour' THEN 1 ELSE cuotas_explicaciones.cantidad+1 END,
                inicio=CASE WHEN cuotas_explicaciones.inicio<CURRENT_TIMESTAMP-INTERVAL '1 hour' THEN CURRENT_TIMESTAMP ELSE cuotas_explicaciones.inicio END
                RETURNING cantidad''', (user_hash,)).fetchone()['cantidad']
            if cantidad > 10:
                raise HTTPException(429, 'Se alcanzó el límite de 10 generaciones por hora para tu cuenta. Las explicaciones en caché siguen disponibles.',
                                    headers={'Retry-After': '3600'})
            # No iniciar proveedor alguno si la reserva no pudo persistirse.
            # Un error, caída del proceso o rollback posterior ya no borra el intento.
            conn.commit()
            try:
                resultado = generar()
            except HTTPException as exc:
                # Solo mensajes saneados de nuestros adaptadores, no excepciones externas.
                error = HTTPException(exc.status_code, exc.detail, headers=exc.headers)
            except Exception:
                # No reflejar excepción/payload/llaves. Sin reintento automático.
                error = HTTPException(503, 'No se pudo generar la explicación. No se reintentó automáticamente; el intento quedó contabilizado y puede haber consumo.')
            if error:
                conn.execute('''INSERT INTO cache_explicaciones(evaluacion_id,clave,error_http,error_detalle,vence)
                    VALUES (%s,%s,%s,%s,CURRENT_TIMESTAMP+INTERVAL '1 minute')
                    ON CONFLICT(evaluacion_id,clave) DO UPDATE SET respuesta=NULL,error_http=EXCLUDED.error_http,
                    error_detalle=EXCLUDED.error_detalle,vence=EXCLUDED.vence''', (evaluacion, clave, error.status_code, error.detail))
            else:
                conn.execute('''INSERT INTO cache_explicaciones(evaluacion_id,clave,respuesta,vence)
                    VALUES (%s,%s,%s,CURRENT_TIMESTAMP+INTERVAL '24 hours')
                    ON CONFLICT(evaluacion_id,clave) DO UPDATE SET respuesta=EXCLUDED.respuesta,error_http=NULL,
                    error_detalle=NULL,vence=EXCLUDED.vence''', (evaluacion, clave, Jsonb(resultado)))
        # El error saneado se conserva un minuto; cuota ya persistida antes de generar.
        if error:
            raise error
        return resultado


def obtener_cache_explicaciones():
    return CacheExplicaciones() if database_url() else None
