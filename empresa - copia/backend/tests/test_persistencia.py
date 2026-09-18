"""Pruebas de errores y pruebas reales en un esquema temporal aislado."""
import os
import unittest
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.persistencia_postgresql.conexion import database_url
from backend.app.persistencia_postgresql.migrar import migrar
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio, RepositorioEvaluaciones

PAYLOAD = dict(rfc='PRUEBA-POSTGRES', ingresos_mensuales=30000, gastos_mensuales=10000, score_buro_actual=700)
client = TestClient(app)


class DisponibilidadTests(unittest.TestCase):
    def tearDown(self):
        app.dependency_overrides.clear()

    def test_sin_configuracion_no_afirma_guardado(self):
        app.dependency_overrides[obtener_repositorio] = lambda: None
        self.assertFalse(client.post('/api/v1/evaluar', json=PAYLOAD).json()['guardado'])
        self.assertEqual(client.get('/api/v1/evaluaciones').status_code, 503)

    def test_error_postgres_no_expone_credenciales(self):
        app.dependency_overrides[obtener_repositorio] = RepositorioEvaluaciones
        with patch('backend.app.persistencia_postgresql.repositorio.conectar', side_effect=psycopg.OperationalError('contraseña secreta')):
            response = client.post('/api/v1/evaluar', json=PAYLOAD)
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('secreta', response.text)
            self.assertEqual(client.get('/api/v1/evaluaciones').status_code, 503)

    def test_cors_permite_idempotencia(self):
        response = client.options('/api/v1/evaluar', headers={
            'Origin': os.getenv('CORS_ORIGINS', 'http://127.0.0.1:5173').split(',')[0], 'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Idempotency-Key'})
        self.assertEqual(response.status_code, 200)


@unittest.skipUnless(os.getenv('RUN_POSTGRES_TESTS') == '1', 'Activar RUN_POSTGRES_TESTS=1 para probar PostgreSQL real.')
class PostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.url = database_url()
        self.schema = 'test_' + uuid4().hex
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.env = patch.dict(os.environ, {'DATABASE_URL': make_conninfo(self.url, options='-c search_path=' + self.schema)})
        self.env.start()
        app.dependency_overrides[obtener_repositorio] = RepositorioEvaluaciones
        migrar()
        migrar()  # Volver a migrar no recrea ni elimina datos.

    def tearDown(self):
        app.dependency_overrides.clear()
        self.env.stop()
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def test_guardado_reintento_lectura_y_conflicto(self):
        key = str(uuid4())
        headers = {'Idempotency-Key': key}
        first = client.post('/api/v1/evaluar', json=PAYLOAD, headers=headers)
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()['guardado'])
        self.assertEqual(first.json()['id'], key)
        again = client.post('/api/v1/evaluar', json=PAYLOAD, headers=headers)
        self.assertEqual(first.json(), again.json())
        # Cada petición utiliza una conexión nueva: se comprueba el commit real.
        saved = client.get('/api/v1/evaluaciones/' + key)
        self.assertEqual(saved.json()['solicitud'], PAYLOAD)
        self.assertEqual(len(client.get('/api/v1/evaluaciones').json()['items']), 1)
        conflict = client.post('/api/v1/evaluar', json={**PAYLOAD, 'gastos_mensuales': 15000}, headers=headers)
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(client.get('/api/v1/evaluaciones/' + str(uuid4())).status_code, 404)

    def test_validacion_paginacion_y_rollback(self):
        self.assertEqual(client.post('/api/v1/evaluar', json={**PAYLOAD, 'ingresos_mensuales': -1}).status_code, 422)
        self.assertEqual(client.get('/api/v1/evaluaciones').json()['items'], [])
        for _ in range(3):
            self.assertEqual(client.post('/api/v1/evaluar', json=PAYLOAD).status_code, 200)
        first = client.get('/api/v1/evaluaciones?limite=2').json()
        second = client.get('/api/v1/evaluaciones?limite=2&offset=2').json()
        self.assertTrue(first['hay_mas'])
        self.assertFalse(second['hay_mas'])
        self.assertEqual(len({row['id'] for row in first['items'] + second['items']}), 3)
        self.assertEqual(client.get('/api/v1/evaluaciones?limite=101').status_code, 422)
        with self.assertRaises(RuntimeError):
            with psycopg.connect(os.environ['DATABASE_URL']) as conn:
                conn.execute('DELETE FROM evaluaciones')
                raise RuntimeError('Forzar rollback de prueba')
        self.assertEqual(len(client.get('/api/v1/evaluaciones').json()['items']), 3)
