"""Tokens de prueba firmados localmente; nunca usa cuentas ni claves reales."""
import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import API_ID, CLIENT_ID, TENANT_ID, ISSUER, validar_token
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio


class EntraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.other = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def setUp(self):
        app.dependency_overrides.clear()
        now = int(time.time())
        self.claims = dict(aud=API_ID, iss=ISSUER, tid=TENANT_ID, azp=CLIENT_ID,
                           oid=str(uuid4()), sub='test-subject', ver='2.0', nbf=now-10, iat=now-10,
                           exp=now+300, scp='access_as_user', roles=['Analista'], name='Analista prueba')
        self.keys = patch('backend.app.autenticacion_entra_id.seguridad.claves_publicas')
        self.mock_keys = self.keys.start()
        self.mock_keys.return_value.get_signing_key_from_jwt.return_value = SimpleNamespace(key=self.private.public_key())
        self.addCleanup(self.keys.stop)
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)

    def token(self, **changes):
        return jwt.encode({**self.claims, **changes}, self.private, algorithm='RS256', headers={'kid': 'test-key'})

    def test_roles_validos(self):
        for role in ['Analista', 'Administrador']:
            user = validar_token(self.token(roles=[role]))
            self.assertEqual(user['roles'], [role])
            self.assertEqual(user['id'], self.claims['oid'])

    def test_marca_nueva_conserva_identificadores_y_controles_de_acceso(self):
        self.assertEqual(self.client.get('/openapi.json').json()['info']['title'], 'API de Riesgo Crediticio - NexoCredit')
        config = self.client.get('/api/v1/auth/config').json()
        self.assertEqual(config, {'clientId': CLIENT_ID, 'tenantId': TENANT_ID,
                                 'scope': f'api://{API_ID}/access_as_user', 'redirectUri': 'http://localhost:8080/'})
        response = self.client.get('/api/v1/auth/me')
        self.assertEqual(response.status_code, 401)
        self.assertIn('NexoCredit', response.json()['detail'])
        self.assertNotIn('PluriOne', response.text)
        response = self.client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {self.token(roles=[])}'})
        self.assertEqual(response.status_code, 403)
        self.assertIn('NexoCredit', response.json()['detail'])

    def test_firma_y_claims_requeridos(self):
        bad_signature = jwt.encode(self.claims, self.other, algorithm='RS256', headers={'kid': 'test-key'})
        for token in [bad_signature, 'no-es-token', self.token(aud=CLIENT_ID), self.token(iss='https://evil.test'),
                      self.token(tid=str(uuid4())), self.token(azp=str(uuid4())), self.token(exp=1),
                      self.token(nbf=int(time.time())+300), self.token(ver='1.0'), self.token(oid='incorrecto')]:
            with self.subTest(token=token[:12]), self.assertRaises(HTTPException) as error:
                validar_token(token)
            self.assertEqual(error.exception.status_code, 401)
        for key in ['exp', 'nbf', 'iat', 'iss', 'aud', 'tid', 'oid', 'sub', 'azp', 'ver']:
            claims = dict(self.claims); claims.pop(key)
            with self.assertRaises(HTTPException) as error:
                validar_token(jwt.encode(claims, self.private, algorithm='RS256', headers={'kid': 'test-key'}))
            self.assertEqual(error.exception.status_code, 401)

    def test_sin_ambito_o_rol_no_accede(self):
        for changes in [{'scp': ''}, {'scp': 'otro'}, {'scp': ['access_as_user']},
                        {'roles': []}, {'roles': ['Otro']}, {'roles': 'Analista'}]:
            with self.assertRaises(HTTPException) as error:
                validar_token(self.token(**changes))
            self.assertEqual(error.exception.status_code, 403)

    def test_algoritmos_no_permitidos(self):
        token = jwt.encode(self.claims, 'clave-ficticia-para-test-de-algoritmo', algorithm='HS256', headers={'kid': 'test-key'})
        with self.assertRaises(HTTPException) as error:
            validar_token(token)
        self.assertEqual(error.exception.status_code, 401)
        self.mock_keys.return_value.get_signing_key_from_jwt.assert_not_called()

    def test_todas_las_rutas_de_datos_requieren_sesion(self):
        for method, path in [('GET', '/api/v1/evaluaciones'), ('GET', '/api/v1/dashboard'),
                             ('GET', '/api/v1/azure-ml/estado'), ('GET', '/api/v1/auth/me'),
                             ('GET', '/api/v1/datos-financieros/indicadores'),
                             ('GET', f'/api/v1/evaluaciones/{uuid4()}'), ('POST', '/api/v1/evaluar'),
                             ('POST', '/api/v1/azure-ml/predecir'), ('POST', f'/api/v1/evaluaciones/{uuid4()}/revisiones')]:
            response = self.client.request(method, path)
            self.assertEqual(response.status_code, 401, path)
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/auth/config').status_code, 200)

    def test_identidad_confirmada_y_cors(self):
        response = self.client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {self.token()}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.claims['oid'])
        self.assertNotIn('access_token', response.text)
        origin = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')[0]
        response = self.client.options('/api/v1/auth/me', headers={'Origin': origin,
            'Access-Control-Request-Method': 'GET', 'Access-Control-Request-Headers': 'Authorization'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Authorization', response.headers['access-control-allow-headers'])

    def test_revision_no_acepta_suplantar_responsable(self):
        captured = []
        class Repo:
            def revisar(self, ident, revision):
                captured.append(revision.responsable)
                return {'responsable': revision.responsable}
        app.dependency_overrides[obtener_repositorio] = Repo
        response = self.client.post(f'/api/v1/evaluaciones/{uuid4()}/revisiones',
            headers={'Authorization': f'Bearer {self.token()}'},
            json={'id': str(uuid4()), 'version_anterior': 0, 'estado': 'Pendiente',
                  'observaciones': 'Prueba aislada', 'responsable': 'Otra persona'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured, [f"Analista prueba [{self.claims['oid']}]"])

    def test_fallo_de_claves_no_abre_acceso(self):
        self.mock_keys.return_value.get_signing_key_from_jwt.side_effect = jwt.PyJWKClientConnectionError('detalle privado')
        response = self.client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {self.token()}'})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('detalle privado', response.text)
