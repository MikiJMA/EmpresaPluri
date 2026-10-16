"""Modelo ENIF real y contrato principal, sin tocar la instalación de desarrollo."""
import copy
import os
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.prediccion_mexico import cliente
from backend.app.main import app
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.validacion_datos.perfil_enif import PerfilENIF, vectorizar, COLUMNAS

PERFIL = {'ingreso_laboral': 12000, 'periodicidad': 3, 'ingreso_variable': 1, 'presupuesto': 1,
          'gastos_cubiertos': 1, 'ahorro_emergencia': 4, 'creditos': ['bancaria']}
SOLICITUD = {'rfc': 'ENIF-DEMO', 'ingresos_mensuales': 30000, 'gastos_mensuales': 10000,
             'score_buro_actual': 900, 'deuda_actual': 0, 'pagos_mensuales_creditos': 0, 'dias_atraso_actual': 0}


class ModeloMexicoTests(unittest.TestCase):
    def setUp(self):
        self.entorno = patch.dict(os.environ, {'DATABASE_URL': ''})
        self.entorno.start()
        self.addCleanup(self.entorno.stop)
        self.addCleanup(app.dependency_overrides.clear)
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa', 'roles': ['Analista']}
        self.client = TestClient(app)

    def test_modelo_numerico_real_sin_red_reglas_ni_pickle(self):
        with patch('httpx.AsyncClient') as red, patch('pickle.load') as pickle:
            r = cliente.evaluar_perfil(PERFIL)
        self.assertEqual(r['pais'], 'México')
        self.assertIs(r['reglas_score_utilizadas'], False)
        self.assertIsNone(r['probabilidad_impago_futuro'])
        self.assertEqual(r['modelo_sha256'], cliente.MODELO_SHA256)
        self.assertTrue(0 <= r['estimacion_asociativa'] <= 1)
        self.assertAlmostEqual(r['metricas_prueba']['auc_roc'], .6054963570127504)
        self.assertEqual(r['metricas_prueba']['filas'], 783)
        red.assert_not_called()
        pickle.assert_not_called()

    def test_transformacion_no_confunde_ausencia_o_respuestas_con_datos(self):
        self.assertEqual(len(vectorizar(PERFIL)), len(COLUMNAS))
        for cambios in ({'ingreso_laboral': 0}, {'ingreso_laboral': 99888}, {'periodicidad': 0},
                        {'ahorro_emergencia': 9}, {'ingreso_variable': True}, {'creditos': []},
                        {'creditos': ['bancaria', 'bancaria']}, {'creditos': ['buro']}, {'edad': 30},
                        {'P6_3_1': 1}, {'ingreso_laboral': float('nan')}):
            with self.subTest(cambios=cambios), self.assertRaises(ValidationError):
                PerfilENIF.model_validate({**PERFIL, **cambios})

    def test_perfiles_sinteticos_distintos_ejercitan_ambas_clases_reales(self):
        base = cliente.evaluar_perfil(PERFIL)
        distinto = cliente.evaluar_perfil({**PERFIL, 'ingreso_laboral': 4000, 'ingreso_variable': 2,
                                          'presupuesto': 2, 'gastos_cubiertos': 2, 'ahorro_emergencia': 1,
                                          'creditos': ['departamental', 'personal']})
        self.assertAlmostEqual(base['estimacion_asociativa'], .111645)
        self.assertAlmostEqual(distinto['estimacion_asociativa'], .428736)
        self.assertFalse(base['atraso_reportado_estimado'])
        self.assertTrue(distinto['atraso_reportado_estimado'])
        self.assertIsNone(distinto['probabilidad_impago_futuro'])

    def test_artefacto_alterado_falla_cerrado(self):
        with patch.object(cliente, 'MODELO_SHA256', '0' * 64), self.assertRaises(HTTPException) as error:
            cliente.evaluar_perfil(PERFIL)
        self.assertEqual(error.exception.status_code, 503)

    def test_evaluacion_principal_incluye_modelo_y_conserva_comparacion(self):
        body = {**SOLICITUD, 'perfil_enif': PERFIL}
        original = copy.deepcopy(body)
        r = self.client.post('/api/v1/evaluar', json=body)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIn('analisis_mexico', r.json())
        self.assertEqual(r.json()['version_modelo'], 'reglas-demo-v2')
        self.assertEqual(r.json()['nivel_riesgo_preliminar'], 'Bajo')
        self.assertEqual(body, original)
        self.assertFalse(r.json()['guardado'])

    def test_score_no_interviene_en_modelo_mexicano(self):
        resultados = []
        for score in (0, 600, 1000):
            r = self.client.post('/api/v1/evaluar', json={**SOLICITUD, 'score_buro_actual': score, 'perfil_enif': PERFIL})
            self.assertEqual(r.status_code, 200)
            resultados.append(r.json()['analisis_mexico'])
        self.assertEqual(resultados[0], resultados[1])
        self.assertEqual(resultados[1], resultados[2])

    def test_conserva_api_legacy_sin_inventar_perfil(self):
        r = self.client.post('/api/v1/evaluar', json=SOLICITUD)
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('analisis_mexico', r.json())

    def test_modelo_fallido_no_guarda_solo_reglas_silenciosamente(self):
        repo = Mock()
        app.dependency_overrides[obtener_repositorio] = lambda: repo
        with patch.object(cliente, 'MODELO_SHA256', '0' * 64):
            r = self.client.post('/api/v1/evaluar', json={**SOLICITUD, 'perfil_enif': PERFIL})
        self.assertEqual(r.status_code, 503)
        repo.guardar.assert_not_called()

    def test_guardar_incluye_perfil_resultado_y_version(self):
        repo = Mock()
        repo.guardar.side_effect = lambda _id, _solicitud, resultado: {**resultado, 'guardado': True}
        app.dependency_overrides[obtener_repositorio] = lambda: repo
        r = self.client.post('/api/v1/evaluar', json={**SOLICITUD, 'perfil_enif': PERFIL})
        self.assertEqual(r.status_code, 200)
        _, guardada, resultado = repo.guardar.call_args.args
        self.assertEqual(guardada['perfil_enif']['creditos'], ['bancaria'])
        self.assertEqual(resultado['analisis_mexico']['modelo_id'], cliente.MODELO_ID)

    def test_perfil_invalido_no_filtra_datos_en_422(self):
        r = self.client.post('/api/v1/evaluar', json={**SOLICITUD, 'perfil_enif': {**PERFIL, 'nombre': 'NO-MOSTRAR'}})
        self.assertEqual(r.status_code, 422)
        self.assertNotIn('NO-MOSTRAR', r.text)

    def test_metadatos_exigen_autenticacion(self):
        self.assertEqual(self.client.get('/api/v1/modelo-mexico').status_code, 200)
        app.dependency_overrides.pop(usuario_actual)
        self.assertEqual(self.client.get('/api/v1/modelo-mexico').status_code, 401)


class PreparacionENIFTests(unittest.TestCase):
    def test_target_real_no_convierte_saltos_o_desconocidos_en_negativos(self):
        import pandas as pd
        from backend.app.integraciones.prediccion_mexico.datos import preparar
        row = {'P3_11A': '12000', 'P3_11B': '3', 'P3_12': '1', 'P4_1': '1', 'P4_3': '1', 'P4_10': '4', 'UPM_DIS': 'QA'}
        row.update({f'P6_2_{i}': '2' for i in range(1, 10)})
        row.update({f'P6_3_{i}': '' for i in range(1, 10)})
        fila = {**row, 'P6_2_2': '1', 'P6_3_2': '2'}
        datos = pd.DataFrame([row, fila, {**fila, 'P6_3_2': '1'}, {**fila, 'P6_3_2': '9'},
                              {**fila, 'P3_11A': '99888'}, {**fila, 'P6_3_2': ''}])
        x, y, _, descartes = preparar(datos)
        self.assertEqual(y.tolist(), [0, 1])
        self.assertEqual(x.shape[0], 2)
        self.assertEqual(descartes, {'sin_credito': 1, 'atraso_desconocido': 2, 'perfil_incompleto': 1})
        self.assertNotIn('P6_3_2', COLUMNAS)
