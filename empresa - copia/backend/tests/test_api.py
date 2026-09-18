import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio

client = TestClient(app)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        # Las pruebas de reglas no escriben en la base de uso local.
        app.dependency_overrides[obtener_repositorio] = lambda: None

    def tearDown(self):
        app.dependency_overrides.clear()

    def payload(self, **changes):
        return dict(rfc="AAAA010101AA1", ingresos_mensuales=30000,
                    gastos_mensuales=10000, score_buro_actual=700, **changes)

    def test_demo_explains_result(self):
        response = client.post('/api/v1/evaluar', json=self.payload())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['margen_libre'], 20000)
        self.assertEqual(data['nivel_riesgo_preliminar'], 'Bajo')
        self.assertEqual(data['modo'], 'demostracion')
        self.assertEqual(len(data['factores']), 3)

    def test_boundaries_and_negative_margin(self):
        for income, score, expected in [(25000, 700, 'Medio'), (17000, 700, 'Alto'), (30000, 679, 'Medio'), (5000, 700, 'Alto')]:
            with self.subTest(income=income, score=score):
                payload = self.payload()
                payload.update(ingresos_mensuales=income, score_buro_actual=score)
                self.assertEqual(client.post('/api/v1/evaluar', json=payload).json()['nivel_riesgo_preliminar'], expected)

    def test_free_format_identifier(self):
        for identifier in ['AAAD33123232', 'cliente de prueba #1', 'abc', '123', 'áé / ejemplo largo sin formato fiscal']:
            with self.subTest(identifier=identifier):
                payload = self.payload()
                payload['rfc'] = identifier
                response = client.post('/api/v1/evaluar', json=payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['rfc'], identifier)

    def test_invalid_inputs(self):
        for field, value in [('rfc', ''), ('ingresos_mensuales', 0), ('gastos_mensuales', -1), ('score_buro_actual', 1001), ('score_buro_actual', 650.5), ('ingresos_mensuales', 'Infinity')]:
            with self.subTest(field=field, value=value):
                payload = self.payload()
                payload[field] = value
                self.assertEqual(client.post('/api/v1/evaluar', json=payload).status_code, 422)

    def test_cors_rejects_unknown_origin(self):
        response = client.options('/api/v1/evaluar', headers={'Origin': 'https://unknown.example', 'Access-Control-Request-Method': 'POST'})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('access-control-allow-origin', response.headers)


if __name__ == '__main__':
    unittest.main()
