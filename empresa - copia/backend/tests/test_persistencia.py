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

    def test_nuevos_campos_persisten_y_conflicto(self):
        payload = {**PAYLOAD, 'deuda_actual': 50000.50, 'pagos_mensuales_creditos': 2500, 'dias_atraso_actual': 15}
        key = str(uuid4())
        headers = {'Idempotency-Key': key}
        self.assertEqual(client.post('/api/v1/evaluar', json=payload, headers=headers).status_code, 200)
        self.assertEqual(client.get('/api/v1/evaluaciones/' + key).json()['solicitud'], payload)
        self.assertEqual(client.post('/api/v1/evaluar', json=payload, headers=headers).status_code, 200)
        self.assertEqual(client.post('/api/v1/evaluar', json={**payload, 'dias_atraso_actual': 16}, headers=headers).status_code, 409)

    def test_dashboard_totales_filtros_y_ausencias(self):
        empty = client.get('/api/v1/dashboard').json()
        self.assertEqual(empty['total'], 0)
        self.assertIsNone(empty['deuda_promedio'])
        for n in range(12):
            payload = {**PAYLOAD, 'ingresos_mensuales': [30000, 20000, 11000][n % 3]}
            if n < 2:
                payload['deuda_actual'] = n * 100
            response = client.post('/api/v1/evaluar', json=payload)
            self.assertEqual(response.status_code, 200)
            with psycopg.connect(os.environ['DATABASE_URL']) as conn:
                conn.execute('UPDATE evaluaciones SET fecha = %s WHERE id = %s', ('2026-09-22T23:59:59Z' if n < 6 else '2026-09-23T00:00:00Z', response.json()['id']))
        data = client.get('/api/v1/dashboard').json()
        self.assertEqual(data['total'], 12)
        self.assertEqual([data[k] for k in ['bajo', 'medio', 'alto']], [4, 4, 4])
        self.assertEqual(float(data['deuda_promedio']), 50)
        self.assertEqual(data['con_deuda_capturada'], 2)
        self.assertEqual(client.get('/api/v1/dashboard?riesgo=Alto').json()['total'], 4)
        filtered = client.get('/api/v1/dashboard?desde=2026-09-22&hasta=2026-09-22').json()
        self.assertEqual(filtered['total'], 6)
        self.assertEqual(client.get('/api/v1/dashboard?desde=2026-09-22&hasta=2026-09-22&riesgo=Bajo').json()['total'], 2)
        for query in ['riesgo=Otro', 'desde=incorrecto', 'desde=2026-09-23&hasta=2026-09-22']:
            self.assertEqual(client.get('/api/v1/dashboard?' + query).status_code, 422)

    def test_revision_manual_historial_reintentos_y_conflictos(self):
        saved = client.post('/api/v1/evaluar', json=PAYLOAD).json()
        url = '/api/v1/evaluaciones/' + saved['id']
        self.assertEqual(client.get(url).json()['version_revision'], 0)
        payload = dict(id=str(uuid4()), version_anterior=0, estado='Aprobada', responsable='Analista demo', observaciones='Revisión ficticia')
        first = client.post(url + '/revisiones', json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(client.post(url + '/revisiones', json=payload).json(), first.json())
        self.assertEqual(client.post(url + '/revisiones', json={**payload, 'observaciones': 'Otra'}).status_code, 409)
        self.assertEqual(client.post(url + '/revisiones', json={**payload, 'id': str(uuid4())}).status_code, 409)
        second = {**payload, 'id': str(uuid4()), 'version_anterior': 1, 'estado': 'Rechazada'}
        self.assertEqual(client.post(url + '/revisiones', json=second).status_code, 200)
        detail = client.get(url).json()
        self.assertEqual(detail['estado_revision'], 'Rechazada')
        self.assertEqual(len(detail['revisiones']), 2)
        self.assertEqual(detail['solicitud'], PAYLOAD)
        self.assertEqual(detail['nivel_riesgo_preliminar'], saved['nivel_riesgo_preliminar'])
        for change in [{'estado': 'Otro'}, {'responsable': '   '}, {'observaciones': ''}, {'observaciones': 'x' * 2001}, {'version_anterior': -1}]:
            self.assertEqual(client.post(url + '/revisiones', json={**payload, **change}).status_code, 422)
        self.assertEqual(client.post('/api/v1/evaluaciones/' + str(uuid4()) + '/revisiones', json=payload).status_code, 404)
