import os
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES


class AzureMLTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[usuario_actual] = lambda: {'responsable': 'Prueba aislada', 'roles': ['Analista']}
        self.addCleanup(app.dependency_overrides.clear)
        self.env = patch.dict(os.environ, {'AZURE_ML_SCORING_URI': '', 'AZURE_ML_API_KEY': '', 'AZURE_ML_MODEL_ID': ''})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = TestClient(app)
        self.values = {name: 0 for name in FEATURES}
        self.values['LIMIT_BAL'] = 20000

    def configure(self):
        os.environ.update(AZURE_ML_SCORING_URI='https://demo.eastus.inference.ml.azure.com/score',
                          AZURE_ML_API_KEY='secret-test', AZURE_ML_MODEL_ID='candidate:1')

    def send(self, values=None):
        return self.client.post('/api/v1/azure-ml/predecir', json={'valores': self.values if values is None else values})

    def test_unconfigured(self):
        self.assertFalse(self.client.get('/api/v1/azure-ml/estado').json()['configurado'])
        self.assertEqual(self.send().status_code, 503)

    def test_invalid_fields(self):
        for name, value in [('PAY_0', 10), ('PAY_AMT1', -1), ('LIMIT_BAL', 0), ('BILL_AMT1', True), ('BILL_AMT1', 1.5), ('BILL_AMT1', '1')]:
            with self.subTest(name=name, value=value):
                self.assertEqual(self.send({**self.values, name: value}).status_code, 422)
        self.assertEqual(self.send({**self.values, 'RFC': 1}).status_code, 422)
        self.assertEqual(self.send({}).status_code, 422)

    def test_no_arbitrary_host(self):
        self.configure()
        for url in ['http://demo.eastus.inference.ml.azure.com/score', 'https://evil.test/score',
                    'https://demo.inference.ml.azure.com.evil.test/score']:
            os.environ['AZURE_ML_SCORING_URI'] = url
            self.assertEqual(self.send().status_code, 503)

    @patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    def test_success_contract_and_no_secret(self, post):
        self.configure()
        for output in [[True], {'predictions': [False]}]:
            post.return_value = httpx.Response(200, json=output, request=httpx.Request('POST', 'https://example.test'))
            response = self.send()
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('secret-test', response.text)
            payload = post.call_args.kwargs['json']['input_data']
            self.assertEqual(payload['columns'], FEATURES)
            self.assertEqual(payload['data'], [[self.values[name] for name in FEATURES]])

    @patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    def test_rejects_unexpected_responses(self, post):
        self.configure()
        for body in [[1], ['false'], [], [True, False], {'predictions': [0.7]}, None]:
            post.return_value = httpx.Response(200, json=body, request=httpx.Request('POST', 'https://example.test'))
            self.assertEqual(self.send().status_code, 502)

    @patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    def test_errors_are_sanitized(self, post):
        self.configure()
        for code in [401, 403, 429, 500, 302]:
            post.return_value = httpx.Response(code, text='secret-test', request=httpx.Request('POST', 'https://example.test'))
            response = self.send()
            self.assertEqual(response.status_code, 502)
            self.assertNotIn('secret-test', response.text)
        post.side_effect = httpx.ReadTimeout('secret-test')
        self.assertEqual(self.send().status_code, 504)
