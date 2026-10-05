import test from 'node:test'
import assert from 'node:assert/strict'
import { crearGeneradorExplicaciones } from '../src/azure_openai/generacion.mjs'

test('deduplica solicitudes simultáneas para la misma evaluación', async () => {
  let calls = 0
  let resolver
  const generar = crearGeneradorExplicaciones(() => {
    calls += 1
    return new Promise(resolve => { resolver = resolve })
  })
  const first = generar('evaluacion-1')
  const second = generar('evaluacion-1')
  assert.equal(first, second)
  await Promise.resolve()
  assert.equal(calls, 1)
  resolver({ explicacion: 'Respuesta simulada' })
  assert.deepEqual(await first, await second)
})

test('reutiliza la explicación completada sin generar nuevo consumo', async () => {
  let calls = 0
  const generar = crearGeneradorExplicaciones(async () => { calls += 1; return 'demo' })
  assert.equal(await generar('evaluacion-1'), 'demo')
  assert.equal(await generar('evaluacion-1'), 'demo')
  assert.equal(calls, 1)
})

test('un error no provoca reintentos automáticos para el mismo id', async () => {
  let calls = 0
  const generar = crearGeneradorExplicaciones(async () => { calls += 1; throw new Error('Timeout simulado') })
  await assert.rejects(generar('evaluacion-1'), /Timeout simulado/)
  await assert.rejects(generar('evaluacion-1'), /Timeout simulado/)
  assert.equal(calls, 1)
})

test('una evaluación diferente obtiene su propia explicación', async () => {
  const calls = []
  const generar = crearGeneradorExplicaciones(async id => { calls.push(id); return id })
  const first = generar('evaluacion-1')
  const second = generar('evaluacion-2')
  assert.notEqual(first, second)
  assert.deepEqual(await Promise.all([first, second]), ['evaluacion-1', 'evaluacion-2'])
  assert.deepEqual(calls, ['evaluacion-1', 'evaluacion-2'])
})

test('sin evaluación guardada no llama al servicio', async () => {
  let calls = 0
  const generar = crearGeneradorExplicaciones(() => { calls += 1 })
  await assert.rejects(generar(null), /Falta la evaluación guardada/)
  assert.equal(calls, 0)
})
