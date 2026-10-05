import assert from 'node:assert/strict'
import test from 'node:test'
import { createElement as h } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { agruparGuias, crearServicioDocumentos } from '../src/azure_search/servicio.mjs'
import { cargarComponente } from './helpers/cargar-componente.mjs'

const Panel = (await cargarComponente(new URL('../src/azure_search/PanelDocumentos.jsx', import.meta.url))).default
const fragmento = (seccion = 'DEM-01', fuente = 'guia-demo') => ({ id: `${fuente}-${seccion}`, fuente,
  titulo: 'Guía de demostración', seccion, contenido: 'Contenido original de la guía.', version: '1.0', aviso: 'Material demo. No autoriza créditos.' })
const props = { consulta: '', onConsultaChange: () => {}, submit: () => {}, busy: false, error: '', resultados: null,
  catalogo: { estado: 'lista', fragmentos: [fragmento()] }, reintentar: () => {} }
const render = overrides => renderToStaticMarkup(h(Panel, { ...props, ...overrides }))

test('muestra las guías sin buscar y mantiene el buscador arriba', () => {
  const html = render()
  assert.ok(html.includes('Contenido original de la guía.'))
  assert.ok(html.includes('Fuente: guia-demo · versión 1.0'))
  assert.ok(html.includes('Leer guía · 1 sección'))
  assert.ok(html.indexOf('consulta-documentos') < html.indexOf('Guías disponibles'))
  assert.ok(!html.includes('Resultados de búsqueda'))
})

test('agrupa por fuente y versión y conserva todas las secciones ordenadas', () => {
  const docs = [fragmento('DEM-02'), fragmento('DEM-01'), fragmento('ALC-01', 'alcance-demo'),
    { ...fragmento('DEM-03'), version: '2.0' }]
  const guias = agruparGuias(docs)
  assert.equal(guias.length, 3)
  assert.deepEqual(guias[0].secciones.map(item => item.seccion), ['DEM-01', 'DEM-02'])
  assert.equal(guias.reduce((sum, guia) => sum + guia.secciones.length, 0), 4)
  assert.ok(render({ catalogo: { estado: 'lista', fragmentos: docs } }).includes('3 guías · 4 secciones'))
})

test('carga, fallo recuperable y catálogo vacío tienen mensajes visibles', () => {
  assert.ok(render({ catalogo: { estado: 'cargando' } }).includes('Cargando las guías desde Azure AI Search'))
  const error = render({ catalogo: { estado: 'error', error: 'No hay conexión.' } })
  assert.ok(error.includes('role="alert"'))
  assert.ok(error.includes('Reintentar carga de guías'))
  assert.ok(!error.includes('Contenido original de la guía.'))
  assert.ok(render({ catalogo: { estado: 'lista', fragmentos: [] } }).includes('Todavía no hay guías disponibles'))
})

test('la búsqueda conserva el catálogo y maneja cero coincidencias', () => {
  const html = render({ consulta: 'margen', resultados: [] })
  assert.ok(html.includes('No se encontraron coincidencias'))
  assert.ok(html.includes('Guías disponibles'))
  assert.ok(html.includes('Contenido original'))
  assert.ok(render({ busy: true }).includes('Buscando fragmentos en Azure AI Search'))
})

test('contenido y errores se muestran como texto, nunca HTML ejecutable', () => {
  const html = render({ error: '<script>error()</script>', catalogo: { estado: 'lista',
    fragmentos: [{ ...fragmento(), contenido: '<img src=x onerror=alert(1)>' }] } })
  assert.ok(html.includes('&lt;img'))
  assert.ok(html.includes('&lt;script&gt;'))
  assert.ok(!html.includes('<script>') && !html.includes('<img '))
})

test('cliente usa GET autenticado para el catálogo y POST solo para buscar', async () => {
  const calls = []
  const fetchApi = async (url, options) => { calls.push({ url, options }); return { ok: true, json: async () => ({ resultados: [fragmento()] }) } }
  const servicio = crearServicioDocumentos(fetchApi, 'http://localhost:8000/')
  const controller = new AbortController()
  assert.equal((await servicio.listar(controller.signal)).length, 1)
  await servicio.buscar('  margen  ', controller.signal)
  assert.equal(calls[0].url, 'http://localhost:8000/api/v1/azure-search/documentos')
  assert.equal(calls[0].options.method, 'GET')
  assert.equal(calls[0].options.signal, controller.signal)
  assert.equal(calls[0].options.body, undefined)
  assert.equal(calls[1].options.method, 'POST')
  assert.deepEqual(JSON.parse(calls[1].options.body), { consulta: 'margen' })
  assert.ok(calls.every(call => !call.url.includes('azure-openai')))
})

test('cliente propaga errores y rechaza respuestas de formato inválido', async () => {
  const servicio = payload => crearServicioDocumentos(async () => ({ ok: true, json: async () => payload }), '/api')
  for (const payload of [{}, { resultados: [null] }, { resultados: [{}] }]) {
    await assert.rejects(servicio(payload).listar(), /formato esperado/)
  }
  const denegado = crearServicioDocumentos(async () => ({ ok: false, json: async () => ({ detail: 'Acceso denegado.' }) }), '/api')
  await assert.rejects(denegado.listar(), /Acceso denegado/)
  const abortado = crearServicioDocumentos(async () => { throw new DOMException('Cancelada', 'AbortError') }, '/api')
  await assert.rejects(abortado.listar(), { name: 'AbortError' })
})
