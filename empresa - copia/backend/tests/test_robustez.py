"""Regresiones de las pruebas de ruptura: nunca usan DB ni identidades reales."""
import json
import os
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from fastapi.testclient import TestClient
from starlette.requests import Request
from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.autenticacion_local.origen import origen_cliente
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio

BASE = dict(rfc='AACD900101A01', ingresos_mensuales=30000, gastos_mensuales=10000, score_buro_actual=700)


class RobustezTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[usuario_actual] = lambda: {'roles': ['Analista']}
        app.dependency_overrides[obtener_repositorio] = lambda: None
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)

    def test_no_finitos_rechazados_sin_500_ni_eco(self):
        for field in ('ingresos_mensuales', 'gastos_mensuales', 'deuda_actual', 'pagos_mensuales_creditos'):
            for value in ('NaN', 'Infinity', '-Infinity', '1e309'):
                raw = json.dumps({**BASE, field: 123}).replace(f'"{field}": 123', f'"{field}": {value}')
                response = self.client.post('/api/v1/evaluar', content=raw, headers={'Content-Type': 'application/json'})
                self.assertEqual(response.status_code, 422, (field, value))
                self.assertNotIn('AACD900101A01', response.text)
                self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_importes_solo_numeros_json_no_booleanos_ni_cadenas(self):
        for field in ('ingresos_mensuales', 'gastos_mensuales', 'deuda_actual', 'pagos_mensuales_creditos'):
            for value in (True, False, '123', {}, []):
                self.assertEqual(self.client.post('/api/v1/evaluar', json={**BASE, field: value}).status_code, 422)
        for value in (1, 1.5):
            self.assertEqual(self.client.post('/api/v1/evaluar', json={**BASE, 'ingresos_mensuales': value}).status_code, 200)

    def test_identificador_blanco_excesivo_control_y_unicode(self):
        for value in ('', ' '*3, '\n', 'AB\0CD', '\ud800', '\u200b', 'A'*121, 'A'*8192):
            response = self.client.post('/api/v1/evaluar', content=json.dumps({**BASE, 'rfc':value}), headers={'Content-Type':'application/json'})
            self.assertEqual(response.status_code, 422)
        for value in ('cliente de prueba #1', 'áé / ejemplo', 'A'*120):
            response = self.client.post('/api/v1/evaluar', json={**BASE, 'rfc':value})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['rfc'], value)

    def test_paginacion_acotada_antes_de_consultar_postgres(self):
        for offset in ('-1', '1000001', '9223372036854775808', '9'*100):
            self.assertEqual(self.client.get('/api/v1/evaluaciones?offset='+offset).status_code, 422)
        self.assertEqual(self.client.get('/api/v1/evaluaciones?offset=1000000').status_code, 503)

    def test_cuerpo_profundo_invalido_no_refleja_input(self):
        response = self.client.post('/api/v1/evaluar', content='['*700+'0'+']'*700, headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 422)
        self.assertLess(len(response.text), 300)

    def test_observaciones_invalidas_se_rechazan_antes_de_postgres(self):
        repo = Mock()
        app.dependency_overrides[obtener_repositorio] = lambda: repo
        app.dependency_overrides[usuario_actual] = lambda: {'roles':['Analista'], 'responsable':'Analista fixture'}
        url = f'/api/v1/evaluaciones/{uuid4()}/revisiones'
        payload = dict(id=str(uuid4()), version_anterior=0, estado='Pendiente', responsable='Fixture')
        for value in ('Motivo\0ficticio', '\u200b', '\x7f', '\t\n', '\u202eTexto', '\ud800'):
            with self.subTest(value=repr(value)):
                response = self.client.post(url, content=json.dumps({**payload, 'observaciones':value}), headers={'Content-Type':'application/json'})
                self.assertEqual(response.status_code, 422)
                self.assertNotIn('ficticio', response.text)
        repo.revisar.assert_not_called()
        repo.revisar.return_value = {'guardada':True}
        for value in ('Revisión válida: áé, 中文 y 👍', 'Línea uno\nLínea dos\tOK'):
            self.assertEqual(self.client.post(url, json={**payload, 'observaciones':value}).status_code, 200)
            self.assertEqual(repo.revisar.call_args.args[1].responsable, 'Analista fixture')

    def test_incoherencia_financiera_no_llega_al_guardado(self):
        repo = Mock()
        app.dependency_overrides[obtener_repositorio] = lambda: repo
        for changes in ({'gastos_mensuales':100, 'pagos_mensuales_creditos':2000},
                        {'deuda_actual':0, 'pagos_mensuales_creditos':2500, 'dias_atraso_actual':30},
                        {'deuda_actual':0, 'dias_atraso_actual':1}):
            response = self.client.post('/api/v1/evaluar', json={**BASE, **changes})
            self.assertEqual(response.status_code, 422)
        repo.guardar.assert_not_called()

    def test_captura_coherente_y_api_antigua_siguen_funcionando(self):
        for changes in ({}, {'deuda_actual':None, 'dias_atraso_actual':30},
                        {'deuda_actual':0, 'pagos_mensuales_creditos':0, 'dias_atraso_actual':0},
                        {'deuda_actual':50000, 'pagos_mensuales_creditos':10000, 'dias_atraso_actual':30},
                        {'deuda_actual':0, 'pagos_mensuales_creditos':2500, 'dias_atraso_actual':0}):
            response = self.client.post('/api/v1/evaluar', json={**BASE, **changes})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['nivel_riesgo_preliminar'], 'Bajo')


class OrigenTests(unittest.TestCase):
    def request(self, peer, header):
        return Request({'type':'http', 'client':(peer,1234), 'headers':[(b'x-forwarded-for',header.encode())]})

    def test_solo_confia_en_proxy_explicito_y_un_solo_ip(self):
        with patch.dict(os.environ, {'LOCAL_AUTH_TRUSTED_PROXY_HOST':'frontend'}), \
                patch('backend.app.autenticacion_local.origen._direcciones_proxy', return_value={'172.18.0.3'}):
            self.assertEqual(origen_cliente(self.request('172.18.0.3','198.51.100.1')), '198.51.100.1')
            self.assertEqual(origen_cliente(self.request('172.18.0.3','198.51.100.2')), '198.51.100.2')
            self.assertEqual(origen_cliente(self.request('127.0.0.1','198.51.100.1')), '127.0.0.1')
            for header in ('mal','198.51.100.1, 198.51.100.2','fe80::1%eth0'):
                self.assertEqual(origen_cliente(self.request('172.18.0.3',header)), '172.18.0.3')
        with patch.dict(os.environ, {'LOCAL_AUTH_TRUSTED_PROXY_HOST':''}):
            self.assertEqual(origen_cliente(self.request('172.18.0.3','198.51.100.1')), '172.18.0.3')
