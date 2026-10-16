"""Recorrido integral API + PostgreSQL efímero; no es una prueba humana de navegador.

Login/JWT, reglas v2, repositorios, documentos, modelo numérico local y seguimiento
son reales en este recorrido. La explicación usa la plantilla determinista (NO IA).
Banxico y Banco Mundial usan exclusivamente MockTransport: NO consultas externas.
No lee archivos de configuración privada ni usa el volumen/base de trabajo.
"""
from datetime import datetime, timedelta, timezone
import os
import re
import unittest
from unittest.mock import patch
from uuid import uuid4

import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.autenticacion_local.repositorio import RepositorioUsuarios
from backend.app.integraciones.datos_financieros import servicio as financieros
from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES
from backend.app.integraciones.prediccion_local.cliente_local import MODELO_ID, MODELO_SHA256
from backend.app.persistencia_postgresql.migrar import migrar
from backend.app.seguimiento_crediticio.modelos import hoy_utc

REAL_HTTP_CLIENT = httpx.Client
PASSWORD_FIXTURE = 'Contrasena-ficticia-QA-123'
SECRET_FIXTURE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_entrega_fixture'
BASE = {'rfc': 'DEMO-ENTREGA-NO-REAL', 'ingresos_mensuales': 30000, 'gastos_mensuales': 10000,
        'deuda_actual': 100.10, 'pagos_mensuales_creditos': 50.05, 'dias_atraso_actual': 0}
PERFIL_ENIF = {'ingreso_laboral': 12000, 'periodicidad': 3, 'ingreso_variable': 1,
               'presupuesto': 1, 'gastos_cubiertos': 1, 'ahorro_emergencia': 4,
               'creditos': ['bancaria']}


@unittest.skipUnless(os.getenv('RUN_POSTGRES_TESTS') == '1', 'Requiere la base PostgreSQL efímera de la suite.')
class EntregaDemoPostgreSQLTests(unittest.TestCase):
    def setUp(self):
        # No usar database_url(): así el test no busca .env.postgresql privado.
        self.url = os.getenv('DATABASE_URL', '')
        connection = conninfo_to_dict(self.url)
        self.assertEqual(connection.get('dbname'), 'pluri_test', 'Este recorrido sólo admite la base efímera pluri_test.')
        self.assertEqual(connection.get('user'), 'ci', 'Este recorrido sólo admite el usuario de pruebas ci.')
        self.assertIn(connection.get('host'), ('127.0.0.1', 'localhost', '::1'),
                      'La base de pruebas debe usar loopback, nunca un servidor remoto.')
        self.assertEqual(connection.get('port', '5432'), '5432', 'No usar los puertos de PostgreSQL de trabajo.')
        self.schema = 'test_entrega_' + uuid4().hex
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.addCleanup(self._retirar_esquema_propio)
        self.env = patch.dict(os.environ, {
            'DATABASE_URL': make_conninfo(self.url, options='-c search_path=' + self.schema),
            'LOCAL_AUTH_ENABLED': 'true', 'LOCAL_AUTH_SECRET': SECRET_FIXTURE,
            'LOCAL_AUTH_TOKEN_SECONDS': '1800', 'EXPLICACIONES_PROVEEDOR': 'local',
            'DOCUMENTOS_PROVEEDOR': 'local', 'ML_PROVEEDOR': 'local',
            'BANXICO_API_TOKEN': 'a' * 64,
            'AZURE_OPENAI_API_KEY': '', 'AZURE_SEARCH_QUERY_KEY': '', 'AZURE_ML_API_KEY': '',
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        # Los helpers de producción leen el dotenv opcional: impedir también esa
        # lectura en este test aunque alguien lo ejecute fuera del contenedor QA.
        self.dotenv = patch('backend.app.persistencia_postgresql.conexion.load_dotenv', return_value=False)
        self.dotenv.start()
        self.addCleanup(self.dotenv.stop)
        migrar()
        migrar()  # También comprobar que las migraciones son repetibles.

        # Ninguna dependencia de identidad/persistencia es sustituida.
        self.overrides_anteriores = dict(app.dependency_overrides)
        app.dependency_overrides.clear()
        self.addCleanup(self._restaurar_overrides)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.peticiones_fixture = []
        self.mock_transport = httpx.MockTransport(self._respuesta_financiera_fixture)
        self.red_sync = patch('httpx.Client', side_effect=lambda **kwargs: REAL_HTTP_CLIENT(
            transport=self.mock_transport, **kwargs))
        self.red_async = patch('httpx.AsyncClient', side_effect=AssertionError('No se permiten consultas externas en entrega QA.'))
        self.red_entra = patch('backend.app.autenticacion_entra_id.seguridad.claves_publicas',
                               side_effect=AssertionError('El login de este recorrido es local, no Microsoft.'))
        self.cache_financiera = patch.object(financieros, '_cache', {})
        for stub in (self.red_sync, self.red_async, self.red_entra, self.cache_financiera):
            stub.start()
            self.addCleanup(stub.stop)

    def _retirar_esquema_propio(self):
        # Comprobación estricta antes de borrar únicamente el esquema UUID creado aquí.
        if not re.fullmatch(r'test_entrega_[a-f0-9]{32}', self.schema):
            raise RuntimeError('No se eliminará un esquema sin identidad de prueba válida.')
        with psycopg.connect(self.url) as conn:
            conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def _restaurar_overrides(self):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.overrides_anteriores)

    def _respuesta_financiera_fixture(self, request):
        self.peticiones_fixture.append(request)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.content, b'')
        # Fechas sintéticas válidas respecto del reloj UTC del test, no publicaciones reales.
        hoy = datetime.now(timezone.utc).date()
        if request.url.host == 'www.banxico.org.mx':
            self.assertEqual(request.headers['Bmx-Token'], 'a' * 64)
            return httpx.Response(200, json={'bmx': {'series': [
                {'idSerie': code, 'datos': [{'fecha': hoy.strftime('%d/%m/%Y'), 'dato': dato}]}
                for code, dato in [('SF43718', '20.1234'), ('SF61745', '7.00')]
            ]}})
        if request.url.host == 'api.worldbank.org':
            return httpx.Response(200, json=[{'pages': 1, 'total': 2}, [
                {'indicator': {'id': code}, 'countryiso3code': 'MEX', 'date': str(hoy.year - 1), 'value': dato}
                for code, dato in [('FP.CPI.TOTL.ZG', 3.8), ('NY.GDP.MKTP.KD.ZG', 1.2)]
            ]])
        raise AssertionError('El recorrido no admite destinos diferentes de los dos proveedores simulados.')

    def pedir(self, method, path, esperado=200, **kwargs):
        response = self.client.request(method, path, **kwargs)
        self.assertEqual(response.status_code, esperado, f'{method} {path}: {response.text}')
        return response.json()

    def login(self, usuario):
        data = self.pedir('POST', '/api/v1/auth/local/login', json={'usuario': usuario, 'password': PASSWORD_FIXTURE})
        self.assertEqual(data['token_type'], 'bearer')
        self.assertEqual(data['user']['proveedor'], 'local')
        self.assertNotIn(PASSWORD_FIXTURE, str(data))
        self.assertNotIn(SECRET_FIXTURE, str(data))
        return data, {'Authorization': 'Bearer ' + data['access_token']}

    def test_recorrido_integral_demo_con_login_real_y_datos_aislados(self):
        repo_cuentas = RepositorioUsuarios()
        self.assertEqual(self.pedir('GET', '/api/v1/auth/config')['local'],
                         {'habilitado': True, 'cuentas_disponibles': False})
        analista_id = repo_cuentas.guardar('qa.entrega', 'Analista QA ficticio', PASSWORD_FIXTURE, ['Analista'])
        repo_cuentas.guardar('qa.administrador', 'Administrador QA ficticio', PASSWORD_FIXTURE, ['Administrador'])
        for ruta in ('/api/v1/dashboard', '/api/v1/evaluaciones', '/api/v1/ml/estado',
                     '/api/v1/azure-search/documentos', '/api/v1/seguimiento/creditos'):
            self.pedir('GET', ruta, esperado=401)
        sesion, headers = self.login('qa.entrega')
        self.assertEqual(sesion['user']['id'], analista_id)
        self.assertEqual(self.pedir('GET', '/api/v1/auth/me', headers=headers), sesion['user'])
        self.assertEqual(app.dependency_overrides, {})

        with self.subTest(etapa='Evaluaciones v2, idempotencia, historial y revisión'):
            guardadas = {}
            analisis_modelo = None
            for score, riesgo in ((200, 'Alto'), (900, 'Bajo')):
                ident = str(uuid4())
                payload = {**BASE, 'score_buro_actual': score, 'perfil_enif': PERFIL_ENIF}
                data = self.pedir('POST', '/api/v1/evaluar', headers={**headers, 'Idempotency-Key': ident}, json=payload)
                self.assertTrue(data['guardado'])
                self.assertEqual(data['id'], ident)
                self.assertEqual(data['version_modelo'], 'reglas-demo-v2')
                self.assertEqual(data['nivel_riesgo_preliminar'], riesgo)
                self.assertEqual(data['margen_libre'], 20000)
                modelo = data['analisis_mexico']
                self.assertEqual(modelo['modelo_id'], 'nexocredit-enif2024-logistica-v1')
                self.assertIs(modelo['reglas_score_utilizadas'], False)
                self.assertIs(modelo['control_uso']['decision_automatizada_habilitada'], False)
                if analisis_modelo is not None:
                    self.assertEqual(modelo, analisis_modelo)
                analisis_modelo = modelo
                self.assertEqual(self.pedir('POST', '/api/v1/evaluar', headers={**headers, 'Idempotency-Key': ident},
                                           json=payload), data)
                guardadas[riesgo] = ident
            resumen = self.pedir('GET', '/api/v1/dashboard', headers=headers)
            self.assertEqual([resumen[k] for k in ('total', 'alto', 'medio', 'bajo')], [2, 1, 0, 1])
            self.assertEqual(self.pedir('GET', '/api/v1/dashboard?riesgo=Alto', headers=headers)['total'], 1)
            historial = self.pedir('GET', '/api/v1/evaluaciones?limite=1', headers=headers)
            self.assertTrue(historial['hay_mas'])
            self.assertEqual(len(historial['items']), 1)
            bajo = guardadas['Bajo']
            revision = {'id': str(uuid4()), 'version_anterior': 0, 'estado': 'Aprobada',
                        'observaciones': 'Revisión de un escenario ficticio; no autoriza crédito real.',
                        'responsable': 'NO-SUPLANTAR-RESPONSABLE'}
            registrada = self.pedir('POST', f'/api/v1/evaluaciones/{bajo}/revisiones', headers=headers, json=revision)
            self.assertEqual(registrada['responsable'], sesion['user']['responsable'])
            detalle = self.pedir('GET', f'/api/v1/evaluaciones/{bajo}', headers=headers)
            self.assertEqual(detalle['estado_revision'], 'Aprobada')
            self.assertEqual(detalle['version_revision'], 1)
            self.assertEqual(detalle['solicitud'], {**BASE, 'score_buro_actual': 900, 'perfil_enif': PERFIL_ENIF})
            self.assertEqual(detalle['analisis_mexico'], analisis_modelo)

        with self.subTest(etapa='Documentos, explicación NO IA, modelo local y fuentes simuladas'):
            documentos = self.pedir('GET', '/api/v1/azure-search/documentos', headers=headers)
            self.assertEqual(documentos['proveedor'], 'local')
            self.assertEqual(len(documentos['resultados']), 15)
            self.assertEqual(len({d['fuente'] for d in documentos['resultados']}), 3)
            busqueda = self.pedir('POST', '/api/v1/azure-search/buscar', headers=headers, json={'consulta': 'reglas-demo-v2'})
            self.assertTrue(any(d['fuente'] == 'guia-demostracion-v2' for d in busqueda['resultados']))
            for riesgo, ident in guardadas.items():
                explicacion = self.pedir('POST', f'/api/v1/evaluaciones/{ident}/explicacion', headers=headers)
                self.assertFalse(explicacion['generada_por_ia'])
                self.assertEqual(explicacion['proveedor'], 'local')
                self.assertEqual(explicacion['fuentes'][0]['version'], '2.0')
                self.assertIn('Riesgo preliminar ' + riesgo, explicacion['explicacion'])
                self.assertNotIn(BASE['rfc'], str(explicacion))
                self.assertEqual(self.pedir('POST', f'/api/v1/evaluaciones/{ident}/explicacion', headers=headers), explicacion)
            valores = {n: 0 for n in FEATURES}
            valores['LIMIT_BAL'] = 200000
            valores.update({n: 3000 for n in FEATURES if n.startswith('PAY_AMT')})
            prediccion = self.pedir('POST', '/api/v1/ml/predecir', headers=headers, json={'valores': valores})
            self.assertIs(type(prediccion['incumplimiento_predicho']), bool)
            self.assertEqual(prediccion['modelo_configurado'], MODELO_ID)
            self.assertEqual(prediccion['modelo_sha256'], MODELO_SHA256)
            self.assertEqual(prediccion['proveedor'], 'local')
            self.assertNotIn('score', prediccion)
            indicadores = self.pedir('GET', '/api/v1/datos-financieros/indicadores', headers=headers)
            self.assertEqual([p['estado'] for p in indicadores['proveedores']], ['disponible', 'disponible'])
            self.assertEqual(len(self.peticiones_fixture), 2)
            self.assertEqual({r.url.host for r in self.peticiones_fixture}, {'www.banxico.org.mx', 'api.worldbank.org'})

        with self.subTest(etapa='Plan ficticio, abonos exactos, alertas y auditoría por rol'):
            hoy = hoy_utc()
            plan = {'id': str(uuid4()), 'evaluacion_id': bajo, 'concepto': 'Plan exclusivamente ficticio QA',
                    'fecha_apertura': str(hoy - timedelta(days=30)), 'monto_total_pactado': '100.10',
                    'cuotas': [{'vencimiento': str(hoy - timedelta(days=5)), 'importe': '50.05'},
                               {'vencimiento': str(hoy + timedelta(days=5)), 'importe': '50.05'}]}
            credito = self.pedir('POST', '/api/v1/seguimiento/creditos', headers=headers, json=plan)
            self.assertEqual(credito['resumen']['saldo_vencido'], '50.05')
            self.assertEqual(credito['alertas'][0]['estado'], 'Pendiente')
            alerta = credito['alertas'][0]
            atencion = {'id': str(uuid4()), 'version_anterior': alerta['version'], 'observaciones': 'Seguimiento ficticio QA.'}
            atendida = self.pedir('POST', f"/api/v1/seguimiento/alertas/{alerta['id']}/atender", headers=headers, json=atencion)
            self.assertEqual(atendida['alertas'][0]['estado'], 'Atendida')
            self.assertEqual(atendida['resumen']['saldo_vencido'], '50.05')
            pago = {'id': str(uuid4()), 'cuota_id': credito['resumen']['cuotas'][0]['id'],
                    'importe': '20.02', 'fecha_pago': str(hoy)}
            pago_url = f"/api/v1/seguimiento/creditos/{credito['id']}/pagos"
            parcial = self.pedir('POST', pago_url, headers=headers, json=pago)
            self.assertEqual(parcial['resumen']['saldo_vencido'], '30.03')
            self.assertEqual(self.pedir('POST', pago_url, headers=headers, json=pago)['resumen']['total_pagado'], '20.02')
            final = self.pedir('POST', pago_url, headers=headers, json={**pago, 'id': str(uuid4()), 'importe': '30.03'})
            self.assertEqual(final['resumen']['total_pagado'], '50.05')
            self.assertEqual(final['resumen']['saldo_pendiente'], '50.05')
            self.assertEqual(final['resumen']['saldo_vencido'], '0.00')
            self.assertEqual(final['resumen']['puntualidad_cuotas_vencidas_pct'], '0.00')
            self.assertEqual(final['alertas'][0]['estado'], 'Resuelta')
            self.assertEqual(len(final['pagos']), 2)
            self.assertEqual(len(self.pedir('GET', '/api/v1/seguimiento/creditos', headers=headers)['items']), 1)
            self.pedir('GET', '/api/v1/seguimiento/auditoria', esperado=403, headers=headers)
            _, admin_headers = self.login('qa.administrador')
            eventos = self.pedir('GET', '/api/v1/seguimiento/auditoria', headers=admin_headers)['items']
            self.assertTrue({'credito_creado', 'pago_registrado', 'alerta_atendida'}.issubset({e['accion'] for e in eventos}))
            self.assertTrue(all(e['responsable'] == sesion['user']['responsable'] for e in eventos))

        # Ni el modelo académico, el contexto económico ni los pagos cambian el scoring.
        for riesgo, ident in guardadas.items():
            detalle = self.pedir('GET', f'/api/v1/evaluaciones/{ident}', headers=headers)
            self.assertEqual(detalle['nivel_riesgo_preliminar'], riesgo)
            self.assertEqual(detalle['version_modelo'], 'reglas-demo-v2')
        with psycopg.connect(os.environ['DATABASE_URL']) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM evaluaciones').fetchone()[0], 2)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM revisiones').fetchone()[0], 1)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM cache_explicaciones').fetchone()[0], 2)
            self.assertEqual(conn.execute('SELECT SUM(cantidad) FROM cuotas_explicaciones').fetchone()[0], 2)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM pagos_demo').fetchone()[0], 2)
        repo_cuentas.desactivar('qa.entrega')
        self.pedir('GET', '/api/v1/auth/me', esperado=401, headers=headers)
        self.assertEqual(len(self.peticiones_fixture), 2, 'Sólo se ejecutaron dos solicitudes de red simuladas.')
