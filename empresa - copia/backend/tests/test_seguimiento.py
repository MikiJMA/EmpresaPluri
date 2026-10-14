"""Obligaciones ficticias, decimales y transacciones. Nunca base de trabajo."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import json
import os
from time import perf_counter
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.app.main import app
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.persistencia_postgresql.conexion import database_url, conectar
from backend.app.persistencia_postgresql.migrar import migrar
from backend.app.persistencia_postgresql.repositorio import RepositorioEvaluaciones
from backend.app.seguimiento_crediticio.repositorio import RepositorioSeguimiento, obtener_seguimiento
from backend.app.seguimiento_crediticio.modelos import NuevoCredito, NuevoPago, hoy_utc
from backend.app.seguimiento_crediticio.analisis import calcular, indicadores

BASE=dict(rfc='DEMO-SEGUIMIENTO', ingresos_mensuales=30000,gastos_mensuales=10000,score_buro_actual=700,deuda_actual=50000,pagos_mensuales_creditos=2500,dias_atraso_actual=0)
RESULT=dict(rfc=BASE['rfc'],version_modelo='reglas-demo-v1',margen_libre=20000,nivel_riesgo_preliminar='Bajo')

def plan(evaluacion=None):
    today=hoy_utc()
    return dict(id=str(uuid4()),evaluacion_id=str(evaluacion or uuid4()),concepto='Plan ficticio',fecha_apertura=str(today-timedelta(days=30)),monto_total_pactado='100.00',
                cuotas=[dict(vencimiento=str(today-timedelta(days=5)),importe='50.00'),dict(vencimiento=str(today+timedelta(days=5)),importe='50.00')])


class SeguimientoUnitTests(unittest.TestCase):
    def test_importes_exactos_y_rechazo_de_coerciones(self):
        base=plan()
        for value in (True,False,'1e2','NaN','Infinity','1.001',-1,0,'1000000001','1,000.00',{},[]):
            with self.subTest(value=value),self.assertRaises(ValidationError):
                NuevoCredito.model_validate({**base,'monto_total_pactado':value})
        base.update(monto_total_pactado='0.30',cuotas=[{**c,'importe':v} for c,v in zip(base['cuotas'],('0.10','0.20'))])
        self.assertEqual(NuevoCredito.model_validate(base).monto_total_pactado,Decimal('.30'))

    def test_plan_fechas_suma_y_limites(self):
        base=plan()
        for cambios in ({'concepto':'\u200b'},{'monto_total_pactado':'99.99'},{'fecha_apertura':str(hoy_utc()+timedelta(days=1))},
                        {'cuotas':[]},{'cuotas':base['cuotas']*31},{'cuotas':list(reversed(base['cuotas']))},
                        {'fecha_apertura':'2026-02-31'},{'fecha_apertura':True},{'propiedad_extra':'no'}):
            with self.assertRaises(ValidationError):NuevoCredito.model_validate({**base,**cambios})

    def test_pago_futuro_o_fecha_no_iso_rechazados(self):
        base=dict(id=str(uuid4()),cuota_id=str(uuid4()),importe='1.00',fecha_pago=str(hoy_utc()))
        for value in (str(hoy_utc()+timedelta(days=1)),True,'2026-02-31','2026-01-01T00:00:00Z'):
            with self.assertRaises(ValidationError):NuevoPago.model_validate({**base,'fecha_pago':value})

    def test_analisis_distingue_ausencia_cero_y_ratio_sin_umbral(self):
        i=indicadores(BASE)
        self.assertEqual(i['pagos_sobre_ingresos_pct'],'8.33')
        self.assertEqual(i['gastos_sobre_ingresos_pct'],'33.33')
        self.assertEqual(i['deuda_sobre_ingreso_mensual_veces'],'1.67')
        self.assertIsNone(indicadores({**BASE,'deuda_actual':None})['deuda_sobre_ingreso_mensual_veces'])
        self.assertEqual(indicadores({**BASE,'deuda_actual':0})['deuda_sobre_ingreso_mensual_veces'],'0.00')
        self.assertIsNotNone(indicadores({**BASE,'ingresos_mensuales':5e-324})['pagos_sobre_ingresos_pct'])

    def test_corte_excluye_pagos_futuros_y_no_confunde_tarde_con_puntual(self):
        cid=uuid4();qid=uuid4();hoy=date(2026,10,12)
        c=dict(id=cid,monto_total_pactado=Decimal('100'))
        cuotas=[dict(id=qid,vencimiento=date(2026,10,10),importe=Decimal('100'))]
        pagos=[dict(cuota_id=qid,fecha_pago=date(2026,10,12),importe=Decimal('100'))]
        anterior=calcular(c,cuotas,pagos,date(2026,10,11))
        self.assertEqual(anterior['saldo_vencido'],'100.00');self.assertEqual(anterior['total_pagado'],'0.00')
        actual=calcular(c,cuotas,pagos,hoy)
        self.assertEqual(actual['saldo_pendiente'],'0.00');self.assertEqual(actual['dias_atraso_maximo'],0)
        self.assertEqual(actual['cumplimiento_cuotas_vencidas_pct'],'100.00');self.assertEqual(actual['puntualidad_cuotas_vencidas_pct'],'0.00')

    def test_rutas_sin_sesion_y_admin_diferenciado(self):
        client=TestClient(app)
        app.dependency_overrides.clear()
        for path in ('/creditos','/auditoria','/creditos/'+str(uuid4())):
            self.assertEqual(client.get('/api/v1/seguimiento'+path).status_code,401)
        for path in ('/creditos','/creditos/'+str(uuid4())+'/pagos','/creditos/'+str(uuid4())+'/actualizar-alertas','/alertas/'+str(uuid4())+'/atender'):
            self.assertEqual(client.post('/api/v1/seguimiento'+path,json={}).status_code,401)
        repo=Mock()
        app.dependency_overrides[usuario_actual]=lambda:{'id':'fixture','responsable':'Fixture','roles':['Analista']}
        app.dependency_overrides[obtener_seguimiento]=lambda:repo
        try:
            self.assertEqual(client.get('/api/v1/seguimiento/auditoria').status_code,403)
            repo.auditoria.assert_not_called()
            self.assertEqual(client.get('/api/v1/seguimiento/creditos?offset=1000001').status_code,422)
        finally:app.dependency_overrides.clear()


@unittest.skipUnless(os.getenv('RUN_POSTGRES_TESTS')=='1','Sólo PostgreSQL temporal de la suite.')
class SeguimientoPostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.url=database_url();self.schema='test_seguimiento_'+uuid4().hex
        with psycopg.connect(self.url) as conn:conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.env=patch.dict(os.environ,{'DATABASE_URL':make_conninfo(self.url,options='-c search_path='+self.schema)});self.env.start()
        migrar();migrar()
        self.user={'id':str(uuid4()),'responsable':'Analista sintético','roles':['Analista']}
        app.dependency_overrides[usuario_actual]=lambda:self.user
        app.dependency_overrides[obtener_seguimiento]=RepositorioSeguimiento
        self.client=TestClient(app)
        self.eval=uuid4();RepositorioEvaluaciones().guardar(self.eval,BASE,RESULT)
        self.payload=plan(self.eval)

    def tearDown(self):
        app.dependency_overrides.clear();self.env.stop()
        with psycopg.connect(self.url) as conn:conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def crear(self):
        r=self.client.post('/api/v1/seguimiento/creditos',json=self.payload)
        self.assertEqual(r.status_code,200,r.text)
        return r.json()

    def pago(self,detail,importe='50.00'):
        return dict(id=str(uuid4()),cuota_id=detail['resumen']['cuotas'][0]['id'],importe=importe,fecha_pago=str(hoy_utc()))

    def test_crear_reintentar_conflicto_y_evaluacion_intacta(self):
        first=self.crear()
        self.assertEqual(self.client.post('/api/v1/seguimiento/creditos',json=self.payload).status_code,200)
        self.assertEqual(self.client.post('/api/v1/seguimiento/creditos',json={**self.payload,'concepto':'Distinto'}).status_code,409)
        self.assertEqual(self.client.post('/api/v1/seguimiento/creditos',json={**self.payload,'id':str(uuid4())}).status_code,409)
        self.assertEqual(first['resumen']['saldo_pendiente'],'100.00')
        self.assertEqual(first['alertas'][0]['estado'],'Pendiente')
        self.assertEqual(RepositorioEvaluaciones().obtener(self.eval)['nivel_riesgo_preliminar'],'Bajo')
        self.assertEqual(RepositorioEvaluaciones().obtener(self.eval)['solicitud'],BASE)
        with conectar() as conn:self.assertEqual(conn.execute('SELECT count(*) AS n FROM creditos_demo').fetchone()['n'],1)

    def test_pagos_parciales_idempotentes_y_alerta_resuelta(self):
        d=self.crear();url='/api/v1/seguimiento/creditos/'+d['id']+'/pagos';p=self.pago(d,'20.00')
        first=self.client.post(url,json=p);self.assertEqual(first.status_code,200)
        self.assertEqual(first.json()['resumen']['saldo_vencido'],'30.00')
        self.assertEqual(self.client.post(url,json=p).json()['resumen']['total_pagado'],'20.00')
        self.assertEqual(self.client.post(url,json={**p,'importe':'21.00'}).status_code,409)
        self.assertEqual(self.client.post(url,json={**p,'id':str(uuid4()),'importe':'31.00'}).status_code,409)
        final=self.client.post(url,json=self.pago(d,'30.00')).json()
        self.assertEqual(final['alertas'][0]['estado'],'Resuelta')
        self.assertEqual(final['resumen']['puntualidad_cuotas_vencidas_pct'],'0.00')
        self.assertEqual(len(final['pagos']),2)

    def test_pago_no_admite_cuota_ajena_fecha_previa_o_clave_suplantada(self):
        d=self.crear();url='/api/v1/seguimiento/creditos/'+d['id']+'/pagos';p=self.pago(d)
        self.assertEqual(self.client.post(url,json={**p,'cuota_id':str(uuid4())}).status_code,404)
        self.assertEqual(self.client.post(url,json={**p,'fecha_pago':str(hoy_utc()-timedelta(days=40))}).status_code,422)
        self.assertEqual(self.client.post(url,json={**p,'responsable':'Falso'}).status_code,422)

    def test_concurrencia_no_sobrepaga_y_reintentos_no_duplican(self):
        d=self.crear();url='/api/v1/seguimiento/creditos/'+d['id']+'/pagos'
        p=self.pago(d,'30.00')
        with ThreadPoolExecutor(max_workers=4) as pool:
            estados=list(pool.map(lambda _:self.client.post(url,json=p).status_code,range(8)))
        self.assertEqual(estados,[200]*8)
        with ThreadPoolExecutor(max_workers=4) as pool:
            estados=list(pool.map(lambda _:self.client.post(url,json=self.pago(d,'15.00')).status_code,range(4)))
        self.assertEqual(sorted(estados),[200,409,409,409])
        final=self.client.get('/api/v1/seguimiento/creditos/'+d['id']).json()
        self.assertEqual(final['resumen']['total_pagado'],'45.00');self.assertEqual(len(final['pagos']),2)

    def test_atencion_versionada_no_es_pago_y_auditoria_exige_admin(self):
        d=self.crear();a=d['alertas'][0];url='/api/v1/seguimiento/alertas/'+a['id']+'/atender'
        body=dict(id=str(uuid4()),version_anterior=a['version'],observaciones='Se revisó la cuota ficticia')
        response=self.client.post(url,json=body);self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['alertas'][0]['estado'],'Atendida')
        self.assertEqual(response.json()['resumen']['saldo_vencido'],'50.00')
        self.assertEqual(self.client.post(url,json=body).status_code,200)
        self.assertEqual(self.client.post(url,json={**body,'id':str(uuid4())}).status_code,409)
        self.assertEqual(self.client.post(url,json={**body,'observaciones':'\u200b'}).status_code,422)
        self.assertEqual(self.client.get('/api/v1/seguimiento/auditoria').status_code,403)
        self.user['roles']=['Administrador']
        eventos=self.client.get('/api/v1/seguimiento/auditoria').json()['items']
        self.assertTrue(any(e['accion']=='alerta_atendida' for e in eventos))
        self.assertTrue(all(e['responsable']=='Analista sintético' for e in eventos))
        self.assertTrue(all('actor_hash' not in e and 'datos' not in e for e in eventos))

    def test_refrescar_sin_cambios_no_duplica_eventos(self):
        d=self.crear()
        for _ in range(3):self.assertEqual(self.client.post('/api/v1/seguimiento/creditos/'+d['id']+'/actualizar-alertas').status_code,200)
        with conectar() as conn:self.assertEqual(conn.execute('SELECT count(*) AS n FROM eventos_seguimiento_demo').fetchone()['n'],2)

    def test_fallo_al_auditar_revierte_pago_y_no_filtra_error(self):
        d=self.crear()
        with patch.object(RepositorioSeguimiento,'_evento',side_effect=psycopg.OperationalError('LLAVE_PRIVADA_SINTETICA')):
            r=self.client.post('/api/v1/seguimiento/creditos/'+d['id']+'/pagos',json=self.pago(d))
        self.assertEqual(r.status_code,503);self.assertNotIn('LLAVE_PRIVADA',r.text)
        self.assertEqual(self.client.get('/api/v1/seguimiento/creditos/'+d['id']).json()['resumen']['total_pagado'],'0.00')

    def test_decimales_exactos_en_postgres(self):
        self.payload.update(monto_total_pactado='0.30',cuotas=[{**q,'importe':v} for q,v in zip(self.payload['cuotas'],('0.10','0.20'))])
        d=self.crear()
        d=self.client.post('/api/v1/seguimiento/creditos/'+d['id']+'/pagos',json=self.pago(d,'0.10')).json()
        p={**self.pago(d,'0.20'),'cuota_id':d['resumen']['cuotas'][1]['id']}
        d=self.client.post('/api/v1/seguimiento/creditos/'+d['id']+'/pagos',json=p).json()
        self.assertEqual(d['resumen']['total_pagado'],'0.30');self.assertEqual(d['resumen']['saldo_pendiente'],'0.00')

    def test_medicion_local_lecturas_secuenciales_y_concurrentes(self):
        d=self.crear();url='/api/v1/seguimiento/creditos/'+d['id']
        def medir(_):
            start=perf_counter();r=self.client.get(url);self.assertEqual(r.status_code,200)
            return (perf_counter()-start)*1000
        muestras=[medir(n) for n in range(40)]
        with ThreadPoolExecutor(max_workers=4) as pool:concurrentes=list(pool.map(medir,range(40)))
        def stats(values):
            ordered=sorted(values)
            return {'peticiones':len(values),'p50_ms':round(ordered[len(ordered)//2],2),'p95_ms':round(ordered[int(len(ordered)*.95)-1],2),'max_ms':round(max(values),2)}
        print('RENDIMIENTO_SEGUIMIENTO='+json.dumps({'entorno':'TestClient/FastAPI/PostgreSQL Docker temporal; sin navegador ni TLS/red externa','secuencial':stats(muestras),'cuatro_hilos':stats(concurrentes),'creditos_fixture':1,'cuotas_fixture':2,'errores_http':0}))
