"""Proveedores alternativos aislados: sin llamadas Azure, descargas o base de trabajo."""
import asyncio
import importlib.util
import json
import os
from hashlib import sha256
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones import proveedores
from backend.app.integraciones.proveedores_locales import documentos, explicaciones
from backend.app.integraciones.cache_explicaciones import clave_explicacion
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.persistencia_postgresql.explicaciones import obtener_cache_explicaciones


class _Fixture:
    def setUp(self):
        self.env = patch.dict(os.environ, {
            'EXPLICACIONES_PROVEEDOR': 'local', 'DOCUMENTOS_PROVEEDOR': 'local', 'ML_PROVEEDOR': 'local',
            'OLLAMA_URL': 'http://127.0.0.1:11434', 'OLLAMA_MODEL': 'llama3.1:8b',
            'AZURE_OPENAI_API_KEY': 'NO-ENVIAR-CLAVE', 'AZURE_SEARCH_QUERY_KEY': 'NO-ENVIAR-CLAVE',
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.registro = {'version_modelo': 'reglas-demo-v1', 'margen_libre': 20000,
                         'nivel_riesgo_preliminar': 'Bajo', 'rfc': 'NO-ENVIAR-RFC',
                         'solicitud': {'rfc': 'NO-ENVIAR-RFC', 'ingresos_mensuales': 30000,
                                       'gastos_mensuales': 10000, 'score_buro_actual': 700,
                                       'observaciones': 'NO-ENVIAR-OBSERVACIONES'}}
        self.repo = Mock()
        self.repo.obtener.return_value = self.registro
        app.dependency_overrides[usuario_actual] = lambda: {'id': str(uuid4()), 'roles': ['Analista']}
        app.dependency_overrides[obtener_repositorio] = lambda: self.repo
        self.cache = Mock()
        self.cache.obtener_o_generar.side_effect = lambda _id, _key, _user, generar: generar()
        app.dependency_overrides[obtener_cache_explicaciones] = lambda: self.cache
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)
        self.url = f'/api/v1/evaluaciones/{uuid4()}/explicacion'


class ProveedoresLocalesTests(_Fixture, unittest.TestCase):

    def test_plantilla_no_inventa_igualdad_al_redondear_importes_originales(self):
        self.registro['solicitud'].update(ingresos_mensuales=30000.004, gastos_mensuales=10000.006)
        data = proveedores.explicar(self.registro)
        self.assertIn('Margen mensual guardado: 20,000.00 MXN', data['explicacion'])
        self.assertIn('importes originales redondeada', data['explicacion'])
        self.assertNotIn('30,000.00 − 10,000.01 = 20,000.00', data['explicacion'])

    def test_catalogo_mismos_ids_y_contenidos_del_cargador_azure(self):
        archivo = Path(__file__).resolve().parents[2] / 'scripts/cargar_documentos_search.py'
        spec = importlib.util.spec_from_file_location('cargador_prueba_local', archivo)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        esperado = [{k: v for k, v in doc.items() if k != '@search.action'} for doc in modulo.documentos()]
        self.assertEqual(documentos.catalogo(), sorted(esperado, key=lambda doc:
                         (doc['fuente'], doc['version'], doc['seccion'], doc['id'])))
        respuesta = self.client.get('/api/v1/azure-search/documentos')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()['resultados']), 15)
        self.assertEqual(respuesta.json()['proveedor'], 'local')

    def test_documentos_y_plantilla_no_consultan_red(self):
        self.assertEqual(proveedores.estado_explicaciones()['implementacion'], 'plantilla-reglas-demo')
        with patch('httpx.Client') as sync, patch('httpx.AsyncClient') as async_client:
            self.assertEqual(self.client.get('/api/v1/azure-search/documentos').status_code, 200)
            self.assertEqual(self.client.post('/api/v1/azure-search/buscar', json={'consulta': 'margen'}).status_code, 200)
            respuesta = self.client.post(self.url)
        sync.assert_not_called()
        async_client.assert_not_called()
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.json()['generada_por_ia'])
        self.assertEqual(respuesta.json()['proveedor'], 'local')
        self.assertNotIn('NO-ENVIAR', respuesta.text)
        self.repo.guardar.assert_not_called()
        self.repo.revisar.assert_not_called()

    def test_busqueda_literal_acentos_y_limite(self):
        sin = documentos.buscar('credito')['resultados']
        con = documentos.buscar('crédito')['resultados']
        self.assertEqual(sin, con)
        self.assertLessEqual(len(con), 5)
        self.assertEqual(documentos.buscar('terminoinexistente')['resultados'], [])
        self.assertEqual(documentos.buscar('margen terminoinexistente')['resultados'], [])
        with self.assertRaises(HTTPException) as contexto:
            documentos.buscar('***')
        self.assertEqual(contexto.exception.status_code, 422)

    def test_catalogo_incompleto_no_se_presenta_como_completo(self):
        with patch.object(documentos, 'ARCHIVOS', ('archivo_inexistente.md',)):
            self.assertFalse(documentos.configurado())
            self.assertEqual(self.client.get('/api/v1/azure-search/documentos').status_code, 503)
            self.assertEqual(self.client.post(self.url).status_code, 503)

    def test_plantilla_preserva_resultado_y_umbral_estricto(self):
        for margen, score, riesgo in ((20000, 700, 'Bajo'), (15000, 700, 'Medio'),
                                      (7000, 700, 'Alto'), (20000, 679, 'Medio')):
            registro = {**self.registro, 'margen_libre': margen, 'nivel_riesgo_preliminar': riesgo,
                        'solicitud': {**self.registro['solicitud'], 'gastos_mensuales': 30000 - margen,
                                      'score_buro_actual': score}}
            original = json.dumps(registro)
            salida = proveedores.explicar(registro)
            self.assertIn(f'Riesgo preliminar {riesgo}', salida['explicacion'])
            self.assertIn('Exactamente 15,000', salida['explicacion'])
            self.assertIn('exactamente 7,000', salida['explicacion'])
            self.assertEqual(salida['fuentes'][0]['id'], 'guia-demostracion-v1-DEM-02')
            self.assertEqual(json.dumps(registro), original)

    def test_version_y_registro_invalido_se_rechazan(self):
        for cambios in ({'version_modelo': 'otro'}, {'solicitud': {}}, {'margen_libre': float('nan')},
                         {'nivel_riesgo_preliminar': 'Inventado'}):
            with self.assertRaises(HTTPException) as contexto:
                proveedores.explicar({**self.registro, **cambios})
            self.assertEqual(contexto.exception.status_code, 409)

    def test_seleccion_invalida_sin_fallback(self):
        for variable, metodo in (('DOCUMENTOS_PROVEEDOR', proveedores.listar_documentos),
                                 ('EXPLICACIONES_PROVEEDOR', lambda: proveedores.explicar(self.registro)),
                                 ('ML_PROVEEDOR', proveedores.estado_ml)):
            with patch.dict(os.environ, {variable: 'desconocido'}), patch('httpx.Client') as cliente:
                with self.assertRaises(HTTPException) as contexto:
                    metodo()
                self.assertEqual(contexto.exception.status_code, 503)
                cliente.assert_not_called()

    def test_azure_es_default_y_selector_no_borra_sus_integraciones(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(proveedores.proveedor('explicaciones'), 'azure')
            self.assertEqual(proveedores.proveedor('documentos'), 'azure')
            self.assertEqual(proveedores.proveedor('ml'), 'azure')
            with patch('backend.app.integraciones.explicaciones_azure_openai.cliente.explicar', return_value={}) as azure:
                self.assertEqual(proveedores.explicar(self.registro)['proveedor'], 'azure')
                azure.assert_called_once_with(self.registro)

    def test_azure_openai_con_documentos_locales_inyeccion_explicita(self):
        with patch.dict(os.environ, {'EXPLICACIONES_PROVEEDOR': 'azure'}), \
                patch('backend.app.integraciones.explicaciones_azure_openai.cliente.explicar', return_value={}) as azure:
            proveedores.explicar(self.registro)
        self.assertEqual(azure.call_args.kwargs['buscador'], proveedores.buscar_documentos)

    def test_estado_no_contiene_secretos_ni_url_y_no_consulta_red(self):
        with patch('httpx.Client') as cliente:
            estado = proveedores.estados()
            respuesta = self.client.get('/api/v1/proveedores/estado')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), estado)
        self.assertEqual(set(estado), {'explicaciones', 'documentos', 'ml'})
        self.assertTrue(estado['explicaciones']['configurado'])
        self.assertFalse(estado['explicaciones']['generada_por_ia'])
        self.assertTrue(estado['ml']['configurado'])
        self.assertEqual(estado['ml']['origen'], 'scikit-learn local')
        self.assertNotIn('NO-ENVIAR', json.dumps(estado))
        self.assertNotIn('11434', json.dumps(estado))
        cliente.assert_not_called()

    def test_ml_local_nunca_carga_pickle_ni_consulta_azure(self):
        with patch('httpx.AsyncClient') as cliente, patch('pickle.load') as load:
            with self.assertRaises(HTTPException) as contexto:
                asyncio.run(proveedores.predecir({}))
        self.assertEqual(contexto.exception.status_code, 422)
        cliente.assert_not_called()
        load.assert_not_called()

    def test_endpoints_alternativos_siguen_autenticados(self):
        app.dependency_overrides.pop(usuario_actual)
        for ruta in ('/api/v1/azure-openai/estado', '/api/v1/azure-search/estado', '/api/v1/azure-ml/estado',
                     '/api/v1/proveedores/estado', '/api/v1/ml/estado'):
            self.assertEqual(self.client.get(ruta).status_code, 401)
        self.assertEqual(self.client.post(self.url).status_code, 401)
        self.repo.obtener.assert_not_called()


class HechosCalculadosTests(_Fixture, unittest.TestCase):
    """Hechos/razones producidos por código; no se evalúa un modelo real."""

    def construir_registro(self, score, margen, riesgo, version='reglas-demo-v2'):
        return {**self.registro, 'version_modelo': version, 'margen_libre': margen,
                'nivel_riesgo_preliminar': riesgo, 'solicitud': {**self.registro['solicitud'],
                'ingresos_mensuales': 30000, 'gastos_mensuales': 30000 - margen, 'score_buro_actual': score}}

    def test_bandas_inclusivas_y_categoria_mas_riesgosa_calculadas_sin_ia(self):
        severidad = {'Bajo': 0, 'Medio': 1, 'Alto': 2}
        scores = [(0, 'Alto', '0–499'), (200, 'Alto', '0–499'), (499, 'Alto', '0–499'),
                  (500, 'Medio', '500–679'), (679, 'Medio', '500–679'),
                  (680, 'Bajo', '680–1000'), (1000, 'Bajo', '680–1000')]
        for score, por_score, banda in scores:
            for margen, minimo in ((-100, 'Alto'), (7000, 'Alto'), (7000.01, 'Medio'),
                                    (15000, 'Medio'), (15000.01, 'Bajo'), (20000, 'Bajo')):
                riesgo = max((por_score, minimo), key=severidad.get)
                registro = self.construir_registro(score, margen, riesgo)
                original = json.dumps(registro)
                with self.subTest(score=score, margen=margen), patch('httpx.Client') as red:
                    hechos = explicaciones.hechos_calculados(explicaciones.escenario_permitido(registro))
                red.assert_not_called()
                self.assertEqual(hechos['riesgo_por_score'], por_score)
                self.assertEqual(hechos['banda_score'], banda)
                self.assertEqual(hechos['riesgo_minimo_por_margen'], minimo)
                self.assertEqual(hechos['resultado_guardado'], riesgo)
                self.assertEqual(json.dumps(registro), original)

    def test_version_historica_no_usa_bandas_v2_y_centavos_no_formateados(self):
        for score, margen, riesgo in ((200, 20000, 'Medio'), (680, 20000, 'Bajo'),
                                      (900, 15000, 'Medio'), (900, 7000, 'Alto')):
            hechos = explicaciones.hechos_calculados(explicaciones.escenario_permitido(
                self.construir_registro(score, margen, riesgo, 'reglas-demo-v1')))
            self.assertIsNone(hechos['banda_score'])
            self.assertEqual(hechos['resultado_guardado'], riesgo)
            self.assertIn('histórica', hechos['razon'])
        registro = self.construir_registro(900, 20000, 'Bajo')
        registro['solicitud'].update(ingresos_mensuales=30000.004, gastos_mensuales=10000.006)
        hechos = explicaciones.hechos_calculados(explicaciones.escenario_permitido(registro))
        self.assertEqual(hechos['margen_guardado'], 20000)
        self.assertNotIn('30,000.00 − 10,000.01 = 20,000.00', explicaciones._texto_hechos(
                         explicaciones.escenario_permitido(registro), hechos))

    def test_registro_incoherente_no_se_modifica_ni_se_inventa_explicacion(self):
        for registro in (self.construir_registro(200, 20000, 'Bajo'), self.construir_registro(900, 15000, 'Bajo'),
                         {**self.construir_registro(900, 20000, 'Bajo'), 'margen_libre': 18000}):
            original = json.dumps(registro)
            with self.assertRaises(HTTPException) as contexto:
                explicaciones.hechos_calculados(explicaciones.escenario_permitido(registro))
            self.assertEqual(contexto.exception.status_code, 409)
            self.assertEqual(json.dumps(registro), original)

    def test_clave_ollama_revision_v3_separa_exitos_antiguos_sin_cambiar_azure(self):
        for proveedor in ('ollama', 'azure'):
            with patch.dict(os.environ, {'EXPLICACIONES_PROVEEDOR': proveedor, 'AZURE_SEARCH_INDEX_NAME': 'fixture-indice'}):
                estado = proveedores.estado_explicaciones()
                descriptor = {'contrato': 'explicaciones-cache-v1', 'version_modelo': 'reglas-demo-v2',
                              'proveedor': proveedor, 'documentos': 'local',
                              'implementacion': estado.get('implementacion'), 'configurado': estado['configurado'],
                              'indice': 'fixture-indice'}
                antigua = sha256(json.dumps(descriptor, sort_keys=True).encode('utf-8')).hexdigest()
                nueva = clave_explicacion({'version_modelo': 'reglas-demo-v2'})
                if proveedor == 'ollama':
                    self.assertNotEqual(antigua, nueva)
                    descriptor['revision_ollama'] = 'hechos-servidor-comentario-academico-v3'
                    self.assertEqual(nueva, sha256(json.dumps(descriptor, sort_keys=True).encode('utf-8')).hexdigest())
                else:
                    self.assertEqual(antigua, nueva)


class OllamaTests(_Fixture, unittest.TestCase):
    """Respuesta Ollama simulada, sin ejecutar un modelo en pruebas unitarias."""

    def setUp(self):
        super().setUp()
        os.environ['EXPLICACIONES_PROVEEDOR'] = 'ollama'
        self.http_patch = patch.object(explicaciones.httpx, 'Client')
        self.http = self.http_patch.start().return_value.__enter__.return_value
        self.addCleanup(self.http_patch.stop)
        self.success()

    def success(self, **changes):
        datos = {'model': 'llama3.1:8b', 'done': True, 'message': {'role': 'assistant',
                 'content': json.dumps({'explicacion': 'Explicación académica con revisión humana.',
                                       'fuentes': ['guia-demostracion-v1-DEM-02']})}}
        datos.update(changes)
        self.http.post.return_value = httpx.Response(200, json=datos)

    def test_ollama_privacidad_contrato_y_no_descarga(self):
        respuesta = self.client.post(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['proveedor'], 'ollama')
        self.assertTrue(respuesta.json()['generada_por_ia'])
        llamada = self.http.post.call_args
        self.assertEqual(llamada.args[0], 'http://127.0.0.1:11434/api/chat')
        payload = llamada.kwargs['json']
        self.assertFalse(payload['stream'])
        self.assertEqual(payload['model'], 'llama3.1:8b')
        self.assertEqual(payload['options']['temperature'], 0)
        self.assertNotIn('NO-ENVIAR', json.dumps(llamada.kwargs))
        self.assertNotIn('headers', llamada.kwargs)
        self.assertEqual(self.http.post.call_count, 1)
        self.repo.guardar.assert_not_called()

    def test_solo_endpoints_locales_puerto_y_modelos_locales(self):
        for host in ('localhost', '127.0.0.1', '[::1]', 'host.docker.internal'):
            with patch.dict(os.environ, {'OLLAMA_URL': f'http://{host}:11434'}):
                self.assertTrue(explicaciones.configuracion_ollama()[2])
        for url in ('https://localhost:11434', 'http://localhost:8000', 'http://example.com:11434',
                    'http://user:pass@localhost:11434', 'http://localhost:11434/api',
                    'http://localhost:11434?api-key=secret', 'http://localhost:11434#fragmento',
                    'http://localhost:malformado', 'http://localhost:11434.evil.test'):
            with patch.dict(os.environ, {'OLLAMA_URL': url}):
                self.assertFalse(explicaciones.configuracion_ollama()[2])
                self.assertEqual(self.client.post(self.url).status_code, 503)
        for modelo in ('', 'modelo-cloud', 'https://modelo', '../archivo', 'modelo\ninyeccion'):
            with patch.dict(os.environ, {'OLLAMA_MODEL': modelo}):
                self.assertFalse(explicaciones.configuracion_ollama()[2])
        self.http.post.assert_not_called()

    def test_respuesta_incompleta_invalida_o_modelo_distinto(self):
        for cambios in ({'done': False}, {'model': 'modelo-distinto'}, {'message': None},
                         {'message': {'role': 'user', 'content': '{}'}},
                         {'message': {'role': 'assistant', 'tool_calls': [{}], 'content': '{}'}},
                         {'message': {'role': 'assistant', 'content': '{}'}},
                         {'message': {'role': 'assistant', 'content': '{"explicacion":"x","fuentes":["inventada"]}'}},
                         {'message': {'role': 'assistant', 'content': 'texto sin JSON'}}):
            self.success(**cambios)
            self.assertEqual(self.client.post(self.url).status_code, 502)
        self.assertEqual(self.http.post.call_count, 8)

    def test_errores_sanitizados_y_sin_cambio_automatico(self):
        with patch('backend.app.integraciones.explicaciones_azure_openai.cliente.explicar') as azure:
            for status in (404, 401, 500, 302):
                self.http.post.return_value = httpx.Response(status, text='NO-ENVIAR-SECRETO')
                respuesta = self.client.post(self.url)
                self.assertGreaterEqual(respuesta.status_code, 500)
                self.assertNotIn('NO-ENVIAR', respuesta.text)
            self.http.post.side_effect = httpx.ReadTimeout('NO-ENVIAR-ERROR')
            self.assertEqual(self.client.post(self.url).status_code, 504)
            azure.assert_not_called()

    def test_limite_concurrencia_y_liberacion_tras_fallo(self):
        slots = Mock()
        slots.acquire.return_value = False
        with patch.object(explicaciones, '_slots', slots):
            self.assertEqual(self.client.post(self.url).status_code, 429)
            slots.release.assert_not_called()
        self.http.post.side_effect = httpx.ReadTimeout('privado')
        slots.acquire.return_value = True
        with patch.object(explicaciones, '_slots', slots):
            self.assertEqual(self.client.post(self.url).status_code, 504)
            slots.release.assert_called_once()

    def test_estado_ollama_no_equivale_a_conexion_verificada(self):
        estado = proveedores.estado_explicaciones()
        self.assertTrue(estado['configurado'])
        self.assertEqual(estado['proveedor'], 'ollama')
        self.assertFalse(estado['conexion_verificada'])
        self.http.post.assert_not_called()

    def test_v2_hechos_servidor_separados_de_comentario_y_privacidad(self):
        self.registro.update(version_modelo='reglas-demo-v2', nivel_riesgo_preliminar='Alto')
        self.registro['solicitud']['score_buro_actual'] = 200
        original = json.dumps(self.registro)
        self.success(message={'role': 'assistant', 'content': json.dumps({
            'explicacion': 'Este ejercicio académico utiliza reglas ilustrativas. La interpretación requiere revisión humana.',
            'fuentes': ['guia-demostracion-v2-DEM-02']})})
        respuesta = self.client.post(self.url)
        self.assertEqual(respuesta.status_code, 200)
        data = respuesta.json()
        self.assertIn('Hechos calculados por el servidor (no generados por IA)', data['explicacion'])
        self.assertIn('El score capturado 200 pertenece a la banda 0–499: Alto.', data['explicacion'])
        self.assertIn('mínimo Bajo', data['explicacion'])
        self.assertIn('Comentario académico de IA (no calcula ni explica el resultado)', data['explicacion'])
        self.assertIn('no es una verificación semántica completa', data['aviso'])
        self.assertEqual(data['fuentes'][0]['version'], '2.0')
        payload = self.http.post.call_args.kwargs['json']
        hechos = json.loads(payload['messages'][1]['content'])['hechos_calculados_por_servidor']
        self.assertEqual(hechos['banda_score'], '0–499')
        self.assertEqual(hechos['resultado_guardado'], 'Alto')
        self.assertEqual(hechos['riesgo_minimo_por_margen'], 'Bajo')
        self.assertNotIn('NO-ENVIAR', json.dumps(payload))
        self.assertEqual(json.dumps(self.registro), original)

    def test_contradiccion_real_observada_se_rechaza_502_sin_fallback_ni_exito(self):
        self.registro.update(version_modelo='reglas-demo-v2', nivel_riesgo_preliminar='Alto')
        self.registro['solicitud']['score_buro_actual'] = 200
        contradicciones = (
            'El score (200) es mayor que el margen (20000). El riesgo es Alto porque el score es mayor que 499.',
            'El puntaje es superior al margen, por lo que corresponde un riesgo bajo.',
            'El score doscientos supera el umbral y por eso se puede aprobar el crédito.',
            'El score ２００ corresponde a Bajo.',
            'La aprobación está garantizada.',
        )
        with patch('backend.app.integraciones.explicaciones_azure_openai.cliente.explicar') as azure, \
                patch.object(explicaciones, 'explicar_local') as plantilla:
            for texto in contradicciones:
                self.success(message={'role': 'assistant', 'content': json.dumps({
                    'explicacion': texto, 'fuentes': ['guia-demostracion-v2-DEM-02']})})
                respuesta = self.client.post(self.url)
                self.assertEqual(respuesta.status_code, 502)
                self.assertNotIn(texto, respuesta.text)
                self.assertNotIn('explicacion', respuesta.json())
            azure.assert_not_called()
            plantilla.assert_not_called()
        self.repo.guardar.assert_not_called()
        self.repo.revisar.assert_not_called()

    def test_comentario_limitado_numeros_simbolos_control_y_extension(self):
        for texto in ('La cifra es 20.', 'Uno < otro.', 'Texto\u200b oculto.', 'texto ' * 66,
                      'a' * 601, 'El riesgo sería medio.', 'Más ingresos dan un mejor puntaje.'):
            with self.assertRaises(ValueError):
                explicaciones.validar_comentario_ia(texto)
        self.assertEqual(explicaciones.validar_comentario_ia(' Explicación académica con revisión humana. '),
                         'Explicación académica con revisión humana.')
