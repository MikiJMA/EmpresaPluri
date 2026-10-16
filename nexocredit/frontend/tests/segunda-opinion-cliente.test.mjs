import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { COLUMNAS_UCI } from '../src/azure_ml/estadoConexion.mjs'
import { crearServicioSegundaOpinion, validarSegundaOpinion } from '../src/evaluacion_crediticia/servicios/segundaOpinion.mjs'
import { crearControlSegundaOpinion } from '../src/evaluacion_crediticia/servicios/controlSegundaOpinion.mjs'
import { evaluacion, estado, respuesta, valores, http, pendiente } from './helpers/segunda-opinion-fixtures.mjs'

test('segunda opinión valida exactamente el envelope y la relación con la evaluación guardada', () => {
  assert.equal(validarSegundaOpinion(respuesta, evaluacion, estado), respuesta)
  assert.equal(validarSegundaOpinion({ ...respuesta, modelo: { ...respuesta.modelo, incumplimiento_predicho: true } }, evaluacion, estado).modelo.incumplimiento_predicho, true)
  for (const cambio of [{ evaluacion_id: '0ef0fa1b-2248-4125-8f62-c472a001e518' }, { evaluacion_id: 'mal' },
    { riesgo_por_reglas: 'Medio' }, { riesgo_por_reglas: 'Aprobado' }, { version_reglas: 'reglas-demo-v1' },
    { guardada: true }, { guardada: 'false' }, { advertencia: '' }, { advertencia: 5 }, { adicional: true }]) {
    assert.throws(() => validarSegundaOpinion({ ...respuesta, ...cambio }, evaluacion, estado), /contrato esperado/)
  }
  for (const data of [null, [], {}, { ...respuesta, modelo: null }, { ...respuesta, advertencia: 'a'.repeat(4001) }]) {
    assert.throws(() => validarSegundaOpinion(data, evaluacion, estado), /contrato esperado/)
  }
  const incompleta = { ...respuesta }; delete incompleta.guardada
  assert.throws(() => validarSegundaOpinion(incompleta, evaluacion, estado), /contrato esperado/)
})

test('rechaza clases no booleanas, huellas/modelos distintos y métricas incoherentes', () => {
  for (const cambio of [{ incumplimiento_predicho: 0 }, { incumplimiento_predicho: 'false' }, { proveedor: 'azure' },
    { modelo_sha256: '0'.repeat(64) }, { modelo_configurado: 'otro' }, { variables_fuera_rango_entrenamiento: ['RFC'] },
    { metricas_prueba: { ...estado.metricas_prueba, exactitud: 1 } }]) {
    assert.throws(() => validarSegundaOpinion({ ...respuesta, modelo: { ...respuesta.modelo, ...cambio } }, evaluacion, estado), /contrato esperado/)
  }
})

test('estado es GET sin inferencia y POST contiene sólo las 19 variables enteras independientes', async () => {
  const llamadas = []
  const servicio = crearServicioSegundaOpinion(async (url, opciones) => {
    llamadas.push({ url, opciones }); return http(url.endsWith('/estado') ? estado : respuesta)
  }, 'http://api.local/')
  const signal = new AbortController().signal
  assert.equal(await servicio.consultarEstado(signal), estado)
  assert.equal(llamadas[0].url, 'http://api.local/api/v1/ml/estado')
  assert.equal(llamadas[0].opciones.body, undefined)
  assert.equal(await servicio.consultar(evaluacion, valores, estado, signal), respuesta)
  const { url, opciones } = llamadas[1]
  assert.equal(url, `http://api.local/api/v1/evaluaciones/${evaluacion.id}/segunda-opinion`)
  assert.equal(opciones.method, 'POST')
  assert.equal(opciones.headers['Content-Type'], 'application/json')
  const payload = JSON.parse(opciones.body)
  assert.deepEqual(Object.keys(payload), ['valores'])
  assert.deepEqual(Object.keys(payload.valores), COLUMNAS_UCI)
  assert.equal(payload.valores.LIMIT_BAL, 200000)
  assert.ok(Object.values(payload.valores).every(Number.isInteger))
  assert.doesNotMatch(opciones.body, /FICTICIO-NO-ENVIAR|ingresos_mensuales|score_buro|rfc/i)
  assert.equal(opciones.signal.aborted, false)
})

test('no envía consultas sin evaluación persistida, modelo disponible o datos completos', async () => {
  let llamadas = 0
  const servicio = crearServicioSegundaOpinion(async () => { llamadas += 1; return http(respuesta) }, '/')
  const signal = new AbortController().signal
  for (const evaluada of [null, { ...evaluacion, guardado: false }, { ...evaluacion, id: 'mal' }]) {
    await assert.rejects(servicio.consultar(evaluada, valores, estado, signal), /guarda una evaluación/)
  }
  for (const config of [null, { ...estado, configurado: false }, { ...estado, proveedor: 'deshabilitado' }]) {
    await assert.rejects(servicio.consultar(evaluacion, valores, config, signal), /no está disponible/)
  }
  for (const entrada of [{ ...valores, LIMIT_BAL: '' }, { ...valores, RFC: 'NO-ENVIAR' }, { ...valores, PAY_0: '10' }]) {
    await assert.rejects(servicio.consultar(evaluacion, entrada, estado, signal))
  }
  assert.equal(llamadas, 0)
})

test('HTTP, JSON y contratos inválidos se rechazan y permiten un reintento sin otro guardado', async () => {
  let devolver = { ok: false, json: async () => ({ detail: { privado: 'NO-REFLEJAR' } }) }
  const servicio = crearServicioSegundaOpinion(async () => devolver, '/')
  const signal = new AbortController().signal
  await assert.rejects(servicio.consultar(evaluacion, valores, estado, signal), /No se pudo completar segunda opinión/)
  devolver = { ok: true, json: async () => { throw new Error('NO-REFLEJAR') } }
  await assert.rejects(servicio.consultar(evaluacion, valores, estado, signal), /No se pudo leer/)
  devolver = http({ ...respuesta, evaluacion_id: 'otro' })
  await assert.rejects(servicio.consultar(evaluacion, valores, estado, signal), /otra evaluación/)
  devolver = http(respuesta)
  assert.equal(await servicio.consultar(evaluacion, valores, estado, signal), respuesta)
  devolver = http({ ...estado, columnas: [] })
  await assert.rejects(servicio.consultarEstado(signal), /contrato válido/)
})

test('el controlador sólo comprueba estado al montar; cargar ejemplo no consulta ni modifica la evaluación', async () => {
  const capturada = structuredClone(evaluacion)
  const cambios = []
  let consultas = 0
  const control = crearControlSegundaOpinion({ evaluacion, emitir: v => cambios.push(v), servicio: {
    consultarEstado: async () => estado, consultar: async () => { consultas += 1; return respuesta },
  } })
  await control.iniciar()
  assert.equal(consultas, 0)
  assert.equal(cambios.at(-1).valores.LIMIT_BAL, '')
  control.cargarEjemplo()
  assert.equal(consultas, 0)
  assert.equal(cambios.at(-1).valores.LIMIT_BAL, '200000')
  await control.consultar()
  assert.equal(consultas, 1)
  assert.equal(cambios.at(-1).resultado, respuesta)
  control.cambiar('PAY_0', '1')
  assert.equal(cambios.at(-1).resultado, null)
  assert.equal(cambios.at(-1).consulta, 'pendiente')
  assert.deepEqual(evaluacion, capturada)
  control.cerrar()
})

test('el controlador bloquea doble clic y cambios mientras consulta', async () => {
  const espera = pendiente()
  let ultimo, llamadas = 0
  const control = crearControlSegundaOpinion({ evaluacion, emitir: v => { ultimo = v }, servicio: {
    consultarEstado: async () => estado, consultar: async () => { llamadas += 1; return espera.promesa },
  } })
  await control.iniciar(); control.cargarEjemplo()
  const envio = control.consultar()
  await control.consultar(); control.cambiar('LIMIT_BAL', '1'); control.cargarEjemplo()
  assert.equal(llamadas, 1)
  assert.equal(ultimo.busy, true)
  assert.equal(ultimo.valores.LIMIT_BAL, '200000')
  espera.resolver(respuesta); await envio
  assert.equal(ultimo.busy, false)
  assert.equal(ultimo.resultado, respuesta)
  control.cerrar()
})

test('un fallo no borra la evaluación, no muestra resultado anterior y permite reintentar', async () => {
  let ultimo, fallo = true
  const control = crearControlSegundaOpinion({ evaluacion, emitir: v => { ultimo = v }, servicio: {
    consultarEstado: async () => estado,
    consultar: async () => { if (fallo) throw new TypeError('Detalle privado NO-REFLEJAR'); return respuesta },
  } })
  await control.iniciar(); control.cargarEjemplo(); await control.consultar()
  assert.equal(ultimo.busy, false); assert.equal(ultimo.resultado, null)
  assert.equal(ultimo.valores.LIMIT_BAL, '200000')
  assert.match(ultimo.error, /evaluación guardada no cambia/)
  assert.doesNotMatch(ultimo.error, /NO-REFLEJAR/)
  fallo = false; await control.consultar()
  assert.equal(ultimo.resultado, respuesta); assert.equal(ultimo.error, '')
  control.cerrar()
})

test('al desmontar aborta y descarta la respuesta de la evaluación anterior aunque el transporte ignore abort', async () => {
  const espera = pendiente()
  let signal, emisiones = 0
  const control = crearControlSegundaOpinion({ evaluacion, emitir: () => { emisiones += 1 }, servicio: {
    consultarEstado: async () => estado, consultar: async (_evaluacion, _valores, _estado, s) => { signal = s; return espera.promesa },
  } })
  await control.iniciar(); control.cargarEjemplo()
  const envio = control.consultar()
  const antes = emisiones; control.cerrar()
  assert.equal(signal.aborted, true)
  espera.resolver(respuesta); await envio
  await control.consultar(); control.cargarEjemplo(); control.cambiar('PAY_0', '1')
  assert.equal(emisiones, antes)
})

test('descarta también un estado tardío y permite recuperar una comprobación de proveedor fallida', async () => {
  const espera = pendiente()
  let signal, emisiones = 0
  const control = crearControlSegundaOpinion({ evaluacion, emitir: () => { emisiones += 1 }, servicio: {
    consultarEstado: async s => { signal = s; return espera.promesa },
  } })
  const carga = control.iniciar(); control.cerrar(); assert.equal(signal.aborted, true)
  espera.resolver(estado); await carga; assert.equal(emisiones, 0)
  let ultimo, falla = true
  const recuperable = crearControlSegundaOpinion({ evaluacion, emitir: v => { ultimo = v }, servicio: {
    consultarEstado: async () => { if (falla) throw new TypeError('NO-REFLEJAR'); return estado },
  } })
  await recuperable.iniciar(); assert.equal(ultimo.estado, null); assert.equal(ultimo.comprobando, false)
  falla = false; await recuperable.comprobar()
  assert.equal(ultimo.estado, estado); assert.equal(ultimo.error, '')
  recuperable.cerrar()
})

test('App monta la segunda opinión únicamente tras guardar y su key resetea por UUID', async () => {
  const app = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8')
  const componente = await readFile(new URL('../src/evaluacion_crediticia/componentes/SegundaOpinionModelo.jsx', import.meta.url), 'utf8')
  assert.match(app, /result\?\.guardado && result\?\.id && !busy \? <SegundaOpinionModelo key=\{result.id\}/)
  assert.match(componente, /fetchAutenticado/)
  assert.match(componente, /instancia\.cerrar\(\)/)
  assert.doesNotMatch(componente, /localStorage|sessionStorage|console\.|API_KEY|\.password/)
})
