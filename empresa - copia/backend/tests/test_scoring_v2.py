"""Reglas ilustrativas nuevas, monotonicidad y guía exacta; sin red ni base de trabajo."""
import os
import json
import unittest
from unittest.mock import patch
import httpx

from fastapi import HTTPException

from backend.app.evaluacion_crediticia.scoring import evaluar_credito
from backend.app.validacion_datos.credito import SolicitudCredito
from backend.app.integraciones.proveedores_locales import documentos, explicaciones
from backend.app.integraciones.cache_explicaciones import clave_explicacion


def evaluar(score, margen):
    return evaluar_credito(SolicitudCredito(rfc='DEMO-V2', ingresos_mensuales=30000,
                                           gastos_mensuales=30000 - margen, score_buro_actual=score))


class ScoringV2Tests(unittest.TestCase):
    def test_tres_rangos_y_cortes_inclusivos(self):
        for score, esperado in ((0, 'Alto'), (200, 'Alto'), (499, 'Alto'), (500, 'Medio'),
                                (679, 'Medio'), (680, 'Bajo'), (900, 'Bajo'), (1000, 'Bajo')):
            with self.subTest(score=score):
                result = evaluar(score, 20000)
                self.assertEqual(result['nivel_riesgo_preliminar'], esperado)
                self.assertEqual(result['version_modelo'], 'reglas-demo-v2')

    def test_nueve_combinaciones_y_margen_nunca_mejora_score(self):
        for score, esperados in ((200, ['Alto', 'Alto', 'Alto']),
                                (600, ['Alto', 'Medio', 'Medio']), (900, ['Alto', 'Medio', 'Bajo'])):
            for margen, esperado in zip((7000, 15000, 20000), esperados):
                self.assertEqual(evaluar(score, margen)['nivel_riesgo_preliminar'], esperado)

    def test_centavos_deciden_cortes_antes_del_formato_visual(self):
        for margen, esperado in ((-100, 'Alto'), (0, 'Alto'), (7000, 'Alto'),
                                 (7000.004, 'Alto'), (7000.006, 'Medio'), (7000.01, 'Medio'),
                                 (15000, 'Medio'), (15000.004, 'Medio'), (15000.006, 'Bajo'), (15000.01, 'Bajo')):
            with self.subTest(margen=margen):
                self.assertEqual(evaluar(900, margen)['nivel_riesgo_preliminar'], esperado)

    def test_subir_score_no_empeora_riesgo_en_todos_los_puntajes(self):
        nivel = {'Bajo': 0, 'Medio': 1, 'Alto': 2}
        for margen in (-100, 0, 7000, 7000.01, 15000, 15000.01, 20000):
            valores = [nivel[evaluar(score, margen)['nivel_riesgo_preliminar']] for score in range(1001)]
            self.assertTrue(all(a >= b for a, b in zip(valores, valores[1:])))

    def test_plantilla_y_guias_conservan_version_original(self):
        for version, riesgo, fuente in (('reglas-demo-v1', 'Medio', 'guia-demostracion-v1'),
                                        ('reglas-demo-v2', 'Alto', 'guia-demostracion-v2')):
            registro = {'version_modelo': version, 'margen_libre': 20000, 'nivel_riesgo_preliminar': riesgo,
                        'solicitud': {'ingresos_mensuales': 30000, 'gastos_mensuales': 10000,
                                      'score_buro_actual': 200, 'rfc': 'NO-ENVIAR'}}
            response = explicaciones.explicar_local(registro, documentos.buscar)
            self.assertEqual(response['fuentes'][0]['fuente'], fuente)
            self.assertIn('Riesgo preliminar ' + riesgo, response['explicacion'])
            self.assertNotIn('NO-ENVIAR', str(response))
            self.assertIn('0–499 Alto' if version.endswith('v2') else 'margen > 15,000', response['explicacion'])

    def test_falta_guia_v2_no_usa_v1_y_cache_separa_version(self):
        v1 = explicaciones.guia_reglas(documentos.buscar)
        with self.assertRaises(HTTPException) as error:
            explicaciones.guia_reglas(lambda _: {'resultados': [v1]}, 'reglas-demo-v2')
        self.assertEqual(error.exception.status_code, 503)
        with patch.dict(os.environ, {'EXPLICACIONES_PROVEEDOR': 'local', 'DOCUMENTOS_PROVEEDOR': 'local'}):
            self.assertNotEqual(clave_explicacion({'version_modelo': 'reglas-demo-v1'}),
                                clave_explicacion({'version_modelo': 'reglas-demo-v2'}))

    def test_ollama_v2_recibe_guia_correcta_y_solo_datos_permitidos(self):
        registro = {**evaluar(200, 20000), 'solicitud': {'ingresos_mensuales': 30000, 'gastos_mensuales': 10000,
                    'score_buro_actual': 200, 'rfc': 'NO-ENVIAR', 'observaciones': 'NO-ENVIAR'}}
        doc = explicaciones.guia_reglas(documentos.buscar, 'reglas-demo-v2')
        with patch.dict(os.environ, {'OLLAMA_URL': 'http://127.0.0.1:11434', 'OLLAMA_MODEL': 'modelo-ficticio:8b'}), \
                patch('httpx.Client') as cliente:
            http = cliente.return_value.__enter__.return_value
            http.post.return_value = httpx.Response(200, json={'done': True, 'model': 'modelo-ficticio:8b',
                'message': {'role': 'assistant', 'content': json.dumps({'explicacion': 'Ejemplo QA sin decisión real.', 'fuentes': [doc['id']]})}})
            respuesta = explicaciones.explicar_ollama(registro, documentos.buscar)
            payload = http.post.call_args.kwargs['json']
        datos = json.loads(payload['messages'][1]['content'])
        self.assertEqual(datos['escenario']['version_modelo'], 'reglas-demo-v2')
        self.assertEqual(datos['documento']['id'], doc['id'])
        self.assertNotIn('NO-ENVIAR', str(payload))
        self.assertEqual(respuesta['fuentes'][0]['version'], '2.0')
