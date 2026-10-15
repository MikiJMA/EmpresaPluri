import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { COLUMNAS_UCI, construirEscenario, esPrediccionML, validarEstadoML, mensajeConexionAzureML } from '../src/azure_ml/estadoConexion.mjs'

// Fixture pública de las métricas registradas; el frontend se construye sin archivos backend.
const artefacto = { modelo_id: 'nexocredit-uci-logistica-v1', metricas: { prueba: {
  filas: 5955, matriz_confusion: [[3418, 1278], [492, 767]], auc: 0.7150479917676206,
  exactitud: 0.7027707808564232, sensibilidad: 0.6092136616362193, precision: 0.3750611246943765,
  f1: 0.4642857142857143, baseline_exactitud: 0.7885810243492863,
} } }
const { default: Panel } = await cargarComponente(new URL('../src/azure_ml/PanelLaboratorio.jsx', import.meta.url))
const modeloSha = '259b997587543c3466f665a8b62577465014c2c867ebdbfba61544b2d364b8a4'
const estado = { proveedor: 'local', configurado: true, origen: 'scikit-learn local', columnas: COLUMNAS_UCI,
  modelo_sha256: modeloSha, modelo_configurado: artefacto.modelo_id, metricas_prueba: artefacto.metricas.prueba }
const result = { ...estado, modo: 'academico', incumplimiento_predicho: false, advertencia: 'Académico, no autoriza créditos.', variables_fuera_rango_entrenamiento: [] }
const valores = Object.fromEntries(COLUMNAS_UCI.map(n => [n, n === 'LIMIT_BAL' ? '200000' : '0']))
const render = overrides => renderToStaticMarkup(createElement(Panel, { values: valores, estado, status: 'Artefacto presente; consulta pendiente.', consulta: 'pendiente', busy: false, error: '', result: null, submit: () => {}, change: () => {}, cargarEjemplo: () => {}, ...overrides }))

test('el cliente UCI no convierte campos vacíos en cero ni acepta MXN/RFC como predictores', () => {
  assert.equal(construirEscenario(valores).valores.LIMIT_BAL, 200000)
  for (const value of ['', '1.2', 'NaN', true, '2147483648']) assert.throws(() => construirEscenario({ ...valores, BILL_AMT1: value }))
  assert.throws(() => construirirExtra())
  assert.throws(() => construirEscenario({ ...valores, PAY_0: '10' }))
  assert.throws(() => construirEscenario({ ...valores, PAY_AMT1: '-1' }))
  assert.throws(() => construirEscenario({ ...valores, LIMIT_BAL: '0' }))
  assert.equal(construirEscenario({ ...valores, BILL_AMT1: '-1' }).valores.BILL_AMT1, -1)
})
function construirirExtra() { return construirEscenario({ ...valores, RFC: 'NO-ENVIAR' }) }

test('la predicción local exige huella y modelo coherentes, clase booleana y métricas reales', () => {
  assert.equal(validarEstadoML(estado), estado)
  assert.equal(esPrediccionML(result, estado), true)
  assert.equal(esPrediccionML({ ...result, incumplimiento_predicho: true }, estado), true)
  for (const cambio of [{ origen: 'Azure Machine Learning' }, { proveedor: 'azure' }, { modelo_sha256: '0'.repeat(64) },
    { modelo_configurado: 'otro' }, { modo: 'produccion' }, { incumplimiento_predicho: 0 }, { advertencia: '' },
    { metricas_prueba: { ...result.metricas_prueba, exactitud: 1 } }, { variables_fuera_rango_entrenamiento: ['RFC'] }]) {
    assert.equal(esPrediccionML({ ...result, ...cambio }, estado), false)
  }
  assert.throws(() => validarEstadoML({ ...estado, modelo_sha256: '' }))
  assert.throws(() => validarEstadoML({ ...estado, columnas: [...COLUMNAS_UCI].reverse() }))
  assert.equal(esPrediccionML(result, { ...estado, configurado: false }), false)
})

test('los mensajes locales sólo anuncian inferencia tras consulta correcta y nunca atribuyen conexión Azure', () => {
  for (const consulta of ['pendiente', 'consultando', 'correcta', 'fallida']) {
    const mensaje = mensajeConexionAzureML(true, 'Consulta local pendiente.', consulta, 'local')
    assert.doesNotMatch(mensaje, /Conexión con Azure ML comprobada/)
    if (consulta === 'correcta') assert.match(mensaje, /Inferencia local completada/)
    else assert.doesNotMatch(mensaje, /completada correctamente/)
  }
})

test('el panel local conserva 19 entradas, NTD, límites y métricas con baseline sin inventar mejor precisión', () => {
  const html = render()
  assert.match(html, /IA local · scikit-learn/)
  assert.equal((html.match(/<input /g) || []).length, 19)
  assert.match(html, /Consultar IA local/)
  assert.match(html, /Taiwán, 2005/)
  assert.match(html, /NTD/)
  assert.match(html, /AUC: 0.715/)
  assert.match(html, /Sensibilidad: 60.9%/)
  assert.match(html, /Exactitud: 70.3%/)
  assert.match(html, /78.9%/)
  assert.doesNotMatch(html, /32 %|No incumplimiento<\/h3>/)
})

test('resultados, errores y extrapolación se muestran con procedencia, sin guardado ni HTML ejecutable', () => {
  const html = render({ result: { ...result, advertencia: '<script>texto</script>', variables_fuera_rango_entrenamiento: ['LIMIT_BAL'] } })
  assert.match(html, /Clase predicha: No incumplimiento/)
  assert.match(html, /fuera de los rangos observados/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script>/)
  assert.match(html, /no se guarda en PostgreSQL/)
  assert.match(render({ busy: true }), /<fieldset disabled=""/)
  assert.match(render({ error: 'Fallo controlado', result: null }), /role="alert"/)
})

test('el modo Azure sigue disponible y el cliente usa ruta autenticada neutral con guarda de intentos', async () => {
  const html = render({ estado: { proveedor: 'azure', configurado: true, columnas: COLUMNAS_UCI } })
  assert.match(html, /Consultar modelo en Azure/)
  assert.doesNotMatch(html, /Sensibilidad: 60.9/)
  const source = await readFile(new URL('../src/azure_ml/AzureMLDemo.jsx', import.meta.url), 'utf8')
  assert.match(source, /fetchAutenticado as fetch/)
  assert.match(source, /\/api\/v1\/ml\/predecir/)
  assert.match(source, /intentoActual.current !== intento/)
  assert.match(source, /peticion.current\?\.abort\(\)/)
  assert.doesNotMatch(source, /localStorage|sessionStorage|AZURE_ML_API_KEY|\/api\/v1\/evaluaciones/)
})
