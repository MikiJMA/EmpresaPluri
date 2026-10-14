import test from 'node:test'
import assert from 'node:assert/strict'
import { createElement as h } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'

const Explicacion = (await cargarComponente(new URL('../src/azure_openai/Explicacion.jsx', import.meta.url))).default
const base = { explicacion: 'Margen mensual de demostración.', fuentes: [], aviso: 'No autoriza créditos.', implementacion: 'demo' }
const render = proveedor => renderToStaticMarkup(h(Explicacion, { estado: { estado: 'lista', data: { ...base, proveedor } } }))

test('Ollama se distingue de Azure y de una plantilla sin IA', () => {
  assert.match(render('ollama'), /Proveedor: Ollama local/)
  assert.match(render('ollama'), /modelo se ejecuta en tu equipo/)
  assert.doesNotMatch(render('ollama'), /consumo de pago en Azure/)
  assert.match(render('azure'), /Proveedor: Azure OpenAI/)
  assert.match(render('azure'), /consumo de pago en Azure/)
  assert.match(render('local'), /no fue generada por un modelo de IA/)
})

test('no afirma un proveedor cuando la generación está pendiente y escapa el texto', () => {
  const html = renderToStaticMarkup(h(Explicacion, { estado: { estado: 'generando' } }))
  assert.match(html, /proveedor seleccionado/)
  assert.doesNotMatch(html, /Proveedor: Azure OpenAI|Proveedor: Ollama/)
  const malicious = renderToStaticMarkup(h(Explicacion, { estado: { estado: 'lista', data: { ...base, proveedor: 'ollama', explicacion: '<script>demo()</script>' } } }))
  assert.match(malicious, /&lt;script&gt;/)
  assert.doesNotMatch(malicious, /<script>/)
})
