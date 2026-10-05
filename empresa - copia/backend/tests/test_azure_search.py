import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.busqueda_azure_ai_search.buscador import ENDPOINT, INDEX


class SearchTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[usuario_actual] = lambda: {'roles': ['Analista']}
        self.client = TestClient(app)
        self.env = patch.dict(os.environ, {'AZURE_SEARCH_ENDPOINT': ENDPOINT,
            'AZURE_SEARCH_INDEX_NAME': INDEX, 'AZURE_SEARCH_QUERY_KEY': 'ficticia-no-real'})
        self.env.start()
        self.mock = patch('backend.app.integraciones.busqueda_azure_ai_search.buscador.httpx.Client')
        self.http = self.mock.start().return_value.__enter__.return_value

    def tearDown(self):
        app.dependency_overrides.clear()
        self.env.stop(); self.mock.stop()

    def test_sesion_obligatoria(self):
        app.dependency_overrides.clear()
        self.assertEqual(self.client.get('/api/v1/azure-search/estado').status_code, 401)
        self.assertEqual(self.client.get('/api/v1/azure-search/documentos').status_code, 401)
        self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen'}).status_code, 401)
        self.http.post.assert_not_called()

    def test_busqueda_y_fuentes(self):
        doc = dict(id='demo-1', fuente='guia', titulo='Guía', seccion='DEM-02', contenido='Texto', version='1.0', aviso='Demo')
        self.http.post.return_value = httpx.Response(200, json={'value': [doc]})
        response = self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen* OR (score)'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['resultados'], [doc])
        self.assertEqual(self.http.post.call_args.kwargs['json']['search'], 'margen OR score')
        self.assertNotIn('ficticia-no-real', response.text)

    def test_catalogo_automatico_completo_y_ordenado(self):
        docs = [dict(id=f'guia-DEM-0{n}', fuente='guia', titulo='Guía', seccion=f'DEM-0{n}',
                     contenido=f'Texto {n}', version='1.0', aviso='Demo') for n in (2, 1)]
        self.http.post.return_value = httpx.Response(200, json={'value': docs, '@odata.count': 2})
        response = self.client.get('/api/v1/azure-search/documentos')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['resultados'], list(reversed(docs)))
        params = self.http.post.call_args.kwargs['json']
        self.assertEqual(params['search'], '*')
        self.assertEqual(params['top'], 50)
        self.assertTrue(params['count'])
        self.assertNotIn('ficticia-no-real', response.text)

    def test_catalogo_vacio_y_acotado(self):
        self.http.post.return_value = httpx.Response(200, json={'value': [], '@odata.count': 0})
        self.assertEqual(self.client.get('/api/v1/azure-search/documentos').json()['resultados'], [])
        # No presentar una lista parcial como si fuese el catálogo completo.
        for payload in ({'value': [], '@odata.count': 51}, {'value': []},
                        {'value': [{}], '@odata.count': 1}, {'value': [], '@odata.count': True}):
            self.http.post.return_value = httpx.Response(200, json=payload)
            self.assertEqual(self.client.get('/api/v1/azure-search/documentos').status_code, 502)

    def test_catalogo_errores_sanitizados(self):
        for status in (401, 403, 404, 429, 500):
            self.http.post.return_value = httpx.Response(status, text='detalle privado')
            response = self.client.get('/api/v1/azure-search/documentos')
            self.assertGreaterEqual(response.status_code, 500)
            self.assertNotIn('detalle privado', response.text)
        self.http.post.side_effect = httpx.ReadTimeout('privado')
        self.assertEqual(self.client.get('/api/v1/azure-search/documentos').status_code, 504)
        self.http.post.side_effect = None
        with patch.dict(os.environ, {'AZURE_SEARCH_QUERY_KEY': ''}):
            self.assertEqual(self.client.get('/api/v1/azure-search/documentos').status_code, 503)

    def test_vacio_y_sin_coincidencias(self):
        for query in ('', '  ', '***', 'x' * 201):
            self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': query}).status_code, 422)
        self.http.post.assert_not_called()
        self.http.post.return_value = httpx.Response(200, json={'value': []})
        self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'inexistente'}).json()['resultados'], [])

    def test_errores_sanitizados(self):
        for status in (401, 403, 404, 429, 500, 302):
            self.http.post.return_value = httpx.Response(status, text='detalle privado')
            response = self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen'})
            self.assertGreaterEqual(response.status_code, 500)
            self.assertNotIn('detalle privado', response.text)
        self.http.post.side_effect = httpx.ReadTimeout('privado')
        self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen'}).status_code, 504)

    def test_configuracion_y_respuesta_invalida(self):
        with patch.dict(os.environ, {'AZURE_SEARCH_ENDPOINT': 'https://otro.example'}):
            self.assertFalse(self.client.get('/api/v1/azure-search/estado').json()['configurado'])
            self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen'}).status_code, 503)
        self.http.post.return_value = httpx.Response(200, json={'value': [{}]})
        self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen'}).status_code, 502)

    def test_documentos_acotados(self):
        path = Path(__file__).resolve().parents[2] / 'scripts/cargar_documentos_search.py'
        spec = importlib.util.spec_from_file_location('cargador', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        docs = module.documentos()
        self.assertEqual(len(docs), 14)
        self.assertEqual(len({doc['id'] for doc in docs}), 14)
        self.assertEqual({doc['fuente'] for doc in docs}, {'alcance-proyecto-v1', 'guia-demostracion-v1'})
        self.assertTrue(all(doc['aviso'] and doc['contenido'] for doc in docs))
