"""Comparación académica autenticada: no recalcula, persiste ni convierte MXN a UCI."""
import copy
import os
import unittest
from unittest.mock import AsyncMock, Mock, call, patch
from uuid import UUID

from fastapi import HTTPException
from fastapi.testclient import TestClient
from psycopg import OperationalError

from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES
from backend.app.integraciones.prediccion_local import cliente_local
from backend.app.main import app
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio

RUTA_PREDICCION = 'backend.app.rutas_api.segunda_opinion.predecir'


class SegundaOpinionTests(unittest.TestCase):
    def setUp(self):
        self.entorno = patch.dict(os.environ, {'ML_PROVEEDOR': 'local', 'DATABASE_URL': ''})
        self.entorno.start()
        self.addCleanup(self.entorno.stop)
        self.addCleanup(app.dependency_overrides.clear)
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa', 'roles': ['Analista']}
        self.repositorio = Mock()
        self.identificador = UUID('00000000-0000-4000-8000-000000000123')
        self.registro = {
            'id': str(self.identificador), 'rfc': 'NO-ENVIAR-RFC',
            'nivel_riesgo_preliminar': 'Bajo', 'version_modelo': 'reglas-demo-v2',
            'solicitud': {'ingresos_mensuales': 30000, 'gastos_mensuales': 10000},
        }
        self.repositorio.obtener.return_value = self.registro
        app.dependency_overrides[obtener_repositorio] = lambda: self.repositorio
        self.valores = {nombre: 0 for nombre in FEATURES}
        self.valores['LIMIT_BAL'] = 200000
        self.valores.update({nombre: 3000 for nombre in FEATURES if nombre.startswith('PAY_AMT')})
        self.client = TestClient(app)

    def enviar(self, valores=None, identificador=None, **otros):
        return self.client.post(
            f'/api/v1/evaluaciones/{identificador or self.identificador}/segunda-opinion',
            json={'valores': self.valores if valores is None else valores, **otros},
        )

    def test_compara_reglas_guardadas_y_modelo_real_sin_red_ni_escrituras(self):
        original = copy.deepcopy(self.registro)
        with patch('httpx.AsyncClient') as red, patch('pickle.load') as pickle:
            response = self.enviar()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        result = response.json()
        self.assertEqual(set(result), {'evaluacion_id', 'riesgo_por_reglas', 'version_reglas',
                                      'modelo', 'guardada', 'advertencia'})
        self.assertEqual(result['evaluacion_id'], str(self.identificador))
        self.assertEqual(result['riesgo_por_reglas'], 'Bajo')
        self.assertEqual(result['version_reglas'], 'reglas-demo-v2')
        self.assertIs(result['guardada'], False)
        self.assertEqual(result['modelo']['proveedor'], 'local')
        self.assertEqual(result['modelo']['modelo_configurado'], cliente_local.MODELO_ID)
        self.assertIs(type(result['modelo']['incumplimiento_predicho']), bool)
        self.assertNotIn('probabilidad', result['modelo'])
        self.assertIn('NTD', result['advertencia'])
        self.assertIn('no se guardan', result['advertencia'])
        self.assertNotIn('NO-ENVIAR-RFC', response.text)
        self.repositorio.obtener.assert_called_once_with(self.identificador)
        self.assertEqual(self.repositorio.mock_calls, [call.obtener(self.identificador)])
        self.assertEqual(self.registro, original)
        red.assert_not_called()
        pickle.assert_not_called()

    def test_conserva_resultado_historico_v1_sin_recalcularlo(self):
        # El score actual no interviene: la respuesta reproduce exclusivamente el resultado guardado.
        self.registro.update(nivel_riesgo_preliminar='Medio', version_modelo='reglas-demo-v1')
        with patch('backend.app.evaluacion_crediticia.scoring.evaluar_credito') as reglas:
            response = self.enviar()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['riesgo_por_reglas'], 'Medio')
        self.assertEqual(response.json()['version_reglas'], 'reglas-demo-v1')
        reglas.assert_not_called()

    def test_reutiliza_19_campos_uci_estrictos_y_no_admite_campos_de_identidad(self):
        incompleto = dict(self.valores)
        incompleto.pop('PAY_AMT6')
        casos = [incompleto, {}, {**self.valores, 'RFC': 123}, {**self.valores, 'SEX': 1}]
        for campo, valor in (('LIMIT_BAL', 0), ('PAY_AMT1', -1), ('PAY_0', -3), ('PAY_6', 10),
                             ('BILL_AMT1', True), ('BILL_AMT1', '1'), ('BILL_AMT1', 1.5),
                             ('BILL_AMT1', 2147483648)):
            casos.append({**self.valores, campo: valor})
        with patch(RUTA_PREDICCION, new_callable=AsyncMock) as modelo:
            for valores in casos:
                with self.subTest(valores=valores):
                    self.assertEqual(self.enviar(valores).status_code, 422)
            self.assertEqual(self.enviar(rfc='NO-ENVIAR-RFC').status_code, 422)
            modelo.assert_not_called()
        self.repositorio.obtener.assert_not_called()

    def test_no_invoca_modelo_para_uuid_invalido_o_evaluacion_ausente(self):
        with patch(RUTA_PREDICCION, new_callable=AsyncMock) as modelo:
            self.assertEqual(self.enviar(identificador='no-es-uuid').status_code, 422)
            self.repositorio.obtener.assert_not_called()
            self.repositorio.obtener.return_value = None
            self.assertEqual(self.enviar().status_code, 404)
            modelo.assert_not_called()

    def test_base_no_configurada_o_inaccesible_no_invoca_modelo(self):
        with patch(RUTA_PREDICCION, new_callable=AsyncMock) as modelo:
            app.dependency_overrides[obtener_repositorio] = lambda: None
            self.assertEqual(self.enviar().status_code, 503)
            app.dependency_overrides[obtener_repositorio] = lambda: self.repositorio
            self.repositorio.obtener.side_effect = OperationalError('NO-ENVIAR-CONEXION')
            response = self.enviar()
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('NO-ENVIAR-CONEXION', response.text)
            modelo.assert_not_called()

    def test_requiere_autenticacion(self):
        app.dependency_overrides.pop(usuario_actual)
        with patch(RUTA_PREDICCION, new_callable=AsyncMock) as modelo:
            self.assertEqual(self.enviar().status_code, 401)
            modelo.assert_not_called()
            self.repositorio.obtener.assert_not_called()

    def test_errores_del_proveedor_no_se_convierten_en_prediccion(self):
        for codigo in (502, 503, 504):
            with self.subTest(codigo=codigo), patch(RUTA_PREDICCION, new_callable=AsyncMock) as modelo:
                modelo.side_effect = HTTPException(codigo, 'Proveedor no disponible.')
                response = self.enviar()
                self.assertEqual(response.status_code, codigo)
                self.assertNotIn('modelo', response.json())

    def test_azure_explicito_preserva_contrato_y_no_envia_datos_del_solicitante(self):
        prediccion = {'incumplimiento_predicho': True, 'origen': 'Azure Machine Learning',
                      'modelo_configurado': 'modelo-academico-test', 'modo': 'academico',
                      'advertencia': 'Clasificación académica, no probabilidad ni autorización de crédito.'}
        with patch.dict(os.environ, {'ML_PROVEEDOR': 'azure'}), patch(
                'backend.app.integraciones.prediccion_azure_ml.cliente_ml.predecir',
                new_callable=AsyncMock, return_value=prediccion) as azure:
            response = self.enviar()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['modelo'], {**prediccion, 'proveedor': 'azure'})
        azure.assert_awaited_once_with(self.valores)
        self.assertNotIn('NO-ENVIAR-RFC', str(azure.call_args))

    def test_proveedor_deshabilitado_no_simula_segunda_opinion(self):
        with patch.dict(os.environ, {'ML_PROVEEDOR': 'deshabilitado'}):
            response = self.enviar()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('modelo', response.json())


if __name__ == '__main__':
    unittest.main()
