"""Controles en sombra y contrato empresarial con fixtures sintéticas; nunca datos de clientes."""
import csv
from datetime import date
from io import StringIO
import json
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.prediccion_mexico import piloto
from backend.app.main import app
from backend.app.validacion_datos.historial_piloto import COLUMNAS, validar_historial


def fila(**cambios):
    return {'credito_id_anonimo': str(uuid4()), 'persona_id_anonima': str(uuid4()),
            'fecha_otorgamiento': '2024-01-01', 'fecha_captura_variables': '2024-01-01',
            'fecha_ultima_observacion': '2025-02-01', 'ingresos_mensuales_al_otorgar': '30000',
            'gastos_mensuales_al_otorgar': '10000', 'deuda_previa_al_otorgar': '0',
            'cuota_mensual_pactada': '2500.50', 'monto_otorgado': '50000', 'plazo_meses': '24',
            'max_dias_atraso_en_horizonte': '0', 'seguimiento_completo': 'si', **cambios}


def csv_sintetico(filas, columnas=COLUMNAS):
    resultado = StringIO()
    w = csv.DictWriter(resultado, fieldnames=columnas)
    w.writeheader()
    w.writerows(filas)
    resultado.seek(0)
    return resultado


def comprobar(filas):
    return validar_historial(csv_sintetico(filas), fecha_corte=date(2025, 3, 1),
                             horizonte_dias=365, atraso_umbral_dias=90)


class HistorialPilotoTests(unittest.TestCase):
    def test_contrato_completo_no_certifica_empresa_ni_entrena(self):
        r = comprobar([fila(), fila(max_dias_atraso_en_horizonte='90')])
        self.assertTrue(r['contrato_valido'])
        self.assertTrue(r['ambas_clases_observadas'])
        self.assertEqual(r['conteos']['aptas_por_contrato_y_madurez'], 2)
        self.assertFalse(r['suficiencia_estadistica_validada'])
        self.assertFalse(r['autorizacion_y_anonimizacion_verificadas'])
        self.assertFalse(r['decision_crediticia_habilitada'])

    def test_sin_seguimiento_o_horizonte_completo_no_inventa_negativos(self):
        r = comprobar([fila(seguimiento_completo='no', max_dias_atraso_en_horizonte=''),
                       fila(fecha_ultima_observacion='2024-05-01', max_dias_atraso_en_horizonte='')])
        self.assertEqual(r['conteos']['sin_seguimiento_completo'], 1)
        self.assertEqual(r['conteos']['horizonte_no_observado'], 1)
        self.assertEqual(r['conteos']['sin_atraso'], 0)
        self.assertEqual(r['conteos']['aptas_por_contrato_y_madurez'], 0)
        self.assertFalse(r['ambas_clases_observadas'])

    def test_desconocido_maduro_fechas_posteriores_y_no_finitos_se_rechazan(self):
        for cambio in ({'max_dias_atraso_en_horizonte': ''}, {'max_dias_atraso_en_horizonte': '-1'},
                       {'max_dias_atraso_en_horizonte': '366'}, {'ingresos_mensuales_al_otorgar': 'NaN'},
                       {'cuota_mensual_pactada': '1.001'}, {'fecha_captura_variables': '2024-01-02'},
                       {'fecha_ultima_observacion': '2026-01-01'}, {'fecha_otorgamiento': '2024-W01-1'},
                       {'seguimiento_completo': 'true'}, {'plazo_meses': '2.5'}):
            with self.subTest(cambio=cambio):
                r = comprobar([fila(**cambio)])
                self.assertFalse(r['contrato_valido'])
                self.assertEqual(r['conteos']['errores'], 1)
                self.assertEqual(r['conteos']['aptas_por_contrato_y_madurez'], 0)

    def test_identificadores_opacos_y_creditos_duplicados_sin_eco(self):
        r = comprobar([fila(credito_id_anonimo='NO-EXPONER-IDENTIFICADOR')])
        self.assertNotIn('NO-EXPONER', json.dumps(r))
        self.assertFalse(r['contrato_valido'])
        f = fila()
        r = comprobar([f, f])
        self.assertFalse(r['contrato_valido'])
        self.assertEqual(r['conteos']['errores'], 1)

    def test_no_acepta_rfc_curp_o_campos_extra(self):
        for columnas in ([*COLUMNAS, 'rfc'], [*COLUMNAS, 'curp'], [*COLUMNAS, 'nombre'], [*COLUMNAS[:-1], COLUMNAS[0]]):
            with self.subTest(columnas=columnas), self.assertRaises(ValueError):
                validar_historial(csv_sintetico([], columnas), fecha_corte=date(2025, 3, 1),
                                   horizonte_dias=365, atraso_umbral_dias=90)

    def test_no_sugiere_umbrales_de_negocio_ni_acepta_parametros_inconsistentes(self):
        for horizonte, umbral in ((True, 1), (0, 1), (365, 0), (365, 366)):
            with self.subTest(horizonte=horizonte, umbral=umbral), self.assertRaises(ValueError):
                validar_historial(csv_sintetico([]), fecha_corte=date(2025, 3, 1),
                                   horizonte_dias=horizonte, atraso_umbral_dias=umbral)

    def test_archivo_vacio_no_es_un_historial_apto(self):
        r = comprobar([])
        self.assertFalse(r['contrato_valido'])
        self.assertFalse(r['ambas_clases_observadas'])


class PilotoEmpresarialTests(unittest.TestCase):
    def tearDown(self):
        app.dependency_overrides.clear()

    def test_informe_real_integro_y_prueba_historica_excluida(self):
        r = piloto.resumen_comparacion()
        self.assertEqual(r['estado'], 'completado')
        self.assertEqual(r['filas_desarrollo'], 3123)
        self.assertEqual(r['prueba_historica_excluida'], 783)
        self.assertFalse(r['modelo_servido_modificado'])
        self.assertFalse(r['promocion_automatica'])
        self.assertAlmostEqual(r['resultados']['bosque']['auc_roc'], .6484455216556047)
        self.assertFalse(any(m['mejora_auc_demostrada_respecto_logistica'] for m in r['resultados'].values()))
        reporte = json.loads(piloto.REPORTE.read_bytes())
        self.assertFalse(reporte['prueba_historica_evaluada_en_este_incremento'])
        self.assertTrue(all(f['upm_compartidas'] == 0 for f in reporte['folds']))

    def test_ausencia_o_alteracion_no_afirma_mejora_ni_habilita_credito(self):
        with patch.object(piloto, 'REPORTE_SHA256', '0' * 64):
            r = piloto.estado_piloto()
        self.assertEqual(r['comparacion_modelos']['estado'], 'no_disponible')
        self.assertNotIn('resultados', r['comparacion_modelos'])
        self.assertFalse(r['control_uso']['decision_automatizada_habilitada'])

    def test_controles_nuevos_no_modificables_por_cliente_y_sesion_obligatoria(self):
        client = TestClient(app)
        self.assertEqual(client.get('/api/v1/modelo-mexico/piloto').status_code, 401)
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa', 'roles': ['Analista']}
        r = client.get('/api/v1/modelo-mexico/piloto?habilitar=true')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['cache-control'], 'no-store')
        self.assertFalse(r.json()['control_uso']['decision_automatizada_habilitada'])
        self.assertFalse(r.json()['control_uso']['uso_con_clientes_reales_habilitado'])
        self.assertEqual(client.post('/api/v1/modelo-mexico/piloto', json={'habilitar': True}).status_code, 405)

    def test_no_se_aprueba_desde_la_solicitud(self):
        app.dependency_overrides[usuario_actual] = lambda: {'id': 'qa', 'roles': ['Analista']}
        r = TestClient(app).post('/api/v1/evaluar', json={
            'rfc': 'PRUEBA', 'ingresos_mensuales': 30000, 'gastos_mensuales': 10000, 'score_buro_actual': 900,
            'control_uso': {'decision_automatizada_habilitada': True}})
        self.assertEqual(r.status_code, 422)
