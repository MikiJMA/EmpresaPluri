"""Valoración generativa del mismo escenario: proveedor simulado, privacidad y caché."""
import copy
import json
import os
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from psycopg import OperationalError

from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.evaluacion_crediticia import valoracion_ia as motor
from backend.app.integraciones.proveedores_locales import explicaciones
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.persistencia_postgresql.explicaciones import obtener_cache_explicaciones


class ValoracionIATests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'VALORACION_IA_PROVEEDOR': 'ollama', 'OLLAMA_MODEL': 'llama3.1:8b',
                                         'OLLAMA_URL': 'http://127.0.0.1:11434', 'DATABASE_URL': ''})
        self.env.start(); self.addCleanup(self.env.stop)
        self.addCleanup(app.dependency_overrides.clear)
        self.id = uuid4()
        self.captura = dict(ingresos_mensuales=30000, gastos_mensuales=10000, deuda_actual=50000,
                            pagos_mensuales_creditos=2500, dias_atraso_actual=0, score_buro_actual=900)
        self.registro = {'id': str(self.id), 'rfc': 'NO-ENVIAR-RFC', 'nivel_riesgo_preliminar': 'Bajo',
                         'margen_libre': 20000, 'version_modelo': 'reglas-demo-v2',
                         'solicitud': {**self.captura, 'rfc': 'NO-ENVIAR-RFC', 'curp': 'NO-ENVIAR-CURP', 'nombre': 'NO-ENVIAR-NOMBRE'}}
        self.repo = Mock(); self.repo.obtener.return_value = self.registro
        self.cache = Mock(); self.cache.obtener_o_generar.side_effect = lambda _id, _key, _user, generar: generar()
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'cuenta-qa', 'roles': ['Analista']}
        app.dependency_overrides[obtener_repositorio] = lambda: self.repo
        app.dependency_overrides[obtener_cache_explicaciones] = lambda: self.cache
        self.http_patch = patch.object(motor.httpx, 'Client')
        self.http = self.http_patch.start().return_value.__enter__.return_value
        self.addCleanup(self.http_patch.stop)
        self.salida = {'nivel_riesgo_ia': 'Medio', 'factores': ['deuda_ingreso', 'pagos_ingreso', 'score_capturado'],
                       'recomendaciones': ['revisar_deuda_pagos', 'revision_humana']}
        self.respuesta()
        self.client = TestClient(app)
        self.url = f'/api/v1/evaluaciones/{self.id}/valoracion-ia'

    def respuesta(self, salida=None, **changes):
        data = {'done': True, 'model': 'llama3.1:8b', 'message': {'role': 'assistant', 'content': json.dumps(self.salida if salida is None else salida)}}
        data.update(changes)
        self.http.post.return_value = httpx.Response(200, json=data)

    def test_valora_mismos_seis_datos_no_copia_reglas_y_no_cambia_registro(self):
        original = copy.deepcopy(self.registro)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        data = response.json()
        self.assertEqual(data['riesgo_por_reglas'], 'Bajo')
        self.assertEqual(data['nivel_riesgo_ia'], 'Medio')
        self.assertEqual(data['evaluacion_id'], str(self.id))
        self.assertIs(data['reglas_modificadas'], False)
        self.assertIs(data['generada_por_ia'], True)
        self.assertEqual(data['modelo'], 'llama3.1:8b')
        self.assertEqual(data['datos_evaluados'], {**self.captura, 'margen_mensual': 20000, 'pagos_ingreso': 8.33, 'deuda_ingreso': 1.67})
        payload = self.http.post.call_args.kwargs['json']
        enviados = json.loads(payload['messages'][1]['content'])
        self.assertEqual(enviados['datos_capturados_e_indicadores'], data['datos_evaluados'])
        for secreto in ('NO-ENVIAR', 'riesgo_por_reglas', 'nivel_riesgo_preliminar', 'version_modelo'):
            self.assertNotIn(secreto, json.dumps(payload))
        self.assertNotIn('NO-ENVIAR', response.text)
        self.assertEqual(self.registro, original)
        self.repo.guardar.assert_not_called(); self.repo.revisar.assert_not_called()
        self.assertEqual(self.cache.obtener_o_generar.call_args.args[2], 'valoracion-ia:cuenta-qa')
        self.assertEqual(self.http.post.call_args.args[0], 'http://127.0.0.1:11434/api/chat')

    def test_cero_real_distinto_de_datos_ausentes_y_registros_v1(self):
        for campo in motor.CAMPOS:
            original = self.registro['solicitud'].pop(campo)
            self.assertEqual(self.client.post(self.url).status_code, 409)
            self.registro['solicitud'][campo] = original
        self.http.post.assert_not_called()
        self.registro['solicitud'].update(deuda_actual=0, pagos_mensuales_creditos=0, dias_atraso_actual=0)
        self.registro['version_modelo'] = 'reglas-demo-v1'
        self.assertEqual(self.client.post(self.url).json()['version_reglas'], 'reglas-demo-v1')

    def test_datos_invalidos_no_llegan_al_modelo(self):
        for campo, valor in [('score_buro_actual', True), ('score_buro_actual', '900'), ('deuda_actual', -1),
                             ('pagos_mensuales_creditos', 20000), ('dias_atraso_actual', 1.5),
                             ('ingresos_mensuales', 0), ('ingresos_mensuales', 1e-323)]:
            with self.subTest(campo=campo, valor=valor):
                registro = copy.deepcopy(self.registro)
                registro['solicitud'][campo] = valor
                with self.assertRaises(HTTPException) as error:
                    motor.datos_del_registro(registro)
                self.assertEqual(error.exception.status_code, 409)
        self.http.post.assert_not_called()

    def test_estado_es_metadato_sin_red_y_sin_llaves(self):
        response = self.client.get('/api/v1/valoracion-ia/estado')
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.json()['configurado'], True)
        self.assertIs(response.json()['conexion_verificada'], False)
        self.assertNotIn('OLLAMA_URL', response.text)
        self.http.post.assert_not_called()

    def test_401_uuid_404_y_base_indisponible_sin_inferencia(self):
        app.dependency_overrides.pop(usuario_actual)
        self.assertEqual(self.client.post(self.url).status_code, 401)
        self.assertEqual(self.client.get('/api/v1/valoracion-ia/estado').status_code, 401)
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa'}
        self.assertEqual(self.client.post('/api/v1/evaluaciones/invalido/valoracion-ia').status_code, 422)
        self.repo.obtener.return_value = None
        self.assertEqual(self.client.post(self.url).status_code, 404)
        app.dependency_overrides[obtener_cache_explicaciones] = lambda: None
        self.assertEqual(self.client.post(self.url).status_code, 503)
        self.http.post.assert_not_called()

    def test_fallos_de_base_y_cache_no_filtran_datos(self):
        self.repo.obtener.side_effect = OperationalError('NO-ENVIAR-BASE')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 503); self.assertNotIn('NO-ENVIAR', response.text)
        self.repo.obtener.side_effect = None
        self.cache.obtener_o_generar.side_effect = OperationalError('NO-ENVIAR-CACHE')
        self.assertEqual(self.client.post(self.url).status_code, 503)
        self.http.post.assert_not_called()

    def test_configuracion_local_estricta_deshabilitada_no_fallback(self):
        for valores in ({'VALORACION_IA_PROVEEDOR': 'deshabilitado'}, {'VALORACION_IA_PROVEEDOR': 'azure'},
                        {'OLLAMA_URL': 'http://evil.example:11434'}, {'OLLAMA_URL': 'http://localhost:11434/api'},
                        {'OLLAMA_MODEL': 'modelo-cloud'}, {'OLLAMA_MODEL': ''}):
            with patch.dict(os.environ, valores):
                self.assertEqual(self.client.post(self.url).status_code, 503)
        self.http.post.assert_not_called()

    def test_contrato_rechaza_texto_libre_probabilidades_y_factores_inventados(self):
        casos = [{**self.salida, 'nivel_riesgo_ia': 'Aprobado'}, {**self.salida, 'probabilidad': .98},
                 {**self.salida, 'factores': ['rfc']}, {**self.salida, 'factores': []},
                 {**self.salida, 'factores': ['atraso_dias', 'atraso_dias']},
                 {**self.salida, 'recomendaciones': ['otorgar_credito']},
                 {**self.salida, 'factores': [True]}, [], None]
        for salida in casos:
            with self.subTest(salida=salida):
                self.respuesta(salida=salida if salida is not None else False)
                response = self.client.post(self.url)
                self.assertEqual(response.status_code, 502)
                self.assertNotIn('nivel_riesgo_ia', response.json())

    def test_revision_humana_es_obligatoria_por_codigo_aunque_ollama_la_omita(self):
        self.respuesta(salida={**self.salida, 'recomendaciones': ['revisar_atrasos']})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nivel_riesgo_ia'], self.salida['nivel_riesgo_ia'])
        self.assertEqual([r['codigo'] for r in response.json()['recomendaciones']], ['revisar_atrasos', 'revision_humana'])

    def test_modelo_incompleto_tool_calls_y_json_no_muestran_exito(self):
        for changes in ({'done': False}, {'model': 'otro:8b'}, {'message': {'role': 'user', 'content': '{}'}},
                        {'message': {'role': 'assistant', 'tool_calls': [{}], 'content': '{}'}},
                        {'message': {'role': 'assistant', 'content': 'NO-ENVIAR-RESPUESTA'}}):
            self.respuesta(**changes)
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 502); self.assertNotIn('NO-ENVIAR', response.text)

    def test_http_timeout_concurrencia_y_cuota_no_simulan_resultados(self):
        for status, esperado in ((404, 503), (500, 502), (302, 502)):
            self.http.post.return_value = httpx.Response(status, text='NO-ENVIAR-SECRETO')
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, esperado); self.assertNotIn('NO-ENVIAR', response.text)
        self.http.post.side_effect = httpx.ReadTimeout('NO-ENVIAR-TIMEOUT')
        self.assertEqual(self.client.post(self.url).status_code, 504)
        slots = Mock(); slots.acquire.return_value = False
        with patch.object(explicaciones, '_slots', slots):
            self.assertEqual(self.client.post(self.url).status_code, 429)
        slots.release.assert_not_called()
        self.cache.obtener_o_generar.side_effect = HTTPException(429, 'Cuota agotada')
        self.assertEqual(self.client.post(self.url).status_code, 429)

    def test_clave_de_cache_separa_modelo_y_datos_no_identidad(self):
        datos = motor.datos_del_registro(self.registro)
        original = motor.clave(datos)
        self.registro['rfc'] = 'OTRA-IDENTIDAD'
        self.assertEqual(original, motor.clave(motor.datos_del_registro(self.registro)))
        self.assertNotEqual(original, motor.clave({**datos, 'deuda_actual': 1}))
        with patch.dict(os.environ, {'OLLAMA_MODEL': 'otro:8b'}):
            self.assertNotEqual(original, motor.clave(datos))


if __name__ == '__main__':
    unittest.main()
