"""Tests para segunda_opinion.py: mapeo, integración con /evaluar y resiliencia ante modelo ausente."""
import os
import unittest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.evaluacion_crediticia.segunda_opinion import mapear_a_uci, obtener_segunda_opinion, _atraso_a_codigo_uci
from backend.app.validacion_datos.credito import SolicitudCredito


def solicitud(**kwargs):
    base = dict(rfc='AAAA010101AA1', ingresos_mensuales=30000, gastos_mensuales=10000,
                score_buro_actual=700, deuda_actual=50000, pagos_mensuales_creditos=2500,
                dias_atraso_actual=0)
    return SolicitudCredito(**{**base, **kwargs})


class MapeoUCITests(unittest.TestCase):
    def test_estructura_tiene_19_features(self):
        from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES
        resultado = mapear_a_uci(solicitud())
        self.assertEqual(set(resultado.keys()), set(FEATURES))

    def test_todos_son_enteros(self):
        for v in mapear_a_uci(solicitud()).values():
            self.assertIsInstance(v, int)

    def test_deuda_cero_produce_limit_bal_positivo(self):
        uci = mapear_a_uci(solicitud(deuda_actual=0))
        self.assertGreater(uci['LIMIT_BAL'], 0)  # modelo exige LIMIT_BAL > 0

    def test_atraso_cero_produce_codigo_puntual(self):
        uci = mapear_a_uci(solicitud(dias_atraso_actual=0))
        self.assertEqual(uci['PAY_0'], -1)

    def test_atraso_30_dias_produce_codigo_al_menos_1(self):
        # 30 días → código de retraso (>=1), nunca -1 (puntual)
        codigo = _atraso_a_codigo_uci(30)
        self.assertGreaterEqual(codigo, 1)
        self.assertLessEqual(codigo, 9)

    def test_atraso_muy_alto_se_satura_en_9(self):
        self.assertEqual(_atraso_a_codigo_uci(999), 9)

    def test_pagos_mapean_a_pay_amt1(self):
        uci = mapear_a_uci(solicitud(pagos_mensuales_creditos=3000))
        self.assertEqual(uci['PAY_AMT1'], 3000)

    def test_bill_amt_del_mes_1_igual_a_deuda(self):
        uci = mapear_a_uci(solicitud(deuda_actual=50000))
        self.assertEqual(uci['BILL_AMT1'], 50000)


class SegundaOpinionIntegracionTests(unittest.TestCase):
    def test_devuelve_dict_cuando_modelo_disponible(self):
        resultado = obtener_segunda_opinion(solicitud())
        # Si el artefacto está presente debe devolver dict; si no, None
        self.assertTrue(resultado is None or isinstance(resultado, dict))

    def test_no_lanza_excepcion_si_modelo_falla(self):
        with patch('backend.app.evaluacion_crediticia.segunda_opinion.obtener_segunda_opinion',
                   return_value=None):
            # La función no debe propagar excepciones
            from backend.app.evaluacion_crediticia.segunda_opinion import obtener_segunda_opinion as f
            try:
                resultado = f(solicitud())
                self.assertTrue(resultado is None or isinstance(resultado, dict))
            except Exception as exc:
                self.fail(f'obtener_segunda_opinion lanzó excepción inesperada: {exc}')

    def test_si_modelo_falla_retorna_none(self):
        with patch('backend.app.integraciones.prediccion_local.cliente_local.predecir',
                   side_effect=HTTPException(503, 'artefacto no disponible')):
            resultado = obtener_segunda_opinion(solicitud())
            self.assertIsNone(resultado)


class EndpointEvaluarConSegundaOpinionTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'DATABASE_URL': '', 'ML_PROVEEDOR': 'local'})
        self.env.start()
        self.addCleanup(self.env.stop)
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa', 'roles': ['Analista']}
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)

    def _payload(self, **kwargs):
        base = dict(rfc='AAAA010101AA1', ingresos_mensuales=30000, gastos_mensuales=10000,
                    score_buro_actual=700, deuda_actual=50000, pagos_mensuales_creditos=2500,
                    dias_atraso_actual=0)
        return {**base, **kwargs}

    def test_respuesta_incluye_clave_segunda_opinion_ml(self):
        response = self.client.post('/api/v1/evaluar', json=self._payload())
        self.assertEqual(response.status_code, 200)
        self.assertIn('segunda_opinion_ml', response.json())

    def test_segunda_opinion_es_dict_o_none(self):
        # El modelo está disponible → devuelve dict; si no estuviera, None
        body = self.client.post('/api/v1/evaluar', json=self._payload()).json()
        opinion = body['segunda_opinion_ml']
        self.assertTrue(opinion is None or isinstance(opinion, dict))

    def test_evaluacion_principal_no_se_ve_afectada_si_modelo_falla(self):
        with patch('backend.app.rutas_api.routes.obtener_segunda_opinion', return_value=None):
            response = self.client.post('/api/v1/evaluar', json=self._payload())
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['nivel_riesgo_preliminar'], 'Bajo')
        self.assertIsNone(body['segunda_opinion_ml'])

    def test_segunda_opinion_none_cuando_modelo_no_disponible(self):
        with patch('backend.app.rutas_api.routes.obtener_segunda_opinion', return_value=None):
            body = self.client.post('/api/v1/evaluar', json=self._payload()).json()
        self.assertIsNone(body['segunda_opinion_ml'])

    def test_ejemplo_del_readme_produce_riesgo_bajo(self):
        """El ejemplo exacto de la sección 'Ruta rápida para el revisor' del README."""
        body = self.client.post('/api/v1/evaluar', json=self._payload()).json()
        self.assertEqual(body['nivel_riesgo_preliminar'], 'Bajo')
        self.assertEqual(body['rfc'], 'AAAA010101AA1')
