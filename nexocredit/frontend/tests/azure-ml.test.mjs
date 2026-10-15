import assert from 'node:assert/strict'
import test from 'node:test'
import { esPrediccionAzureML, mensajeConexionAzureML } from '../src/azure_ml/estadoConexion.mjs'

const pendiente = 'Configuración presente; conexión pendiente de una consulta correcta.'
const respuesta = {
  incumplimiento_predicho: false, origen: 'Azure Machine Learning', modo: 'academico',
  modelo_configurado: 'candidato-demo:1', advertencia: 'Clasificación académica, no autorización de crédito.',
}

test('la configuración por sí sola no afirma una conexión comprobada', () => {
  assert.equal(mensajeConexionAzureML(true, pendiente), pendiente)
  assert.equal(mensajeConexionAzureML(true, pendiente, 'estado-desconocido'), pendiente)
})

test('sin configuración mantiene el mensaje inicial aunque reciba un estado de consulta', () => {
  for (const configurado of [false, undefined, 'true']) {
    assert.equal(mensajeConexionAzureML(configurado, 'Azure ML no está configurado.', 'correcta'), 'Azure ML no está configurado.')
  }
  assert.equal(mensajeConexionAzureML(false, 'Comprobando configuración…'), 'Comprobando configuración…')
})

test('durante la consulta muestra espera sin afirmar un resultado correcto', () => {
  const message = mensajeConexionAzureML(true, pendiente, 'consultando')
  assert.match(message, /Consultando Azure ML/)
  assert.doesNotMatch(message, /comprobada|correctamente|pendiente de una consulta/)
})

test('una consulta correcta sustituye el aviso pendiente y limita la evidencia a la sesión', () => {
  const message = mensajeConexionAzureML(true, pendiente, 'correcta')
  assert.match(message, /Conexión con Azure ML comprobada en esta sesión/)
  assert.match(message, /Última consulta completada correctamente/)
  assert.doesNotMatch(message, /pendiente|modelo verificado|producción|probabilidad/)
})

test('el último intento fallido deja de anunciar éxito y no muestra una predicción anterior', () => {
  const states = ['pendiente', 'consultando', 'correcta', 'consultando', 'fallida']
  const messages = states.map(state => mensajeConexionAzureML(true, pendiente, state))
  assert.match(messages[2], /comprobada/)
  assert.match(messages.at(-1), /No se completó la última consulta/)
  assert.match(messages.at(-1), /No hay una predicción disponible/)
  assert.doesNotMatch(messages.at(-1), /comprobada|correctamente/)
})

test('ambas clases booleanas de Azure ML son respuestas correctas', () => {
  assert.equal(esPrediccionAzureML(respuesta), true)
  assert.equal(esPrediccionAzureML({ ...respuesta, incumplimiento_predicho: true }), true)
})

test('una respuesta vacía o una clase no booleana no acredita éxito', () => {
  for (const data of [null, undefined, [], {}, 'false', { ...respuesta, incumplimiento_predicho: 'false' },
    { ...respuesta, incumplimiento_predicho: 0 }, { ...respuesta, incumplimiento_predicho: 0.7 }]) {
    assert.equal(esPrediccionAzureML(data), false)
  }
})

test('el resultado conserva procedencia, modo académico y advertencia sin verificar la etiqueta del modelo', () => {
  for (const change of [{ origen: 'Simulación' }, { modo: 'produccion' }, { modelo_configurado: '' },
    { modelo_configurado: '  ' }, { advertencia: null }, { advertencia: '' }]) {
    assert.equal(esPrediccionAzureML({ ...respuesta, ...change }), false)
  }
  assert.equal(esPrediccionAzureML({ ...respuesta, modelo_configurado: 'otra-etiqueta:2' }), true)
})
