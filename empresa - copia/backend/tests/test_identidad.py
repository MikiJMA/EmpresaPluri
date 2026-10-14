import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.validacion_datos.identidad import revisar_identidad

RFC = 'AACD900101A01'  # Ficticio: no corresponde a una persona consultada.
CURP = 'AACD900101HDFBCD01'  # Máscara sintética; no CURP certificada.


class IdentidadTests(unittest.TestCase):
    def tearDown(self):
        app.dependency_overrides.clear()

    def test_formato_y_fecha_no_equivalen_a_identidad_oficial(self):
        result = revisar_identidad(RFC.lower(), CURP.lower())
        self.assertEqual(result['estado'], 'coherencia_basica')
        self.assertFalse(result['verificacion_oficial'])
        self.assertIn('no confirma', result['mensaje'])
        self.assertNotIn(RFC, str(result))
        self.assertNotIn(CURP, str(result))

    def test_fecha_diferente_y_datos_invalidos(self):
        self.assertEqual(revisar_identidad(RFC, CURP.replace('900101', '910101'))['estado'], 'no_coincide')
        for rfc, curp in [('texto', CURP), ('ABCD900231A01', CURP), (RFC, 'corta'), (RFC, CURP.replace('900101', '900231'))]:
            self.assertEqual(revisar_identidad(rfc, curp)['estado'], 'formato_invalido')
        self.assertEqual(revisar_identidad(RFC)['estado'], 'formato_correcto')

    def test_no_calcula_homoclave_por_iniciales_y_rfc_generico_no_identifica(self):
        result = revisar_identidad(RFC, CURP.replace('AACD', 'ZAXX'))
        self.assertEqual(result['estado'], 'coherencia_basica')
        self.assertFalse(result['verificacion_oficial'])
        self.assertIn('RFC genérico', revisar_identidad('XAXX010101000')['mensaje'])

    def test_ruta_autenticada_y_sin_red_o_persistencia(self):
        client = TestClient(app)
        self.assertEqual(client.post('/api/v1/identidad/revisar', json={'rfc': RFC, 'curp': CURP}).status_code, 401)
        app.dependency_overrides[usuario_actual] = lambda: {'nombre': 'Prueba', 'roles': ['Analista']}
        with patch('backend.app.persistencia_postgresql.conexion.conectar', side_effect=AssertionError('Sin persistencia')) as db, \
                patch('backend.app.integraciones.datos_financieros.proveedores._leer_json', side_effect=AssertionError('Sin proveedor')) as red:
            response = client.post('/api/v1/identidad/revisar', json={'rfc': RFC, 'curp': CURP})
            db.assert_not_called()
            red.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertFalse(response.json()['verificacion_oficial'])

    def test_errores_no_reflejan_rfc_curp(self):
        app.dependency_overrides[usuario_actual] = lambda: {'roles': ['Analista']}
        client = TestClient(app)
        for data in [{'rfc': RFC, 'curp': {'privado': CURP}}, {'rfc': RFC, 'curp': CURP, 'nombre': 'No enviar'}, {'rfc': 'A'*65, 'curp': CURP}]:
            response = client.post('/api/v1/identidad/revisar', json=data)
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(RFC, response.text)
            self.assertNotIn(CURP, response.text)
