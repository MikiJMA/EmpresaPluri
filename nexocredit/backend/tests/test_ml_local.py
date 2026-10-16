"""ML local real sobre artefacto auditado; sin red, secretos, pickle ni base de trabajo."""
import asyncio
import copy
import hashlib
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones import proveedores
from backend.app.integraciones.prediccion_local import cliente_local as ml
from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES


class MLLocalTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'ML_PROVEEDOR': 'local', 'DATABASE_URL': '',
                                          'AZURE_ML_API_KEY': 'NO-ENVIAR-CLAVE'})
        self.env.start()
        self.addCleanup(self.env.stop)
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa', 'roles': ['Analista']}
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)
        self.valores = {n: 0 for n in FEATURES}
        self.valores['LIMIT_BAL'] = 200000
        self.valores.update({n: 3000 for n in FEATURES if n.startswith('PAY_AMT')})

    def enviar(self, valores=None, prefijo='/api/v1/ml'):
        return self.client.post(prefijo + '/predecir', json={'valores': self.valores if valores is None else valores})

    def test_artefacto_real_huella_vectores_y_metricas(self):
        modelo = ml.cargar_modelo()
        self.assertEqual(hashlib.sha256(ml.ARCHIVO.read_bytes()).hexdigest(), ml.MODELO_SHA256)
        self.assertEqual(modelo['columnas'], FEATURES)
        self.assertEqual(modelo['metricas']['prueba']['matriz_confusion'], [[3418, 1278], [492, 767]])
        self.assertEqual(modelo['modelo_id'], ml.MODELO_ID)

    def test_predicciones_locales_no_consultan_red_no_cargan_objetos_ni_guardan(self):
        from backend.app.persistencia_postgresql import conexion
        with patch('httpx.AsyncClient') as red, patch('httpx.Client') as sync, \
                patch('pickle.load') as pickle, patch('joblib.load') as joblib, patch.object(conexion, 'conectar') as db:
            salida = asyncio.run(proveedores.predecir(self.valores))
        for metodo in (red, sync, pickle, joblib, db):
            metodo.assert_not_called()
        self.assertIs(type(salida['incumplimiento_predicho']), bool)
        self.assertEqual(salida['proveedor'], 'local')
        self.assertEqual(salida['modelo_sha256'], ml.MODELO_SHA256)
        self.assertNotIn('probabilidad', salida)
        self.assertNotIn('NO-ENVIAR', str(salida))

    def test_dos_clases_son_predicciones_no_plantilla(self):
        tarde = {**self.valores, **{n: 3 for n in FEATURES if n.startswith('PAY_') and not n.startswith('PAY_AMT')}}
        self.assertFalse(ml.predecir(self.valores)['incumplimiento_predicho'])
        self.assertTrue(ml.predecir(tarde)['incumplimiento_predicho'])

    def test_api_nueva_y_alias_heredado_mismo_modelo(self):
        nuevo = self.enviar()
        heredado = self.enviar(prefijo='/api/v1/azure-ml')
        self.assertEqual(nuevo.status_code, 200)
        self.assertEqual(nuevo.json(), heredado.json())
        self.assertEqual(nuevo.json()['origen'], 'scikit-learn local')

    def test_estados_no_afirman_consulta_ni_filtran_datos(self):
        estado = self.client.get('/api/v1/ml/estado').json()
        self.assertTrue(estado['configurado'])
        self.assertFalse(estado['conexion_verificada'])
        self.assertNotIn('NO-ENVIAR', str(estado))
        self.assertEqual(estado, proveedores.estado_ml())

    def test_proteccion_tambien_en_endpoint_local(self):
        app.dependency_overrides.clear()
        self.assertEqual(self.client.get('/api/v1/ml/estado').status_code, 401)
        self.assertEqual(self.enviar().status_code, 401)
        self.assertEqual(self.enviar(prefijo='/api/v1/azure-ml').status_code, 401)

    def test_no_admite_rfc_demografia_faltantes_ni_bool(self):
        for cambios in ({'RFC': 1}, {'SEX': 1}, {'LIMIT_BAL': 0}, {'PAY_0': 10},
                        {'PAY_AMT1': -1}, {'BILL_AMT1': True}, {'BILL_AMT1': 1.5},
                        {'BILL_AMT1': '1'}, {'BILL_AMT1': 2147483648}):
            self.assertEqual(self.enviar({**self.valores, **cambios}).status_code, 422)
        self.assertEqual(self.enviar({}).status_code, 422)
        self.assertEqual(self.client.post('/api/v1/ml/predecir', json={'valores': self.valores, 'modelo': 'otro'}).status_code, 422)

    def test_fuera_rango_de_entrenamiento_se_advierte_sin_score(self):
        result = self.enviar({**self.valores, 'LIMIT_BAL': 2147483647}).json()
        self.assertIn('LIMIT_BAL', result['variables_fuera_rango_entrenamiento'])
        self.assertNotIn('nivel_riesgo_preliminar', result)
        self.assertNotIn('score', result)

    def test_artefacto_inexistente_o_alterado_falla_cerrado_sin_fallback(self):
        with TemporaryDirectory() as directory:
            archivo = Path(directory) / 'modelo.json'
            with patch.object(ml, 'ARCHIVO', archivo), patch('httpx.AsyncClient') as red:
                self.assertEqual(self.enviar().status_code, 503)
                archivo.write_text('{"texto":"NO-ENVIAR-SECRETO"}', encoding='utf8')
                response = self.enviar()
                self.assertEqual(response.status_code, 503)
                self.assertNotIn('NO-ENVIAR', response.text)
                self.assertFalse(self.client.get('/api/v1/ml/estado').json()['configurado'])
                red.assert_not_called()

    def test_modelo_numerico_incompleto_no_finito_y_metrica_contradictoria(self):
        for cambiar in (lambda m: m.update(columnas=list(reversed(FEATURES))),
                        lambda m: m.update(escala=[0] * 19),
                        lambda m: m.update(coeficientes=[float('nan')] * 19),
                        lambda m: m.update(intercepto=True),
                        lambda m: m.update(media=[]),
                        lambda m: m.update(rangos_entrenamiento=[[0, True]] * 19),
                        lambda m: m.update(rangos_entrenamiento=[[1, 0]] * 19),
                        lambda m: m.update(rangos_entrenamiento=[[0, 1]] * 18),
                        lambda m: m['metricas']['prueba'].update(exactitud=1),
                        lambda m: m['metricas']['prueba'].update(matriz_confusion=[[True, 1278], [492, 767]]),
                        lambda m: m['metricas']['prueba'].update(matriz_confusion=[[3418, 1278], [492]]),
                        lambda m: m['metricas']['prueba'].update(matriz_confusion=[[0, 0], [0, 0]])):
            modelo = copy.deepcopy(ml.cargar_modelo())
            cambiar(modelo)
            with self.assertRaises(ValueError):
                ml.validar_modelo(modelo)

    def test_desactivado_sigue_disponible_y_azure_no_cambia(self):
        with patch.dict(os.environ, {'ML_PROVEEDOR': 'deshabilitado'}):
            self.assertFalse(proveedores.estado_ml()['configurado'])
            self.assertEqual(self.enviar().status_code, 503)
        with patch.dict(os.environ, {'ML_PROVEEDOR': 'azure', 'AZURE_ML_SCORING_URI': '', 'AZURE_ML_API_KEY': ''}):
            self.assertEqual(self.enviar().status_code, 503)
            self.assertEqual(proveedores.estado_ml()['origen'], 'Azure Machine Learning')
