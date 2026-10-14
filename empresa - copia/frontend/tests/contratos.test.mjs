import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { validarEvaluacion, validarHistorial, validarDetalle, validarRevision, validarDashboard, validarExplicacion, leerRespuesta } from '../src/evaluacion_crediticia/servicios/contratos.mjs'

const id='0ef0fa1b-2248-4125-8f62-c472a001e517'
const result={id,fecha:'2026-10-11T10:00:00Z',rfc:'DEMO',margen_libre:20000,nivel_riesgo_preliminar:'Bajo',modo:'demostracion',version_modelo:'reglas-demo-v1',factores:['Regla demo'],mensaje:'No autoriza créditos.',guardado:true}
const revision={id,evaluacion_id:id,version:1,estado:'Pendiente',observaciones:'Ficticio',responsable:'Analista',fecha:result.fecha}
const history={items:[result],hay_mas:false,limite:10,offset:0}
const dashboard={total:1,bajo:1,medio:0,alto:0,con_deuda_capturada:0,margen_promedio:20000,deuda_promedio:null}
const Result=(await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/EvaluationResult.jsx',import.meta.url))).default
const Table=(await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/TablaHistorial.jsx',import.meta.url))).default
const Boundary=(await cargarComponente(new URL('../src/interfaz/ErrorRecuperable.jsx',import.meta.url))).default

test('evaluación valida solo números finitos, riesgo demo, factores y metadatos persistidos',()=>{
  assert.equal(validarEvaluacion(result),result)
  for(const value of [null,{}, {...result,factores:null},{...result,factores:{}},{...result,nivel_riesgo_preliminar:'APROBADO_REAL'},{...result,margen_libre:Infinity},{...result,fecha:'mal'},{...result,id:'mal'},{...result,guardado:'true'}]) assert.throws(()=>validarEvaluacion(value),/formato esperado/)
  assert.equal(validarEvaluacion({...result,guardado:false,id:undefined,fecha:undefined}).guardado,false)
})
test('historial rechaza ausencia de items, filas nulas, fecha inválida y paginación excesiva',()=>{
  assert.equal(validarHistorial(history),history)
  for(const value of [null,{}, {...history,items:{}},{...history,items:[null]},{...history,items:[{...result,fecha:'incorrecta'}]},{...history,offset:1000001}]) assert.throws(()=>validarHistorial(value),/formato esperado/)
})
test('detalle y revisión validan solicitud y relación de sus revisiones sin cambiar el legado demo',()=>{
  assert.equal(validarRevision(revision),revision)
  const detail={...result,solicitud:{rfc:'DEMO',ingresos_mensuales:30000,gastos_mensuales:10000,score_buro_actual:700},revisiones:[revision],estado_revision:'Pendiente',version_revision:1}
  assert.equal(validarDetalle(detail),detail)
  for(const value of [{...detail,solicitud:null},{...detail,revisiones:[null]},{...detail,revisiones:[{...revision,evaluacion_id:'0ef0fa1b-2248-4125-8f62-c472a001e518'}]}]) assert.throws(()=>validarDetalle(value),/formato esperado/)
})
test('dashboard conserva ausencia distinta de cero y rechaza tipos o conteos imposibles',()=>{
  assert.equal(validarDashboard(dashboard),dashboard)
  assert.equal(validarDashboard({...dashboard,con_deuda_capturada:1,deuda_promedio:0}).deuda_promedio,0)
  for(const value of [null,{}, {...dashboard,bajo:2},{...dashboard,total:true},{...dashboard,margen_promedio:'20000'},{...dashboard,con_deuda_capturada:2}]) assert.throws(()=>validarDashboard(value),/formato esperado/)
})

test('fechas exigen calendario real, hora válida y zona explícita sin normalizar febrero',()=>{
  for(const fecha of ['2026-02-31T10:00:00Z','2025-02-29T10:00:00Z','1900-02-29T10:00:00Z','2026-04-31T10:00:00Z',
    '2026-00-10T10:00:00Z','2026-01-00T10:00:00Z','0000-01-01T10:00:00Z','2026-10-11T24:00:00Z',
    '2026-10-11T10:60:00Z','2026-10-11T10:00:60Z','2026-10-11T10:00:00','2026-10-11T10:00:00+24:00',
    '2026-10-11T10:00:00+00:60','2026-10-11T10:00:00Zextra']) {
    assert.throws(()=>validarEvaluacion({...result,fecha}),/formato esperado/,fecha)
    assert.throws(()=>validarRevision({...revision,fecha}),/formato esperado/,fecha)
  }
  for(const fecha of ['2024-02-29T23:59:59Z','2000-02-29T00:00:00+00:00','2026-10-11T10:00:00.123456+00:00',
    '2026-10-11T04:00:00-06:00','0099-01-01T00:00:00Z']) assert.equal(validarEvaluacion({...result,fecha}).fecha,fecha)
})

test('contratos acotan importes al rango del servidor y admiten margen negativo',()=>{
  for(const margen_libre of [-1000000000,0,1000000000]) assert.equal(validarEvaluacion({...result,margen_libre}).margen_libre,margen_libre)
  for(const margen_libre of [1e308,1000000001,-1000000001,true]) assert.throws(()=>validarEvaluacion({...result,margen_libre}),/formato esperado/)
  const detail={...result,solicitud:{rfc:'DEMO',ingresos_mensuales:30000,gastos_mensuales:10000,score_buro_actual:700},revisiones:[],estado_revision:'Pendiente',version_revision:0}
  for(const changes of [{ingresos_mensuales:0},{ingresos_mensuales:1e308},{gastos_mensuales:-1},{deuda_actual:-1},{pagos_mensuales_creditos:1e308}]) {
    assert.throws(()=>validarDetalle({...detail,solicitud:{...detail.solicitud,...changes}}),/formato esperado/)
  }
  // No exigir las reglas de captura nuevas a solicitudes históricas conservadas.
  assert.equal(validarDetalle({...detail,solicitud:{...detail.solicitud,deuda_actual:0,pagos_mensuales_creditos:20000,dias_atraso_actual:30}}).version_revision,0)
})

test('detalle exige RFC coherente y estado/versión correspondientes al historial completo',()=>{
  const older={...revision,id:'0ef0fa1b-2248-4125-8f62-c472a001e516'}
  const latest={...revision,version:2,estado:'Aprobada'}
  const detail={...result,solicitud:{rfc:'DEMO',ingresos_mensuales:30000,gastos_mensuales:10000,score_buro_actual:700},revisiones:[latest,older],estado_revision:'Aprobada',version_revision:2}
  assert.equal(validarDetalle(detail),detail)
  for(const value of [{...detail,solicitud:{...detail.solicitud,rfc:'OTRO'}},{...detail,version_revision:99},
    {...detail,estado_revision:'Pendiente'},{...detail,revisiones:[older,latest]},{...detail,revisiones:[latest]},
    {...detail,revisiones:[latest,{...older,id:latest.id}]},{...detail,revisiones:[],version_revision:0}]) assert.throws(()=>validarDetalle(value),/formato esperado/)
  const empty={...detail,revisiones:[],version_revision:0,estado_revision:'Pendiente'}
  assert.equal(validarDetalle(empty),empty)
})

test('dashboard distingue cero, ausencia y falta de cobertura sin aceptar promedios inventados',()=>{
  const empty={total:0,bajo:0,medio:0,alto:0,con_deuda_capturada:0,margen_promedio:null,deuda_promedio:null}
  assert.equal(validarDashboard(empty),empty)
  for(const value of [{...empty,margen_promedio:20000},{...empty,deuda_promedio:0},
    {...dashboard,deuda_promedio:50000},{...dashboard,margen_promedio:null},
    {...dashboard,con_deuda_capturada:1,deuda_promedio:null},{...dashboard,margen_promedio:1e308},
    {...dashboard,con_deuda_capturada:1,deuda_promedio:-1}]) assert.throws(()=>validarDashboard(value),/formato esperado/)
  assert.equal(validarDashboard({...dashboard,margen_promedio:-500}).margen_promedio,-500)
})
test('explicación exige texto, referencias y proveedor coherentes sin inventar IA',()=>{
  const data={explicacion:'Texto demo',aviso:'Demo',implementacion:'modelo-demo',proveedor:'ollama',generada_por_ia:true,fuentes:[{id:'demo-02',titulo:'Guía demo',fuente:'guia-demostracion-v1',seccion:'DEM-02',version:'1.0'}]}
  assert.equal(validarExplicacion(data),data)
  for(const value of [null,{}, {...data,fuentes:null},{...data,fuentes:[null]},{...data,generada_por_ia:false},{...data,proveedor:'SAT'}]) assert.throws(()=>validarExplicacion(value),/formato esperado/)
})
test('la interfaz informa que el texto se conserva y distingue vigencia de borrado',async()=>{
  const Explanation=(await cargarComponente(new URL('../src/azure_openai/Explicacion.jsx',import.meta.url))).default
  const html=renderToStaticMarkup(createElement(Explanation,{estado:{estado:'generando'}}))
  assert.match(html,/caché privada de PostgreSQL/)
  assert.match(html,/Vencer no los borra automáticamente/)
  assert.match(html,/diez nuevos intentos/)
})
test('HTTP y JSON inesperados generan un mensaje legible sin reflejar objetos privados',async()=>{
  await assert.rejects(leerRespuesta({ok:true,json:async()=>({})},validarEvaluacion,'evaluación'),/formato esperado/)
  await assert.rejects(leerRespuesta({ok:false,json:async()=>({detail:{privado:'NO-REFLEJAR'}})},validarEvaluacion,'evaluación'),/No se pudo completar/)
  await assert.rejects(leerRespuesta({ok:false,json:async()=>{throw new Error('<html>privado</html>')}},validarEvaluacion,'evaluación'),/No se pudo leer/)
})
test('componentes muestran avisos recuperables en lugar de lanzar map o mostrar riesgos inventados',()=>{
  for(const value of [{},{...result,factores:null},{...result,factores:{}},{...result,nivel_riesgo_preliminar:'APROBADO_REAL'}]){
    const html=renderToStaticMarkup(createElement(Result,{result:value,busy:false}))
    assert.match(html,/role="alert"/)
    assert.doesNotMatch(html,/APROBADO_REAL/)
  }
  for(const items of [null,{},[null],[{...result,fecha:'incorrecta'}]]){
    const html=renderToStaticMarkup(createElement(Table,{items}))
    assert.match(html,/role="alert"/)
    assert.doesNotMatch(html,/Invalid Date/)
  }
})
test('Error Boundary tiene recuperación explícita, sin borrar datos ni registrar payloads',async()=>{
  const boundary=new Boundary({children:'Contenido'})
  assert.equal(boundary.render(),'Contenido')
  boundary.state=Boundary.getDerivedStateFromError(new Error('NO-REFLEJAR'))
  const html=renderToStaticMarkup(boundary.render())
  assert.match(html,/Recargar aplicación/)
  assert.match(html,/ya guardados no se eliminan/)
  assert.doesNotMatch(html,/NO-REFLEJAR/)
  const main=await readFile(new URL('../src/main.jsx',import.meta.url),'utf8')
  assert.match(main,/<ErrorRecuperable><Acceso>/)
})
test('cliente HTTP real rechaza resultados falsos antes de devolverlos a App',async t=>{
  const old=globalThis.qaCreditoFetch
  t.after(()=>{globalThis.qaCreditoFetch=old})
  const path=new URL('../src/evaluacion_crediticia/servicios/creditApi.js',import.meta.url)
  const contrato=new URL('../src/evaluacion_crediticia/servicios/contratos.mjs',import.meta.url).href
  const source=(await readFile(path,'utf8')).replace("import { fetchAutenticado as fetch } from '../../autenticacion/cliente'",'const fetch = (...args) => globalThis.qaCreditoFetch(...args)').replace('import.meta.env.VITE_API_URL',"'/'").replace("'./contratos.mjs'",JSON.stringify(contrato))
  const client=await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`)
  globalThis.qaCreditoFetch=async()=>({ok:true,json:async()=>({})})
  await assert.rejects(client.evaluarCredito({rfc:'DEMO'},id),/formato esperado/)
  await assert.rejects(client.consultarHistorial(0,new AbortController().signal),/formato esperado/)
  globalThis.qaCreditoFetch=async()=>({ok:true,json:async()=>result})
  assert.equal(await client.evaluarCredito({rfc:'DEMO'},id),result)
})
