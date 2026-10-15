"""Acceso adicional aislado; no usa cuentas o secretos reales ni elimina datos de trabajo."""
import os
import io
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

import jwt
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.autenticacion_local.configuracion import configuracion, ConfiguracionLocalInvalida
from backend.app.autenticacion_local.contrasenas import hash_password, normalizar_usuario, verificar_password
from backend.app.autenticacion_local.repositorio import LimiteIntentos, RepositorioUsuarios
from backend.app.autenticacion_local.servicio import (AUDIENCE, ISSUER, KEY_ID, TOKEN_TYPE, es_token_local,
                                                    estado_local, iniciar_sesion, validar_token_local)
from backend.app.persistencia_postgresql.conexion import database_url
from backend.app.persistencia_postgresql.migrar import migrar
from backend.app.rutas_api.autenticacion_local import router
from scripts.crear_usuario_local import main as administrar_usuario

SECRET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_solo_fixture_no_real'
PASSWORD = 'Contraseña-aislada-12345'
ENV = {'LOCAL_AUTH_ENABLED': 'true', 'LOCAL_AUTH_SECRET': SECRET, 'LOCAL_AUTH_TOKEN_SECONDS': '1800',
       'DATABASE_URL': 'postgresql://no-conectar/fixture'}
app_local = FastAPI()
app_local.include_router(router)


@app_local.get('/protegida')
def protegida(user=Depends(usuario_actual)):
    return user


class HashLocalTests(unittest.TestCase):
    def test_hash_con_sal_aleatoria_y_verificacion(self):
        first, second = hash_password(PASSWORD), hash_password(PASSWORD)
        self.assertNotEqual(first, second)
        self.assertNotIn(PASSWORD, first)
        self.assertTrue(verificar_password(PASSWORD, first))
        self.assertFalse(verificar_password(PASSWORD+'otra', first))
        self.assertFalse(verificar_password(PASSWORD, 'texto-no-hash'))
        self.assertFalse(verificar_password(PASSWORD, first.replace('32768', '999999999')))

    def test_limites_de_password_y_usuario(self):
        for password in ['', 'corta', ' '*6, ' '*12, 'a'*129, None]:
            with self.assertRaises(ValueError):
                hash_password(password)
        self.assertEqual(normalizar_usuario(' Asesor.DEMO '), 'asesor.demo')
        for usuario in ['ab', 'otro@correo.test', 'a'*65, 'usuario\nmal', "abc' OR 1=1", None]:
            with self.assertRaises(ValueError):
                normalizar_usuario(usuario)

    def test_password_desde_seis_sin_requisitos_de_composicion(self):
        for password in ['123456', 'abcdef', 'áéíóúñ', 'a'*128]:
            with self.subTest(longitud=len(password)):
                self.assertTrue(verificar_password(password, hash_password(password)))


class AdministrarCuentaLocalTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, ENV)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_crear_y_actualizar_sin_password_en_argumentos_o_salida(self):
        for actualizar in (False, True):
            salida = io.StringIO()
            with patch('scripts.crear_usuario_local.getpass', side_effect=[PASSWORD, PASSWORD]) as preguntar, \
                    patch('scripts.crear_usuario_local.RepositorioUsuarios') as repo, patch('sys.stdout', salida):
                args = ['--usuario', 'asesor', '--nombre', 'Asesor demo', '--rol', 'Analista']
                if actualizar:
                    args.append('--actualizar')
                self.assertEqual(administrar_usuario(args), 0)
                repo.return_value.guardar.assert_called_once_with('asesor', 'Asesor demo', PASSWORD,
                                                                 ['Analista'], actualizar=actualizar)
                self.assertEqual(preguntar.call_args_list[0].args[0], 'Contraseña nueva (6–128 caracteres; entrada oculta): ')
            self.assertNotIn(PASSWORD, salida.getvalue())

    def test_no_guardar_si_confirmacion_difiere_y_desactivar_sin_password(self):
        with patch('scripts.crear_usuario_local.getpass', side_effect=[PASSWORD, PASSWORD+'otro']), \
                patch('scripts.crear_usuario_local.RepositorioUsuarios') as repo, patch('sys.stderr', io.StringIO()):
            self.assertEqual(administrar_usuario(['--usuario', 'asesor', '--nombre', 'Asesor demo']), 1)
            repo.return_value.guardar.assert_not_called()
        with patch('scripts.crear_usuario_local.getpass') as preguntar, \
                patch('scripts.crear_usuario_local.RepositorioUsuarios') as repo, patch('sys.stdout', io.StringIO()):
            self.assertEqual(administrar_usuario(['--usuario', 'asesor', '--desactivar']), 0)
            preguntar.assert_not_called()
            repo.return_value.desactivar.assert_called_once_with('asesor')


class AuthLocalTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, ENV)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.repo_patch = patch('backend.app.autenticacion_local.servicio.RepositorioUsuarios')
        self.repo = self.repo_patch.start().return_value
        self.addCleanup(self.repo_patch.stop)
        self.user = {'id': uuid4(), 'nombre': 'Asesor demo', 'roles': ['Analista'], 'activo': True, 'version_sesion': 1}
        self.repo.intentar.return_value = dict(self.user)
        self.repo.obtener.return_value = dict(self.user)
        now = int(time.time())
        self.claims = {'iss': ISSUER, 'aud': AUDIENCE, 'sub': str(self.user['id']), 'iat': now,
                       'nbf': now, 'exp': now+1800, 'jti': str(uuid4()), 'version_sesion': 1}
        self.client = TestClient(app_local)

    def token(self, **cambios):
        return jwt.encode({**self.claims, **cambios}, SECRET, algorithm='HS256',
                          headers={'kid': KEY_ID, 'typ': TOKEN_TYPE})

    def test_acceso_deshabilitado_por_defecto_y_clave_debil(self):
        for cambios in [{'LOCAL_AUTH_ENABLED': ''}, {'LOCAL_AUTH_ENABLED': 'false'},
                        {'LOCAL_AUTH_SECRET': 'corta'}, {'LOCAL_AUTH_SECRET': 'a'*80},
                        {'LOCAL_AUTH_TOKEN_SECONDS': '8'}, {'LOCAL_AUTH_TOKEN_SECONDS': 'texto'},
                        {'LOCAL_AUTH_SECRET': 'cambiar-clave-ejemplo-'*4}]:
            with patch.dict(os.environ, cambios), self.assertRaises(ConfiguracionLocalInvalida):
                configuracion()
        self.assertEqual(configuracion().duracion, 1800)

    def test_estado_publico_no_expone_secretos_ni_cuentas(self):
        self.repo.hay_cuentas.return_value = True
        self.assertEqual(estado_local(), {'habilitado': True, 'cuentas_disponibles': True})
        with patch.dict(os.environ, {'LOCAL_AUTH_ENABLED': 'false'}):
            self.assertEqual(estado_local(), {'habilitado': False, 'cuentas_disponibles': False})
        self.repo.hay_cuentas.side_effect = psycopg.OperationalError('dato privado')
        self.assertEqual(estado_local(), {'habilitado': False, 'cuentas_disponibles': False})

    def test_login_emite_token_separado_y_me_consulta_cuenta_actual(self):
        response = self.client.post('/api/v1/auth/local/login', json={'usuario': 'ASESOR', 'password': PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        data = response.json()
        self.assertEqual(data['token_type'], 'bearer')
        self.assertEqual(data['expires_in'], 1800)
        self.assertNotIn(PASSWORD, response.text)
        self.assertNotIn(SECRET, response.text)
        self.assertEqual(data['user']['proveedor'], 'local')
        self.assertEqual(data['user']['responsable'], f"Asesor demo [local:{self.user['id']}]")
        self.assertTrue(es_token_local(data['access_token']))
        response = self.client.get('/protegida', headers={'Authorization': 'Bearer '+data['access_token']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), data['user'])
        self.repo.intentar.assert_called_once()
        args = self.repo.intentar.call_args.args
        self.assertEqual(args[:2], ('asesor', PASSWORD))
        self.assertEqual(len(args[2]), 64)

    def test_login_fallo_generico_y_limite_ip(self):
        self.repo.intentar.return_value = None
        for usuario in ['asesor', 'inexistente']:
            response = self.client.post('/api/v1/auth/local/login', json={'usuario': usuario, 'password': PASSWORD})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()['detail'], 'Usuario o contraseña incorrectos.')
        self.repo.intentar.side_effect = LimiteIntentos()
        response = self.client.post('/api/v1/auth/local/login', json={'usuario': 'asesor', 'password': PASSWORD})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers['retry-after'], '900')

    def test_login_acepta_seis_y_rechaza_cinco_sin_eco(self):
        response = self.client.post('/api/v1/auth/local/login', json={'usuario': 'asesor', 'password': '123456'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.repo.intentar.call_args.args[:2], ('asesor', '123456'))
        self.repo.intentar.reset_mock()
        response = self.client.post('/api/v1/auth/local/login', json={'usuario': 'asesor', 'password': '12345'})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn('12345', response.text)
        self.repo.intentar.assert_not_called()

    def test_error_de_esquema_login_no_devuelve_password(self):
        for body in [{'usuario': 'a', 'password': PASSWORD}, {'usuario': 'asesor', 'password': 'clave-secreta-corta'},
                     {'usuario': 'asesor', 'password': PASSWORD, 'dato_extra': PASSWORD}]:
            # La segunda contraseña es válida en longitud; provocar un tipo inválido.
            if body.get('password') == 'clave-secreta-corta':
                body['password'] = {'no_imprimir': PASSWORD}
            response = self.client.post('/api/v1/auth/local/login', json=body)
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(PASSWORD, response.text)
        self.assertEqual(self.client.post('/api/v1/auth/local/login', content='no-json',
                         headers={'Content-Type': 'application/json'}).status_code, 422)

    def test_sin_password_default_ni_registro_publico(self):
        self.assertEqual(self.client.post('/api/v1/auth/local/register', json={}).status_code, 404)
        with patch.dict(os.environ, {'LOCAL_AUTH_ENABLED': 'false'}):
            response = self.client.post('/api/v1/auth/local/login', json={'usuario': 'asesor', 'password': PASSWORD})
            self.assertEqual(response.status_code, 503)
        self.assertEqual(self.client.get('/protegida').status_code, 401)

    def test_token_claims_firma_algoritmo_y_marcas(self):
        invalidos = [self.token(exp=1), self.token(iss='otro'), self.token(aud='otro'), self.token(aud=[AUDIENCE]),
                     self.token(nbf=int(time.time())+600), self.token(iat=1.5), self.token(version_sesion=True),
                     self.token(sub='no-uuid'), self.token(jti='no-uuid'), self.token(version_sesion=0),
                     self.token(exp=int(time.time())+7200),
                     jwt.encode(self.claims, SECRET+'otra', algorithm='HS256', headers={'kid': KEY_ID, 'typ': TOKEN_TYPE}),
                     jwt.encode(self.claims, SECRET, algorithm='HS384', headers={'kid': KEY_ID, 'typ': TOKEN_TYPE}),
                     jwt.encode(self.claims, SECRET, algorithm='HS256', headers={'kid': 'otra', 'typ': TOKEN_TYPE})]
        for token in invalidos:
            with self.subTest(token=token[:12]), self.assertRaises(HTTPException) as error:
                validar_token_local(token)
            self.assertEqual(error.exception.status_code, 401)
        for campo in self.claims:
            claims = dict(self.claims)
            claims.pop(campo)
            token = jwt.encode(claims, SECRET, algorithm='HS256', headers={'kid': KEY_ID, 'typ': TOKEN_TYPE})
            with self.assertRaises(HTTPException) as error:
                validar_token_local(token)
            self.assertEqual(error.exception.status_code, 401)

    def test_revocacion_cuenta_inactiva_roles_y_version(self):
        for user in [None, {**self.user, 'activo': False}, {**self.user, 'version_sesion': 2},
                     {**self.user, 'roles': []}, {**self.user, 'roles': ['Otro']}]:
            self.repo.obtener.return_value = user
            with self.assertRaises(HTTPException) as error:
                validar_token_local(self.token())
            self.assertEqual(error.exception.status_code, 401)
        with patch.dict(os.environ, {'LOCAL_AUTH_ENABLED': 'false'}), self.assertRaises(HTTPException) as error:
            validar_token_local(self.token())
        self.assertEqual(error.exception.status_code, 401)

    def test_token_local_invalido_nunca_reintenta_microsoft(self):
        token = self.token(iss='microsoft-falso')
        with patch('backend.app.autenticacion_entra_id.seguridad.validar_token') as entra:
            response = self.client.get('/protegida', headers={'Authorization': 'Bearer '+token})
            self.assertEqual(response.status_code, 401)
            entra.assert_not_called()
        # Un HS256 sin marcas locales sigue rechazado por el validador Entra original.
        token = jwt.encode(self.claims, SECRET, algorithm='HS256')
        response = self.client.get('/protegida', headers={'Authorization': 'Bearer '+token})
        self.assertEqual(response.status_code, 401)

    def test_fallo_postgresql_cierra_acceso_y_oculta_credenciales(self):
        self.repo.obtener.side_effect = psycopg.OperationalError('contraseña-no-imprimir')
        response = self.client.get('/protegida', headers={'Authorization': 'Bearer '+self.token()})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('contraseña-no-imprimir', response.text)
        self.repo.intentar.side_effect = psycopg.OperationalError('contraseña-no-imprimir')
        response = self.client.post('/api/v1/auth/local/login', json={'usuario': 'asesor', 'password': PASSWORD})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('contraseña-no-imprimir', response.text)


@unittest.skipUnless(os.getenv('RUN_POSTGRES_TESTS') == '1', 'Activar RUN_POSTGRES_TESTS=1 para PostgreSQL aislado.')
class AuthLocalPostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.url = database_url()
        self.schema = 'test_auth_' + uuid4().hex
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.env = patch.dict(os.environ, {**ENV, 'DATABASE_URL': make_conninfo(self.url, options='-c search_path='+self.schema)})
        self.env.start()
        migrar()
        migrar()
        self.repo = RepositorioUsuarios()

    def tearDown(self):
        self.env.stop()
        # El nombre fijo prefijado+UUID pertenece únicamente a este test.
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def crear(self):
        return self.repo.guardar('asesor', 'Asesor demo', PASSWORD, ['Analista'])

    def test_login_real_y_actualizacion_revoca(self):
        self.assertEqual(estado_local(), {'habilitado': True, 'cuentas_disponibles': False})
        ident = self.crear()
        token = iniciar_sesion('asesor', PASSWORD, '127.0.0.1')['access_token']
        self.assertEqual(validar_token_local(token)['id'], ident)
        self.assertTrue(estado_local()['cuentas_disponibles'])
        with self.assertRaises(ValueError):
            self.crear()
        self.repo.guardar('asesor', 'Asesor demo', PASSWORD+'nuevo', ['Administrador'], actualizar=True)
        with self.assertRaises(HTTPException) as error:
            validar_token_local(token)
        self.assertEqual(error.exception.status_code, 401)
        nuevo = iniciar_sesion('asesor', PASSWORD+'nuevo', '127.0.0.1')['access_token']
        self.assertEqual(validar_token_local(nuevo)['roles'], ['Administrador'])
        self.repo.desactivar('asesor')
        with self.assertRaises(HTTPException):
            validar_token_local(nuevo)
        self.assertFalse(estado_local()['cuentas_disponibles'])

    def test_password_de_seis_crear_y_resetear_sin_cambiar_hash_legacy(self):
        ident = self.crear()
        anterior = iniciar_sesion('asesor', PASSWORD, '127.0.0.1')['access_token']
        self.assertEqual(validar_token_local(anterior)['id'], ident)
        with self.assertRaises(ValueError):
            self.repo.guardar('asesor', 'Asesor demo', '12345', ['Analista'], actualizar=True)
        self.assertEqual(validar_token_local(anterior)['id'], ident)
        self.repo.guardar('asesor', 'Asesor demo', '123456', ['Analista'], actualizar=True)
        with self.assertRaises(HTTPException):
            validar_token_local(anterior)
        nuevo = iniciar_sesion('asesor', '123456', '127.0.0.1')['access_token']
        self.assertEqual(validar_token_local(nuevo)['id'], ident)
        self.repo.guardar('corta.demo', 'Cuenta demo', 'abcdef', ['Analista'])
        self.assertIn('access_token', iniciar_sesion('corta.demo', 'abcdef', '127.0.0.2'))

    def test_cinco_fallos_persisten_bloqueo_y_expiracion(self):
        self.crear()
        for _ in range(5):
            with self.assertRaises(HTTPException) as error:
                iniciar_sesion('asesor', PASSWORD+'incorrecta', '127.0.0.1')
            self.assertEqual(error.exception.status_code, 401)
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            row = conn.execute('SELECT intentos_fallidos, bloqueado_hasta FROM usuarios_locales').fetchone()
        self.assertEqual(row[0], 5)
        self.assertIsNotNone(row[1])
        with self.assertRaises(HTTPException):
            iniciar_sesion('asesor', PASSWORD, '127.0.0.1')
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            conn.execute("UPDATE usuarios_locales SET bloqueado_hasta=CURRENT_TIMESTAMP-INTERVAL '1 minute', inicio_intentos=CURRENT_TIMESTAMP-INTERVAL '1 hour'")
        self.assertIn('access_token', iniciar_sesion('asesor', PASSWORD, '127.0.0.1'))

    def test_limite_ip_cubre_usuarios_desconocidos_y_no_almacena_ip(self):
        for n in range(20):
            with self.assertRaises(HTTPException) as error:
                iniciar_sesion('noexiste'+str(n), PASSWORD, '198.51.100.8')
            self.assertEqual(error.exception.status_code, 401)
        with self.assertRaises(HTTPException) as error:
            iniciar_sesion('noexiste', PASSWORD, '198.51.100.8')
        self.assertEqual(error.exception.status_code, 429)
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            row = conn.execute('SELECT origen_hash,cantidad FROM auth_intentos_locales').fetchone()
            self.assertNotIn('198.51.100.8', row[0])
            self.assertEqual(row[1], 20)
            conn.execute("UPDATE auth_intentos_locales SET inicio=CURRENT_TIMESTAMP-INTERVAL '1 hour'")
        with self.assertRaises(HTTPException) as error:
            iniciar_sesion('noexiste', PASSWORD, '198.51.100.8')
        self.assertEqual(error.exception.status_code, 401)

    def test_no_modifica_evaluaciones_y_no_crea_password_predeterminada(self):
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM evaluaciones').fetchone()[0], 0)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM usuarios_locales').fetchone()[0], 0)
        with self.assertRaises(ValueError):
            self.repo.guardar('asesor', 'Asesor demo', 'corta', ['Analista'])
        with self.assertRaises(ValueError):
            self.repo.guardar('asesor', 'Asesor demo', PASSWORD, ['Otro'])
        self.crear()
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM evaluaciones').fetchone()[0], 0)
            self.assertNotIn(PASSWORD, conn.execute('SELECT password_hash FROM usuarios_locales').fetchone()[0])

    def test_25_logins_correctos_no_consumen_cuota_fallos(self):
        self.crear()
        for _ in range(25):
            self.assertIn('access_token', iniciar_sesion('asesor', PASSWORD, '198.51.100.9'))
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            row = conn.execute('SELECT cantidad,cantidad_total FROM auth_intentos_locales').fetchone()
            self.assertEqual(row, (0, 25))

    def test_exito_no_borra_fallos_y_rafaga_sigue_limitada(self):
        self.crear()
        with self.assertRaises(HTTPException):
            iniciar_sesion('desconocido', PASSWORD, '198.51.100.9')
        self.assertIn('access_token', iniciar_sesion('asesor', PASSWORD, '198.51.100.9'))
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            self.assertEqual(conn.execute('SELECT cantidad FROM auth_intentos_locales').fetchone()[0], 1)
            conn.execute('UPDATE auth_intentos_locales SET cantidad_total=60')
        with self.assertRaises(HTTPException) as error:
            iniciar_sesion('asesor', PASSWORD, '198.51.100.9')
        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(error.exception.headers['Retry-After'], '60')
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            conn.execute("UPDATE auth_intentos_locales SET inicio_total=CURRENT_TIMESTAMP-INTERVAL '2 minutes'")
        self.assertIn('access_token', iniciar_sesion('asesor', PASSWORD, '198.51.100.9'))
