import test from 'node:test'
import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { importe, valorCapturado } from '../src/evaluacion_crediticia/componentes/metricasEscenario.mjs'

const cargar = async path => (await cargarComponente(new URL(`../src/${path}.jsx`, import.meta.url))).default
const Indicadores = await cargar('evaluacion_crediticia/componentes/IndicadoresEscenario')
const Resultado = await cargar('evaluacion_crediticia/componentes/EvaluationResult')
const Formulario = await cargar('evaluacion_crediticia/componentes/EvaluationForm')
const Marco = await cargar('interfaz/MarcoAplicacion')
const Tabla = await cargar('evaluacion_crediticia/componentes/TablaHistorial')
const render = (component, props) => renderToStaticMarkup(createElement(component, props))
const form = { rfc: 'AAAA010101AA1', ingresos_mensuales: '30000', gastos_mensuales: '10000', deuda_actual: '0', pagos_mensuales_creditos: '0', dias_atraso_actual: '0', score_buro_actual: '700' }
const result = { id: 'prueba', rfc: form.rfc, margen_libre: 20000, nivel_riesgo_preliminar: 'Bajo', factores: ['Factor devuelto por la API'], mensaje: 'Demostración; requiere revisión humana.', version_modelo: 'reglas-demo-v1', guardado: true, fecha: '2026-09-30T12:00:00Z' }

test('los indicadores no muestran cifras antes de evaluar ni una captura anterior', () => {
  const html = render(Indicadores, { result: null, submitted: form })
  assert.equal((html.match(/<strong>—<\/strong>/g) || []).length, 4)
  assert.doesNotMatch(html, /742|136,800|30,000/)
})

test('los indicadores usan exclusivamente la captura enviada y el margen de la API', () => {
  const html = render(Indicadores, { result, submitted: form })
  assert.match(html, /<strong>700<\/strong>/)
  assert.ok(html.includes(importe(30000)))
  assert.ok(html.includes(importe(20000)))
  assert.ok(html.includes(importe(0)))
})

test('cero capturado y dato ausente permanecen distintos', () => {
  assert.equal(valorCapturado(result, form, 'dias_atraso_actual'), 0)
  assert.equal(valorCapturado(result, {}, 'deuda_actual'), null)
  assert.equal(valorCapturado(result, { deuda_actual: 'incorrecto' }, 'deuda_actual'), null)
  assert.equal(importe(null), '—')
})

test('el resumen mantiene escala demo, factores reales y explicación automática', () => {
  const html = render(Resultado, { result, submitted: form, busy: false, explicacion: { estado: 'generando' } })
  assert.match(html, /700 \/ 1000/)
  assert.match(html, /aria-valuemax="1000" aria-valuenow="700"/)
  assert.match(html, /width:70%/)
  assert.match(html, /Factor devuelto por la API/)
  assert.match(html, /Generando explicación con IA/)
  assert.match(html, /Probabilidad de incumplimiento no disponible/)
  assert.doesNotMatch(html, /v4\.2\.1|742 \/ 850|80\.4%|Historial de pago consistente/)
})

test('la explicación solo aparece para evaluaciones guardadas, no mientras se evalúa', () => {
  for (const props of [{ result: null }, { result: { ...result, guardado: false } }, { result, busy: true }]) {
    assert.doesNotMatch(render(Resultado, { submitted: form, ...props }), /Explicación con Azure OpenAI/)
  }
})

test('el formulario conserva siete entradas, validación y aviso de consumo', () => {
  const html = render(Formulario, { form, busy: false, error: '', change: () => {}, submit: () => {} })
  assert.equal((html.match(/<input /g) || []).length, 7)
  assert.equal((html.match(/required=""/g) || []).length, 7)
  assert.match(html, /id="score_buro_actual"[^>]*max="1000"/)
  assert.match(html, /generará automáticamente una explicación/)
  assert.match(html, /consumo de pago/)
  assert.doesNotMatch(html, /Antigüedad laboral|Nombre completo|300–850/)
})

test('el formulario anuncia errores de forma segura y bloquea la edición mientras guarda', () => {
  const html = render(Formulario, { form, busy: true, error: '<script>error</script>', change: () => {}, submit: () => {} })
  assert.match(html, /<fieldset disabled=""/)
  assert.match(html, /role="alert"/)
  assert.match(html, /&lt;script&gt;/)
  assert.match(html, /Evaluando escenario/)
})

test('el menú conserva secciones implementadas e identidad recibida sin afirmaciones inventadas', () => {
  const html = render(Marco, { user: { nombre: 'Usuario de prueba', roles: ['Analista'] }, seccion: 'evaluacion', onSeccionChange: () => {} })
  for (const id of ['seguimiento', 'evaluacion', 'historial', 'laboratorio', 'documentos']) assert.ok(html.includes(`href="#${id}"`))
  assert.match(html, /Usuario de prueba/)
  assert.match(html, /NexoCredit/)
  assert.doesNotMatch(html, /PluriOne|S\.A\. de C\.V\./i)
  assert.match(html, /aria-current="location"/)
  assert.doesNotMatch(html, /Meridian|Sánchez|AES-256|Cumplimiento normativo vigente/)
})

test('la tabla conserva datos, distintivos y acceso a revisión manual', () => {
  const html = render(Tabla, { items: [result], selected: null, onSelected: () => {} })
  assert.match(html, /AAAA010101AA1/)
  assert.match(html, /risk-low/)
  assert.match(html, /Ver detalle/)
  assert.doesNotMatch(html, /Renata|185,000|disabled=""/)
  assert.match(render(Tabla, { items: [result], selected: 'prueba', onSelected: () => {} }), /disabled=""/)
})
