import assert from 'node:assert/strict'
import test from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { vistaInicialSegundaOpinion } from '../src/evaluacion_crediticia/servicios/controlSegundaOpinion.mjs'
import { evaluacion, estado, respuesta, valores } from './helpers/segunda-opinion-fixtures.mjs'

const Panel = (await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/PanelSegundaOpinion.jsx', import.meta.url))).default
const Resultado = (await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/EvaluationResult.jsx', import.meta.url))).default
const vista = { ...vistaInicialSegundaOpinion(), estado, comprobando: false, valores }
const render = cambios => renderToStaticMarkup(createElement(Panel, { evaluacion, vista: { ...vista, ...cambios }, cambiar: () => {}, cargarEjemplo: () => {}, consultar: () => {}, comprobar: () => {} }))

test('panel ofrece 19 entradas sin duplicar ids del laboratorio, ejemplo manual y botón explícito', () => {
  const html = render()
  assert.equal((html.match(/<input /g) || []).length, 19)
  assert.equal((html.match(/required=""/g) || []).length, 19)
  assert.match(html, /id="segunda-opinion-LIMIT_BAL"/)
  assert.doesNotMatch(html, /id="uci-/)
  assert.match(html, /Cargar ejemplo UCI ficticio/)
  assert.match(html, /Consultar segunda opinión/)
  assert.match(html, /Reglas demo/)
  assert.match(html, /Sin consulta/)
  assert.doesNotMatch(html, /Modelo académico: No incumplimiento/)
})

test('panel distingue NTD y MXN, contexto UCI independiente y ausencia de validación crediticia', () => {
  const html = render()
  for (const texto of [/No evalúa a este solicitante/, /Taiwán, 2005/, /NTD/, /no MXN/, /sin llaves ni suscripción Azure/,
    /no consulta, guarda ni modifica la evaluación/, /No es una validación para México ni una probabilidad calibrada/,
    /no cambia las reglas demo y no se guarda en el expediente/]) assert.match(html, texto)
})

test('resultado muestra ambas salidas con origen y avisos, sin traducir clase en riesgo MXN', () => {
  const html = render({ resultado: respuesta, consulta: 'correcta' })
  assert.match(html, /Reglas demo: Bajo · Modelo académico: No incumplimiento/)
  assert.match(html, /scikit-learn local/)
  assert.match(html, /nexocredit-uci-logistica-v1/)
  assert.match(html, /no guardado/)
  assert.match(html, /Inferencia local completada/)
  assert.doesNotMatch(html, /Probabilidad:|Riesgo del modelo: Bajo/)
  const extrapolada = render({ resultado: { ...respuesta, modelo: { ...respuesta.modelo, variables_fuera_rango_entrenamiento: ['LIMIT_BAL'] } } })
  assert.match(extrapolada, /Fuera de los rangos observados/)
})

test('proveedor Azure conserva advertencia de consumo y la clase puede diferir de las reglas', () => {
  const azure = { ...estado, proveedor: 'azure', origen: 'Azure Machine Learning' }
  const resultado = { ...respuesta, modelo: { ...respuesta.modelo, proveedor: 'azure', origen: 'Azure Machine Learning', incumplimiento_predicho: true } }
  const html = render({ estado: azure, resultado })
  assert.match(html, /Reglas demo: Bajo · Modelo académico: Incumplimiento/)
  assert.match(html, /puede generar consumo de pago/)
  assert.match(html, /no se envían los datos MXN/)
  assert.doesNotMatch(html, /sin llaves ni suscripción Azure/)
})

test('consulta bloqueada sin configuración y durante petición; errores y avisos se escapan', () => {
  for (const cambios of [{ estado: null }, { estado: { ...estado, configurado: false } }, { busy: true }, { comprobando: true }]) {
    assert.match(render(cambios), /<button type="submit" disabled=""/)
  }
  assert.match(render({ busy: true }), /<fieldset disabled=""/)
  const html = render({ error: '<script>no ejecutar</script>', resultado: { ...respuesta, advertencia: '<script>aviso</script>' } })
  assert.match(html, /role="alert"/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script>/)
})

test('resultado principal sólo incluye la segunda opinión cuando la evaluación está guardada', () => {
  const nodo = createElement('p', null, 'SEGUNDA-OPINION-CONTROLADA')
  const renderResultado = props => renderToStaticMarkup(createElement(Resultado, { result: evaluacion, busy: false, segundaOpinion: nodo, ...props }))
  assert.match(renderResultado({}), /SEGUNDA-OPINION-CONTROLADA/)
  for (const props of [{ result: null }, { busy: true }, { result: { ...evaluacion, guardado: false } }, { result: { ...evaluacion, factores: null } }]) {
    assert.doesNotMatch(renderResultado(props), /SEGUNDA-OPINION-CONTROLADA/)
  }
})
