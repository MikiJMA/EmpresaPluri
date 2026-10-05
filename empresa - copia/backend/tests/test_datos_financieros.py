from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import os
import ssl
import threading
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.datos_financieros import proveedores as p, servicio as s

RealClient = httpx.Client
TOKEN_FICTICIO = 'a' * 64
PATH = '/api/v1/datos-financieros/indicadores'


def wb_payload(values=(3.8, -0.5)):
    return [{'pages': 1, 'total': 2}, [{'indicator': {'id': code}, 'countryiso3code': 'MEX',
             'date': '2025', 'value': value} for code, value in zip(p.BANCO_MUNDIAL_SERIES, values)]]


def bmx_payload(values=('20.4567', '7.00')):
    return {'bmx': {'series': [{'idSerie': code, 'datos': [{'fecha': '29/09/2026', 'dato': value}]}
            for code, value in zip(p.BANXICO_SERIES, values)]}}


class FinancierosTests(unittest.TestCase):
    def setUp(self):
        s._cache.clear()
        app.dependency_overrides[usuario_actual] = lambda: {'roles': ['Analista']}
        self.client = TestClient(app)
        self.env = patch.dict(os.environ, {'BANXICO_API_TOKEN': TOKEN_FICTICIO})
        self.env.start()
        self.requests = []

        def handler(request):
            self.requests.append(request)
            return httpx.Response(200, json=bmx_payload() if request.url.host == 'www.banxico.org.mx' else wb_payload())
        self.transport = httpx.MockTransport(handler)
        self.mock = patch.object(p.httpx, 'Client', side_effect=lambda **kwargs: RealClient(transport=self.transport, **kwargs))
        self.mock.start()

    def tearDown(self):
        self.mock.stop(); self.env.stop()
        app.dependency_overrides.clear()
        s._cache.clear()

    def test_sesion_obligatoria_sin_llamar_proveedores(self):
        app.dependency_overrides.clear()
        self.assertEqual(self.client.get(PATH).status_code, 401)
        self.assertEqual(self.requests, [])

    def test_contrato_real_de_consulta_y_procedencia(self):
        response = self.client.get(PATH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(response.json()['pais'], 'MX')
        bmx, wb = response.json()['proveedores']
        self.assertEqual([item['valor'] for item in bmx['indicadores']], [20.4567, 7.0])
        self.assertEqual([item['valor'] for item in wb['indicadores']], [3.8, -0.5])
        self.assertEqual(bmx['indicadores'][0]['periodo'], '2026-09-29')
        self.assertEqual(wb['indicadores'][0]['periodo'], '2025')
        self.assertNotIn(TOKEN_FICTICIO, response.text)
        self.assertNotIn('rfc', response.text)
        for request in self.requests:
            self.assertEqual(request.method, 'GET')
            self.assertEqual(request.content, b'')
            if request.url.host == 'www.banxico.org.mx':
                self.assertEqual(str(request.url), p.BANXICO_URL)
                self.assertEqual(request.headers['Bmx-Token'], TOKEN_FICTICIO)
                self.assertNotIn('token', request.url.query.decode())
            else:
                self.assertNotIn('Bmx-Token', request.headers)
                self.assertEqual(dict(request.url.params), {'format': 'json', 'mrnev': '1', 'source': '2', 'per_page': '10'})

    def test_sin_token_no_llama_banxico_y_banco_mundial_funciona(self):
        for token in ('', 'corto', 'a' * 63 + '\n', 'a' * 63 + '$'):
            s._cache.clear(); self.requests.clear()
            with patch.dict(os.environ, {'BANXICO_API_TOKEN': token}):
                bmx, wb = self.client.get(PATH).json()['proveedores']
            self.assertEqual(bmx['estado'], 'sin_configurar')
            self.assertEqual(bmx['indicadores'], [])
            self.assertEqual(wb['estado'], 'disponible')
            self.assertEqual(len(self.requests), 1)

    def test_cache_expira_no_es_mutable_y_configuracion_invalida_cache(self):
        with patch.object(s.time, 'monotonic', return_value=100):
            first = s.obtener_indicadores()
            second = s.obtener_indicadores()
        self.assertTrue(all(item['en_cache'] for item in second['proveedores']))
        self.assertEqual(len(self.requests), 2)
        first['proveedores'][1]['indicadores'][0]['valor'] = 999
        with patch.object(s.time, 'monotonic', return_value=101):
            self.assertEqual(s.obtener_indicadores()['proveedores'][1]['indicadores'][0]['valor'], 3.8)
        with patch.object(s.time, 'monotonic', return_value=3701):
            s.obtener_indicadores()
        self.assertEqual(len(self.requests), 4)
        with patch.dict(os.environ, {'BANXICO_API_TOKEN': ''}):
            self.assertEqual(s.obtener_indicadores()['proveedores'][0]['estado'], 'sin_configurar')

    def test_peticiones_concurrentes_comparten_una_consulta_por_proveedor(self):
        gate = threading.Barrier(5)
        def caller(_):
            gate.wait(timeout=5)
            return s.obtener_indicadores()
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(caller, range(5)))
        self.assertEqual(len(self.requests), 2)
        self.assertTrue(all(len(row['proveedores']) == 2 for row in results))

    def test_fallo_aislado_no_reenvia_detalles_y_no_sirve_cache_vencido(self):
        with patch.object(s.time, 'monotonic', return_value=0):
            self.client.get(PATH)
        def failure(request):
            if request.url.host == 'www.banxico.org.mx':
                return httpx.Response(403, text=f'privado: {TOKEN_FICTICIO}')
            return httpx.Response(200, json=wb_payload())
        self.transport.handler = failure
        with patch.object(s.time, 'monotonic', return_value=3601):
            response = self.client.get(PATH)
            cached = self.client.get(PATH).json()['proveedores'][0]
        bmx, wb = response.json()['proveedores']
        self.assertEqual(bmx['estado'], 'error')
        self.assertEqual(bmx['indicadores'], [])
        self.assertEqual(wb['estado'], 'disponible')
        self.assertTrue(cached['en_cache'])
        self.assertNotIn('privado', response.text)
        self.assertNotIn(TOKEN_FICTICIO, response.text)

    def test_cero_y_ausencia_no_se_confunden(self):
        with patch.object(p, '_leer_json', return_value=wb_payload((0, None))):
            items = p.consultar_banco_mundial()
        self.assertEqual(items[0]['valor'], 0.0)
        self.assertEqual(items[0]['estado'], 'disponible')
        self.assertIsNone(items[1]['valor'])
        self.assertEqual(items[1]['estado'], 'sin_dato')
        with patch.object(p, '_leer_json', return_value=bmx_payload(('20.00', 'N/E'))):
            self.assertIsNone(p.consultar_banxico(TOKEN_FICTICIO)[1]['valor'])
        payload = bmx_payload(); payload['bmx']['series'][1]['datos'] = []
        with patch.object(p, '_leer_json', return_value=payload):
            self.assertIsNone(p.consultar_banxico(TOKEN_FICTICIO)[1]['periodo'])

    def test_estado_parcial_si_falta_valor(self):
        with patch.object(p, '_leer_json', side_effect=lambda url, **_: bmx_payload() if url == p.BANXICO_URL else wb_payload((0, None))):
            wb = self.client.get(PATH).json()['proveedores'][1]
        self.assertEqual(wb['estado'], 'parcial')
        self.assertIsNone(wb['indicadores'][1]['valor'])

    def test_rechaza_identidad_formato_fecha_y_numero_invalido_wb(self):
        invalid = []
        for field, value in [('countryiso3code', 'USA'), ('date', '2025-01'), ('date', '9999'),
                             ('value', True), ('value', '3.8'), ('value', float('nan')), ('value', float('inf'))]:
            payload = wb_payload(); payload[1][0][field] = value; invalid.append(payload)
        payload = wb_payload(); payload[1][1] = deepcopy(payload[1][0]); invalid.append(payload)
        payload = wb_payload(); payload[0]['pages'] = 2; invalid.append(payload)
        payload = wb_payload(); payload[0]['total'] = True; invalid.append(payload)
        invalid.extend([{}, [], [None, None], [{'pages': 1, 'total': 2}, []]])
        for payload in invalid:
            with self.subTest(payload=payload), patch.object(p, '_leer_json', return_value=payload):
                with self.assertRaises(p.ErrorProveedor): p.consultar_banco_mundial()

    def test_banxico_rechaza_serie_fecha_y_valor_invalido(self):
        for field, value in [('dato', '1,23'), ('dato', 'NaN'), ('dato', '0'), ('dato', 'Infinity'),
                             ('dato', 20), ('fecha', '31/02/2025'), ('fecha', '01/01/9999')]:
            payload = bmx_payload(); payload['bmx']['series'][0]['datos'][0][field] = value
            with self.subTest(field=field, value=value), patch.object(p, '_leer_json', return_value=payload):
                with self.assertRaises(p.ErrorProveedor): p.consultar_banxico(TOKEN_FICTICIO)
        payload = bmx_payload(); payload['bmx']['series'][1]['idSerie'] = 'SF43718'
        with patch.object(p, '_leer_json', return_value=payload):
            with self.assertRaises(p.ErrorProveedor): p.consultar_banxico(TOKEN_FICTICIO)

    def test_http_timeouts_limites_redireccion_y_json_invalidos(self):
        for status in (302, 400, 401, 403, 429, 500):
            self.transport.handler = lambda _: httpx.Response(status, text='secreto', headers={'Bmx-secondsToReset': '60'})
            with self.subTest(status=status), self.assertRaises(p.ErrorProveedor) as raised:
                p.consultar_banxico(TOKEN_FICTICIO)
            self.assertNotIn('secreto', str(raised.exception))
        for response in (httpx.Response(200, text='<html>error</html>'),
                         httpx.Response(200, content=b'?', headers={'Content-Type': 'application/json'}),
                         httpx.Response(200, content=b' ' * (p.MAX_BYTES + 1), headers={'Content-Type': 'application/json'})):
            self.transport.handler = lambda _: response
            with self.assertRaises(p.ErrorProveedor): p.consultar_banco_mundial()
        def timeout(_): raise httpx.ReadTimeout('detalle privado')
        self.transport.handler = timeout
        with self.assertRaisesRegex(p.ErrorProveedor, 'tardó demasiado'): p.consultar_banco_mundial()

    def test_tls_13_banxico_y_redireccion_deshabilitada(self):
        with patch.object(p.httpx, 'Client', wraps=RealClient) as factory:
            # Otro parche evita toda conexión de red, pero permite inspeccionar la configuración.
            with patch.object(RealClient, 'stream') as stream:
                stream.return_value.__enter__.return_value = httpx.Response(200, json=bmx_payload())
                p.consultar_banxico(TOKEN_FICTICIO)
            self.assertEqual(factory.call_args.kwargs['verify'].minimum_version, ssl.TLSVersion.TLSv1_3)
            self.assertFalse(factory.call_args.kwargs['follow_redirects'])

    def test_banxico_400_token_y_cuota_se_distinguen_sin_filtrar_respuesta(self):
        self.transport.handler = lambda _: httpx.Response(400, json={'error': {'mensaje': TOKEN_FICTICIO}})
        with self.assertRaisesRegex(p.ErrorProveedor, 'Revisa tu token') as raised:
            p.consultar_banxico(TOKEN_FICTICIO)
        self.assertNotIn(TOKEN_FICTICIO, str(raised.exception))
        self.transport.handler = lambda _: httpx.Response(400, json={'error': {'mensaje': TOKEN_FICTICIO}},
            headers={'Bmx-secondsToReset': '60'})
        with self.assertRaisesRegex(p.ErrorProveedor, 'límite de consultas') as raised:
            p.consultar_banxico(TOKEN_FICTICIO)
        self.assertNotIn(TOKEN_FICTICIO, str(raised.exception))


if __name__ == '__main__':
    unittest.main()
