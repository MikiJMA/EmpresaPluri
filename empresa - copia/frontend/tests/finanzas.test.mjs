import assert from 'node:assert/strict'
import test from 'node:test'
import { createElement as h } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { crearServicioFinanciero, validarIndicadores, formatearValor, formatearPeriodo } from '../src/datos_financieros/servicio.mjs'
import { cargarComponente } from './helpers/cargar-componente.mjs'

const Panel = (await cargarComponente(new URL('../src/datos_financieros/PanelFinanciero.jsx', import.meta.url))).default
const payload = () => ({ pais: 'MX', aviso: 'No modifica el riesgo.', cache_segundos: 3600, proveedores: [
  { id: 'banxico', nombre: 'Banco de México', estado: 'sin_configurar', mensaje: 'Falta configurar Banxico.',
    consulta_utc: '2026-09-30T10:00:00+00:00', proxima_consulta_utc: '2026-09-30T10:01:00+00:00', en_cache: false, indicadores: [] },
  { id: 'banco_mundial', nombre: 'Banco Mundial', estado: 'disponible', mensaje: 'Últimos datos disponibles.',
    consulta_utc: '2026-09-30T10:00:00+00:00', proxima_consulta_utc: '2026-09-30T11:00:00+00:00', en_cache: true,
    indicadores: ['FP.CPI.TOTL.ZG', 'NY.GDP.MKTP.KD.ZG'].map((serie, i) => ({ serie,
      nombre: i === 0 ? 'Inflación de México' : 'Crecimiento del PIB de México', unidad: '% anual', frecuencia: 'Anual',
      valor: i === 0 ? 3.8 : -0.5, periodo: '2025', estado: 'disponible', fuente_url: `https://data.worldbank.org/indicator/${serie}?locations=MX` })) },
] })
const render = overrides => renderToStaticMarkup(h(Panel, { estado: 'lista', data: payload(), reintentar() {}, ...overrides }))

test('fuentes independientes: Banxico pendiente no oculta indicadores del Banco Mundial', () => {
  const html = render()
  assert.ok(html.includes('Requiere configuración'))
  assert.ok(html.includes('Inflación de México'))
  assert.ok(html.includes('3.80'))
  assert.ok(html.includes('-0.50'))
  assert.ok(html.includes('Año 2025'))
  assert.ok(html.includes('% anual'))
  assert.ok(html.includes('Fuente · FP.CPI.TOTL.ZG'))
  assert.ok(html.includes('no cambian el riesgo'))
  assert.ok(html.includes('UTC'))
  assert.ok(html.includes('Respuesta conservada en caché'))
  assert.ok(html.includes('no fuerza llamadas externas'))
})

test('carga y fallo de la aplicación no muestran valores anteriores', () => {
  const loading = render({ estado: 'cargando' })
  assert.ok(loading.includes('role="status"'))
  assert.ok(loading.includes('disabled=""'))
  assert.ok(!loading.includes('3.80'))
  const error = render({ estado: 'error', error: 'No hay conexión.' })
  assert.ok(error.includes('role="alert"'))
  assert.ok(error.includes('Volver a consultar'))
  assert.ok(!error.includes('3.80'))
})

test('ausencia no es cero, negativos conservan su signo y fechas no cambian por zona horaria', () => {
  assert.equal(formatearValor(null), 'Sin dato')
  assert.equal(formatearValor(0), '0.00')
  assert.equal(formatearValor(-0.5), '-0.50')
  assert.ok(formatearPeriodo('2026-09-30').includes('30'))
  const data = payload()
  data.proveedores[1].estado = 'parcial'
  data.proveedores[1].indicadores[0].valor = null
  data.proveedores[1].indicadores[0].estado = 'sin_dato'
  data.proveedores[1].indicadores[1].valor = 0
  const html = render({ data })
  assert.ok(html.includes('Sin dato'))
  assert.ok(html.includes('0.00'))
  assert.ok(html.includes('Datos parciales'))
})

test('el cliente usa solamente el backend autenticado sin enviar el escenario ni secretos', async () => {
  const calls = []
  const service = crearServicioFinanciero(async (url, options) => {
    calls.push({ url, options }); return { ok: true, json: async () => payload() }
  }, 'http://localhost:8000/')
  const signal = new AbortController().signal
  assert.equal((await service(signal)).proveedores.length, 2)
  assert.equal(calls[0].url, 'http://localhost:8000/api/v1/datos-financieros/indicadores')
  assert.deepEqual(calls[0].options, { method: 'GET', signal })
  assert.ok(!JSON.stringify(calls).includes('rfc'))
  assert.ok(!JSON.stringify(calls).includes('Bmx-Token'))
})

test('respuestas incompletas, país ajeno, series duplicadas y enlaces externos son rechazados', () => {
  const changes = [
    data => { data.pais = 'US' },
    data => { data.proveedores.pop() },
    data => { data.proveedores[1] = data.proveedores[0] },
    data => { data.proveedores[1].indicadores[0].valor = NaN },
    data => { data.proveedores[1].indicadores[0].valor = '3.8' },
    data => { data.proveedores[1].indicadores[0].valor = true },
    data => { data.proveedores[1].indicadores[0].periodo = null },
    data => { data.proveedores[1].indicadores[0].estado = 'sin_dato' },
    data => { data.proveedores[1].indicadores[0].fuente_url = 'javascript:alert(1)' },
    data => { data.proveedores[1].indicadores[0].serie = 'otra' },
    data => { data.proveedores[1].indicadores[1] = data.proveedores[1].indicadores[0] },
    data => { data.proveedores[1].consulta_utc = 'ayer' },
    data => { data.proveedores[1].estado = 'error' },
  ]
  assert.equal(validarIndicadores(payload()).pais, 'MX')
  for (const change of changes) { const data = payload(); change(data); assert.throws(() => validarIndicadores(data), /formato esperado/) }
  for (const data of [null, {}, [], { pais: 'MX' }]) assert.throws(() => validarIndicadores(data), /formato esperado/)
})

test('errores de HTTP/JSON y cancelación se manejan sin reenviar contenido del proveedor', async () => {
  const failing = crearServicioFinanciero(async () => ({ ok: false, json: async () => ({ detail: 'secreto' }) }), '')
  await assert.rejects(failing(), /No se pudieron consultar/)
  const invalid = crearServicioFinanciero(async () => ({ ok: true, json: async () => { throw new Error('privado') } }), '')
  await assert.rejects(invalid(), /formato esperado/)
  const aborted = crearServicioFinanciero(async () => { throw new DOMException('Cancelada', 'AbortError') }, '')
  await assert.rejects(aborted(), { name: 'AbortError' })
})

test('texto del proveedor se escapa y las fuentes conservan atributos seguros', () => {
  const data = payload(); data.proveedores[1].mensaje = '<script>error()</script>'
  const html = render({ data })
  assert.ok(html.includes('&lt;script&gt;'))
  assert.ok(!html.includes('<script>'))
  assert.ok(html.includes('rel="noopener noreferrer"'))
})
