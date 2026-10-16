import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { crearServicioValoracion, validarValoracion, validarEstadoValoracion, crearGeneradorValoraciones, crearControlValoracion } from '../src/evaluacion_crediticia/servicios/valoracionIA.mjs'
import { evaluacion, captura, estado, resultado } from './helpers/valoracion-fixtures.mjs'

const copia = v => structuredClone(v)
const espera = () => { let resolver, rechazar; const promesa = new Promise((a, b) => { resolver = a; rechazar = b }); return { promesa, resolver, rechazar } }

test('valoración IA corresponde al UUID, reglas y mismos seis datos guardados, con clase independiente', () => {
  assert.equal(validarValoracion(resultado, evaluacion, captura, estado), resultado)
  for (const cambio of [{ evaluacion_id: '00000000-0000-4000-8000-000000000999' }, { riesgo_por_reglas: 'Medio' },
    { version_reglas: 'v1' }, { reglas_modificadas: true }, { generada_por_ia: false }, { nivel_riesgo_ia: 'Aprobado' },
    { proveedor: 'local' }, { modelo: 'otro' }, { probabilidad: .9 }, { fecha_generacion: '2026-02-30T00:00:00Z' }]) {
    assert.throws(() => validarValoracion({ ...resultado, ...cambio }, evaluacion, captura, estado))
  }
  for (const campo of Object.keys(captura)) {
    const mal = copia(resultado); mal.datos_evaluados[campo] += 1
    assert.throws(() => validarValoracion(mal, evaluacion, captura, estado), campo)
  }
  assert.throws(() => validarValoracion(resultado, evaluacion, { ...captura, deuda_actual: '' }, estado))
})

test('rechaza indicadores falsos, factores inventados, duplicados y recomendaciones decisorias', () => {
  const casos = []
  for (const campo of ['margen_mensual', 'pagos_ingreso', 'deuda_ingreso']) {
    const mal = copia(resultado); mal.datos_evaluados[campo] += 1; casos.push(mal)
  }
  const valor = copia(resultado); valor.factores[0].valor = 900; casos.push(valor)
  casos.push({ ...resultado, factores: [] }, { ...resultado, factores: [resultado.factores[0], resultado.factores[0]] },
    { ...resultado, factores: [{ codigo: 'rfc', etiqueta: 'RFC', valor: 1, unidad: 'MXN' }] },
    { ...resultado, recomendaciones: [{ codigo: 'otorgar_credito', texto: 'Otorgar' }] },
    { ...resultado, recomendaciones: [] })
  for (const mal of casos) assert.throws(() => validarValoracion(mal, evaluacion, captura, estado))
})

test('tolera redondeo de centésimas del servidor sin inventar cero o aceptar cocientes incoherentes', () => {
  const alterno = copia(resultado)
  alterno.datos_evaluados.deuda_actual = 80250
  alterno.datos_evaluados.deuda_ingreso = 2.67
  alterno.factores[0].valor = 2.67
  assert.equal(validarValoracion(alterno, evaluacion, { ...captura, deuda_actual: '80250' }, estado), alterno)
  alterno.datos_evaluados.deuda_ingreso = 2.6
  assert.throws(() => validarValoracion(alterno, evaluacion, { ...captura, deuda_actual: '80250' }, estado))
})

test('el transporte usa GET protegido y POST sin datos privados o variables UCI desde el navegador', async () => {
  const calls = []
  const servicio = crearServicioValoracion(async (url, options) => { calls.push({ url, options }); return Response.json(url.endsWith('/estado') ? estado : resultado) }, 'http://localhost:8080/')
  await servicio.estado(new AbortController().signal)
  assert.deepEqual(await servicio.consultar(evaluacion, captura, estado), resultado)
  assert.equal(calls[0].url, 'http://localhost:8080/api/v1/valoracion-ia/estado')
  assert.equal(calls[1].options.method, 'POST'); assert.equal(calls[1].options.body, undefined)
  assert.match(calls[1].url, new RegExp(evaluacion.id + '/valoracion-ia$'))
  assert.doesNotMatch(JSON.stringify(calls), /DEMO-IA|30000|LIMIT_BAL|RFC|CURP/)
})

test('estado y fallos HTTP/JSON/contrato no muestran un análisis falso', async () => {
  assert.equal(validarEstadoValoracion(estado), estado)
  for (const cambios of [{ conexion_verificada: true }, { proveedor: 'azure' }, { modelo: null }]) {
    assert.throws(() => validarEstadoValoracion({ ...estado, ...cambios }))
  }
  for (const response of [new Response('{}', { status: 503 }), new Response('<html>NO-ENVIAR</html>'), Response.json({ ...resultado, nivel_riesgo_ia: false })]) {
    const servicio = crearServicioValoracion(async () => response, '/')
    await assert.rejects(servicio.consultar(evaluacion, captura, estado))
  }
  const servicio = crearServicioValoracion(() => { throw new Error('No llamar') }, '/')
  await assert.rejects(servicio.consultar({ ...evaluacion, guardado: false }, captura, estado))
  await assert.rejects(servicio.consultar(evaluacion, captura, { ...estado, configurado: false }))
})

test('deduplica inicio automático/StrictMode y no repite fallos sin acción explícita', async () => {
  let llamadas = 0
  const pendiente = espera()
  const generar = crearGeneradorValoraciones(() => { llamadas += 1; return pendiente.promesa })
  const a = generar(evaluacion, captura, estado), b = generar(evaluacion, captura, estado)
  assert.equal(a, b); await Promise.resolve(); assert.equal(llamadas, 1)
  pendiente.resolver(resultado); assert.equal(await a, resultado)
  assert.equal(generar(evaluacion, captura, estado, true), a)
  let fallos = 0
  const conFallo = crearGeneradorValoraciones(() => { fallos += 1; throw new Error('Fallo controlado') })
  await assert.rejects(conFallo(evaluacion, captura, estado))
  await assert.rejects(conFallo(evaluacion, captura, estado)); assert.equal(fallos, 1)
  await assert.rejects(conFallo(evaluacion, captura, estado, true)); assert.equal(fallos, 2)
})

test('control consulta automáticamente tras comprobar configuración, nunca si está deshabilitado', async () => {
  const vistas = [], calls = []
  const control = crearControlValoracion({ evaluacion, captura, emitir: v => vistas.push(v), servicio: { estado: async () => estado },
    generar: async (...args) => { calls.push(args); return resultado } })
  await control.iniciar()
  assert.deepEqual(vistas.map(v => v.estado), ['generando', 'lista'])
  assert.equal(calls.length, 1); assert.equal(calls[0][0], evaluacion); assert.equal(calls[0][1], captura)
  control.cerrar()
  const no = crearControlValoracion({ evaluacion, captura, emitir: v => vistas.push(v), servicio: { estado: async () => ({ ...estado, configurado: false }) },
    generar: () => { throw new Error('No debe inferir') } })
  await no.iniciar(); assert.equal(vistas.at(-1).estado, 'no_disponible'); no.cerrar()
})

test('no muestra respuesta tardía de otro formulario y cerrar aborta comprobación', async () => {
  const pendiente = espera(), vistas = []
  let signal, llamadas = 0
  const control = crearControlValoracion({ evaluacion, captura, emitir: v => vistas.push(v), servicio: { estado: async s => { signal = s; return pendiente.promesa } },
    generar: () => { llamadas += 1 } })
  const carga = control.iniciar(); control.cerrar(); assert.equal(signal.aborted, true)
  pendiente.resolver(estado); await carga; assert.equal(llamadas, 0); assert.equal(vistas.length, 0)
  const inferencia = espera()
  const otro = crearControlValoracion({ evaluacion, captura, emitir: v => vistas.push(v), servicio: { estado: async () => estado }, generar: () => inferencia.promesa })
  const consulta = otro.iniciar(); await Promise.resolve(); otro.cerrar()
  inferencia.resolver(resultado); await consulta
  assert.equal(vistas.at(-1).estado, 'generando')
})

test('fallo conserva reglas y reintento manual no duplica solicitudes pendientes', async () => {
  let llamadas = 0, ultimo
  const control = crearControlValoracion({ evaluacion, captura, emitir: v => { ultimo = v }, servicio: { estado: async () => estado },
    generar: async () => { llamadas += 1; if (llamadas === 1) throw new TypeError('NO-ENVIAR'); return resultado } })
  await control.iniciar(); assert.equal(ultimo.estado, 'error'); assert.doesNotMatch(ultimo.error, /NO-ENVIAR/)
  await Promise.all([control.reintentar(), control.reintentar()])
  assert.equal(llamadas, 2); assert.equal(ultimo.resultado, resultado)
  assert.equal(evaluacion.nivel_riesgo_preliminar, 'Bajo'); control.cerrar()
})

test('App monta IA para la captura persistida y mantiene experimento UCI opcional separado', async () => {
  const app = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8')
  const panel = await readFile(new URL('../src/evaluacion_crediticia/componentes/EvaluationResult.jsx', import.meta.url), 'utf8')
  assert.match(app, /valoracionIA=\{result\?\.guardado && result\?\.id && !busy \? <ValoracionIASolicitud key=\{result.id\}/)
  assert.match(app, /captura=\{submitted\}/); assert.match(app, /crearGeneradorValoraciones\(servicioValoracion.consultar\)/)
  assert.ok(panel.indexOf('&& valoracionIA') < panel.indexOf('&& segundaOpinion'))
  assert.match(panel, /Experimento UCI independiente \(opcional\)/)
})
