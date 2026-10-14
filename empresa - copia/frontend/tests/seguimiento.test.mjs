import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { centavos,validarCredito,validarCreditos,validarAuditoria } from '../src/seguimiento_crediticio/contratos.mjs'

const id='cf53ff00-9981-4ea2-881b-cb62a7584e04',cuota1='cf53ff00-9981-4ea2-881b-cb62a7584e05',cuota2='cf53ff00-9981-4ea2-881b-cb62a7584e06'
const fixture={id,evaluacion_id:id,concepto:'Plan sintético',fecha_apertura:'2026-10-01',alertas_revisadas:'2026-10-12',
  resumen:{fecha_corte:'2026-10-12',moneda:'MXN',total_pactado:'100.00',total_pagado:'0.00',saldo_pendiente:'100.00',saldo_vencido:'50.00',dias_atraso_maximo:5,
    cuotas_vencidas:1,cuotas_completas_vencidas:0,cuotas_pagadas_a_tiempo:0,cumplimiento_cuotas_vencidas_pct:'0.00',puntualidad_cuotas_vencidas_pct:'0.00',
    cuotas:[{id:cuota1,vencimiento:'2026-10-07',importe:'50.00',pagado:'0.00',saldo:'50.00',dias_atraso:5,estado:'Vencida'},
      {id:cuota2,vencimiento:'2026-10-17',importe:'50.00',pagado:'0.00',saldo:'50.00',dias_atraso:0,estado:'Pendiente'}],acciones_seguimiento:['Revisar cuotas vencidas.'],aviso:'Demo: no autoriza créditos.'},
  indicadores:{margen_capturado:'20000.00',pagos_sobre_ingresos_pct:'8.33',gastos_sobre_ingresos_pct:'33.33',deuda_sobre_ingreso_mensual_veces:'1.67',aviso:'Datos capturados, no verificados.'},
  pagos:[],alertas:[{id,credito_id:id,cuota_id:cuota1,tipo:'CUOTA_VENCIDA',estado:'Pendiente',saldo:'50.00',dias_atraso:5,version:1,observaciones:''}]}
const panel=await cargarComponente(new URL('../src/seguimiento_crediticio/PanelCredito.jsx',import.meta.url))

test('seguimiento suma centavos sin coma flotante y exige moneda decimal canónica',()=>{
  assert.equal(centavos('0.10')+centavos('0.20'),centavos('0.30'))
  for(const value of ['NaN','Infinity','1e2','1.001',1,true,'-1.00','1000000001.00']) assert.throws(()=>centavos(value),/Importe/)
})
test('contrato de seguimiento conserva relaciones y saldos de cuotas',()=>{
  assert.equal(validarCredito(fixture),fixture)
  for(const cambios of [{id:'otro'},{resumen:{...fixture.resumen,saldo_pendiente:'99.00'}},{resumen:{...fixture.resumen,total_pagado:'1.00'}},
    {resumen:{...fixture.resumen,saldo_vencido:'101.00'}},{resumen:{...fixture.resumen,cuotas_pagadas_a_tiempo:2}},
    {resumen:{...fixture.resumen,fecha_corte:'2026-02-31'}},{alertas:[{...fixture.alertas[0],credito_id:cuota1}]},
    {pagos:[{id,credito_id:id,cuota_id:id,importe:'1.00',fecha_pago:'2026-10-12'}]},
    {resumen:{...fixture.resumen,cuotas:[fixture.resumen.cuotas[0],fixture.resumen.cuotas[0]]}}]) assert.throws(()=>validarCredito({...fixture,...cambios}),/contrato/)
})
test('listado y auditoría rechazan objetos nulos, claves ajenas y paginación excesiva',()=>{
  const list={items:[{id,evaluacion_id:id,concepto:'Demo',monto_total_pactado:'100.00',fecha_apertura:'2026-10-01'}],hay_mas:false,limite:20,offset:0}
  assert.equal(validarCreditos(list),list)
  for(const value of [null,{...list,items:[null]},{...list,offset:1000001}]) assert.throws(()=>validarCreditos(value),/contrato/)
  assert.equal(validarAuditoria({items:[],hay_mas:false,limite:20,offset:0}).items.length,0)
  assert.throws(()=>validarAuditoria({items:[{id,credito_id:id,accion:'APROBAR_CREDITO_REAL',responsable:'Demo',fecha:'2026-10-12T10:00:00Z'}],hay_mas:false,limite:20,offset:0}),/contrato/)
})
test('indicadores admiten ausencia, cero y ratios altos sin tratarlos como riesgo',()=>{
  const indicadores={...fixture.indicadores,pagos_sobre_ingresos_pct:null,deuda_sobre_ingreso_mensual_veces:'0.00',gastos_sobre_ingresos_pct:'999999999999.00'}
  assert.equal(validarCredito({...fixture,indicadores}).indicadores,indicadores)
  assert.throws(()=>validarCredito({...fixture,indicadores:{...indicadores,pagos_sobre_ingresos_pct:true}}),/contrato/)
})
test('panel presenta pagos/atrasos con avisos, sin identidad bancaria o predicción inventada',()=>{
  const html=renderToStaticMarkup(createElement(panel.PanelCredito,{data:validarCredito(fixture)}))
  assert.match(html,/Saldo vencido/);assert.match(html,/Puntualidad: 0.00%/)
  assert.match(html,/Una cuota completada tarde no cuenta como puntual/)
  assert.match(html,/no autoriza créditos/i);assert.match(html,/No hay pagos registrados/)
  assert.doesNotMatch(html,/Buró verificado|APROBADO|probabilidad del/)
  const hostile={...fixture,resumen:{...fixture.resumen,acciones_seguimiento:['<script>malicioso</script>']}}
  assert.match(renderToStaticMarkup(createElement(panel.PanelCredito,{data:hostile})),/&lt;script&gt;/)
})
test('auditoría muestra nombre sin el UUID técnico y escapa observaciones visuales',()=>{
  const html=renderToStaticMarkup(createElement(panel.PanelAuditoria,{data:{items:[{id,credito_id:id,accion:'pago_registrado',responsable:`<img> [local:${id}]`,fecha:'2026-10-12T10:00:00Z'}]}}))
  assert.match(html,/&lt;img&gt;/);assert.doesNotMatch(html,/local:/);assert.match(html,/sólo Administrador/)
})
test('cliente real conserva dinero como texto y rechaza una respuesta inválida',async t=>{
  const old=globalThis.qaSeguimientoFetch;t.after(()=>{globalThis.qaSeguimientoFetch=old})
  const source=(await readFile(new URL('../src/seguimiento_crediticio/servicio.js',import.meta.url),'utf8'))
    .replace("import { fetchAutenticado as fetch } from '../autenticacion/cliente'",'const fetch=(...args)=>globalThis.qaSeguimientoFetch(...args)')
    .replace('import.meta.env.VITE_API_URL',"'/'")
    .replace("'../evaluacion_crediticia/servicios/contratos.mjs'",JSON.stringify(new URL('../src/evaluacion_crediticia/servicios/contratos.mjs',import.meta.url).href))
    .replace("'./contratos.mjs'",JSON.stringify(new URL('../src/seguimiento_crediticio/contratos.mjs',import.meta.url).href))
  const client=await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`)
  let enviado
  globalThis.qaSeguimientoFetch=async(_url,options)=>{enviado=JSON.parse(options.body);return{ok:true,json:async()=>fixture}}
  const body={id,cuota_id:cuota1,importe:'0.10',fecha_pago:'2026-10-12'}
  await client.registrarPago(id,body);assert.deepEqual(enviado,body)
  globalThis.qaSeguimientoFetch=async()=>({ok:true,json:async()=>({})})
  await assert.rejects(client.cargarCredito(id),/contrato/)
})
test('interfaz preserva claves de reintento, guarda de selección y límite de plan',async()=>{
  const view=await readFile(new URL('../src/seguimiento_crediticio/SeguimientoCreditos.jsx',import.meta.url),'utf8')
  const detail=await readFile(new URL('../src/seguimiento_crediticio/DetalleCredito.jsx',import.meta.url),'utf8')
  const marco=await readFile(new URL('../src/interfaz/MarcoAplicacion.jsx',import.meta.url),'utf8')
  const secciones=await readFile(new URL('../src/interfaz/secciones.mjs',import.meta.url),'utf8')
  assert.match(view,/seleccionActual.current===next.id/);assert.match(view,/clave.current \|\|= crypto.randomUUID/)
  assert.match(view,/lecturaDetalle.current===intento/);assert.match(view,/lecturaDetalle.current\+=1/)
  assert.match(view,/form.cuotas.length>=60/);assert.match(view,/roles\?\.includes\('Administrador'\)/)
  assert.match(detail,/pagoKey.current \|\|= crypto.randomUUID/);assert.match(detail,/Atendida no significa pagada/)
  assert.match(marco,/SECCIONES.map/);assert.match(secciones,/\['creditos', 'Créditos y pagos'/)
})
test('el ledger rechaza estado/atraso/pagos/porcentajes contradictorios aunque cuadren totales',()=>{
  for(const cambio of [{saldo_vencido:'40.00'},{dias_atraso_maximo:4},{cuotas_vencidas:2},{puntualidad_cuotas_vencidas_pct:'10.00'},
    {cuotas:[{...fixture.resumen.cuotas[0],estado:'Pendiente'},fixture.resumen.cuotas[1]]},
    {cuotas:[{...fixture.resumen.cuotas[0],dias_atraso:3},fixture.resumen.cuotas[1]]}]) assert.throws(()=>validarCredito({...fixture,resumen:{...fixture.resumen,...cambio}}),/contrato/)
  assert.throws(()=>validarCredito({...fixture,pagos:[{id,credito_id:id,cuota_id:cuota1,importe:'1.00',fecha_pago:'2026-10-12'}]}),/contrato/)
  assert.throws(()=>validarAuditoria({items:[{id,credito_id:id,accion:'pago_registrado',responsable:'Demo',fecha:'2026-02-31T10:00:00Z'}],hay_mas:false,limite:20,offset:0}),/contrato/)
})
