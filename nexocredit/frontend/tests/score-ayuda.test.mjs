import test from 'node:test'
import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { explicarScore, explicarMargen } from '../src/evaluacion_crediticia/componentes/ayudaScore.mjs'

const { default: ScoreAyuda } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/ScoreAyuda.jsx', import.meta.url))
const { default: EvaluationForm } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/EvaluationForm.jsx', import.meta.url))
const { default: Indicadores } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/IndicadoresEscenario.jsx', import.meta.url))

test('score vacío no se interpreta como cero ni como un riesgo calculado', () => {
  for (const valor of ['', '  ', null, undefined]) {
    assert.match(explicarScore(valor), /Captura un score/)
    assert.match(explicarScore(valor), /también depende de tu margen/)
  }
})

test('de cero a 499 el riesgo del score es Alto y el buen margen no lo reduce', () => {
  for (const valor of [0, '0', 1, '200', 499]) {
    const texto = explicarScore(valor)
    assert.match(texto, new RegExp(`Tu score ${Number(valor)} está en 0–499`))
    assert.match(texto, /riesgo Alto, aunque tengas un buen margen/)
  }
})

test('500 y 679 son Medio y el margen insuficiente sólo puede elevarlo', () => {
  for (const valor of [500, '500', 600, 679]) {
    assert.match(explicarScore(valor), /500–679: riesgo Medio/)
    assert.match(explicarScore(valor), /sube a Alto si el margen es de \$7,000 MXN o menos/)
  }
})

test('680 y 1000 conservan las condiciones estrictas del margen para los tres riesgos', () => {
  for (const valor of [680, '680', 700, 1000]) {
    assert.match(explicarScore(valor), /680–1000: puede dar Bajo/)
    assert.match(explicarScore(valor), /margen insuficiente puede elevarlo a Medio o Alto/)
  }
})

test('score inválido no recibe orientación de clasificación', () => {
  for (const valor of [-1, 1001, 650.5, Infinity, NaN, 'texto', 'Infinity', true, {}, []]) {
    assert.equal(explicarScore(valor), 'El score debe ser un número entero entre 0 y 1000.')
  }
})

test('el formulario conserva ayuda breve accesible sin el desplegable rechazado por el usuario', () => {
  const html = renderToStaticMarkup(createElement(ScoreAyuda, { valor: '700' }))
  assert.match(html, /aria-live="polite"/)
  assert.match(html, /tarjetas «Score capturado» y «Margen disponible»/)
  assert.doesNotMatch(html, /<details|<summary|Qué significa Bajo, Medio o Alto/)
  assert.match(html, /El resultado se confirma al evaluar, no autoriza créditos/)
  assert.doesNotMatch(html, /risk-low|risk-high|probabilidad|300–850|Buró consultado/)
})

test('el campo enlaza su explicación accesible y conserva los siete campos y la validación', () => {
  const form = { rfc: '', ingresos_mensuales: '', gastos_mensuales: '', deuda_actual: '0', pagos_mensuales_creditos: '0', dias_atraso_actual: '0', score_buro_actual: '0' }
  const html = renderToStaticMarkup(createElement(EvaluationForm, { form, busy: false, change: () => {}, submit: () => {} }))
  assert.match(html, /id="score_buro_actual"[^>]*min="0"[^>]*max="1000"[^>]*step="1"[^>]*aria-describedby="score-help score-help-disclaimer"/)
  assert.match(html, /id="score-help"/)
  assert.match(html, /id="score-help-disclaimer"/)
  assert.match(html, /Tu score 0 está en 0–499/)
  assert.equal((html.match(/<input (?!type="checkbox")/g) || []).length, 7)
})

test('el significado del margen conserva exactamente los cortes de la API', () => {
  for (const valor of [-100, 0, 6999.99, 7000]) assert.match(explicarMargen(valor), /riesgo final es Alto con cualquier score/)
  for (const valor of [7000.01, 14000, 15000]) assert.match(explicarMargen(valor), /riesgo será Medio o Alto según el score; no puede ser Bajo/)
  for (const valor of [15000.01, 20000]) assert.match(explicarMargen(valor), /no eleva el riesgo del score, pero tampoco lo reduce/)
  for (const valor of [null, undefined, '']) assert.match(explicarMargen(valor), /Se calcula al evaluar/)
  for (const valor of ['20000', NaN, Infinity, true]) assert.equal(explicarMargen(valor), 'No hay un margen válido disponible.')
})

test('los rangos se explican dentro de las tarjetas de score y margen incluso antes de evaluar', () => {
  const html = renderToStaticMarkup(createElement(Indicadores, { result: null, submitted: { score_buro_actual: '700' } }))
  assert.equal((html.match(/<strong(?: [^>]*)?>—<\/strong>/g) || []).length, 4)
  assert.match(html, /aria-label="Score capturado y significado"/)
  assert.match(html, /<dt>0–499<\/dt>/)
  assert.match(html, /<dt>500–679<\/dt>/)
  assert.match(html, /<dt>680–1000<\/dt>/)
  assert.match(html, /Hasta \$7,000/)
  assert.match(html, /Más de \$7,000 y hasta \$15,000/)
  assert.match(html, /Más de \$15,000/)
  assert.match(html, /Un score de 0–499 siempre da Alto/)
  assert.match(html, /Un score alto no garantiza Bajo/)
  assert.doesNotMatch(html, /Tu score 700|<details|<summary/)
})

test('la lectura de la cifra describe sólo el último escenario y no inventa un score de Buró', () => {
  const html = renderToStaticMarkup(createElement(Indicadores, {
    result: { margen_libre: 20000 }, submitted: { score_buro_actual: '700', ingresos_mensuales: '30000', deuda_actual: '0' },
  }))
  assert.match(html, /Tu score 700 está en 680–1000/)
  assert.match(html, /Este margen supera \$15,000 MXN/)
  assert.match(html, /No es una consulta a Buró/)
  assert.match(html, /no autorizan créditos/)
  assert.doesNotMatch(html, /300–850|score excelente|Buró consultado|risk-low|risk-high/)
})

test('la tarjeta explica ambos rangos sin umbral ambiguo y distingue el ejemplo del resultado', () => {
  const html = renderToStaticMarkup(createElement(Indicadores, { result: null, submitted: null }))
  assert.match(html, /0–499<\/dt><dd>Riesgo Alto/)
  assert.match(html, /500–679<\/dt><dd>Riesgo Medio/)
  assert.match(html, /680–1000<\/dt><dd>Riesgo Bajo con margen mayor a \$15,000 MXN/)
  assert.match(html, /aria-label="Ejemplo ficticio de score y margen"/)
  assert.match(html, /Ejemplo ficticio: margen de \$20,000 MXN/)
  assert.match(html, /500 → Medio/)
  assert.match(html, /700 → Bajo/)
  assert.match(html, /200 → Alto/)
  assert.equal((html.match(/<strong(?: [^>]*)?>—<\/strong>/g) || []).length, 4)
  assert.match(html, /Margen = ingresos − gastos/)
  assert.doesNotMatch(html, /alcanza el umbral|Tu score 500|Tu score 700|<details/)
})

test('un resultado anterior mantiene la guía v1 y uno desconocido no usa v2', () => {
  const anterior = renderToStaticMarkup(createElement(Indicadores, { result: { version_modelo: 'reglas-demo-v1', margen_libre: 20000 }, submitted: { score_buro_actual: '200' } }))
  assert.match(anterior, /No recalculada/)
  assert.match(anterior, /score por sí solo no define Bajo, Medio o Alto/)
  assert.match(anterior, /200 → Medio/)
  assert.doesNotMatch(anterior, /200 → Alto|<dt>0–499/)
  const desconocido = renderToStaticMarkup(createElement(Indicadores, { result: { version_modelo: 'otro', margen_libre: 20000 }, submitted: { score_buro_actual: '200' } }))
  assert.match(desconocido, /No hay una guía disponible/)
  assert.doesNotMatch(desconocido, /<dt>0–499|200 → Alto/)
})
