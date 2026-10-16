import assert from 'node:assert/strict'
import test from 'node:test'
import { renderToStaticMarkup } from 'react-dom/server'
import React from 'react'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { evaluacion, estado, resultado, vista } from './helpers/valoracion-fixtures.mjs'

const { default: Panel } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/PanelValoracionIA.jsx', import.meta.url))
const render = v => renderToStaticMarkup(React.createElement(Panel, { evaluacion, vista: v, reintentar() {} }))

test('muestra los mismos datos MXN y diferencia una valoración generativa de las reglas y del modelo UCI', () => {
  const html = render(vista)
  assert.match(html, /mismos datos guardados/); assert.match(html, /Valoración IA: Medio/)
  assert.match(html, /reglas difieren/); assert.match(html, /no predicción estadística/)
  assert.match(html, /Deuda \/ ingreso mensual/); assert.match(html, /llama3.1:8b/)
  assert.doesNotMatch(html, /LIMIT_BAL|PAY_AMT|NTD|90%/)
})

test('anuncia generación automática sin clasificación inventada y permite reintento sólo al terminar', () => {
  const busy = render({ ...vista, estado: 'generando', resultado: null })
  assert.match(busy, /aria-busy="true"/); assert.match(busy, /Analizando…/)
  assert.doesNotMatch(busy, /Volver a intentar/)
  const no = render({ ...vista, estado: 'no_disponible', configuracion: { ...estado, configurado: false, motivo: 'Modelo no disponible.' }, resultado: null })
  assert.match(no, /No disponible/); assert.match(no, /Modelo no disponible/); assert.match(no, /Volver a intentar/)
})

test('escapa resultados y errores; sin probabilidades, decisiones o borrado del historial', () => {
  const html = render({ ...vista, resultado: { ...resultado, aviso: '<script>NO-EJECUTAR</script>' }, error: '<img src=x onerror=alert(1)>' })
  assert.match(html, /&lt;script&gt;/); assert.match(html, /&lt;img/)
  assert.doesNotMatch(html, /<script|<img/)
  assert.match(html, /no es consulta de Buró/); assert.match(html, /24 horas/)
})
