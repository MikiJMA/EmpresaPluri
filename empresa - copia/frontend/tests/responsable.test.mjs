import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { presentarResponsable } from '../src/evaluacion_crediticia/componentes/presentarResponsable.mjs'

test('presentación sin UUID local o Microsoft, preservando nombres antiguos', () => {
  const id = '1c798d2a-c36e-49c6-9891-896057f5ca97'
  assert.equal(presentarResponsable(`julian [local:${id}]`), 'julian')
  assert.equal(presentarResponsable(`Analista demo [${id}]`), 'Analista demo')
  assert.equal(presentarResponsable('Analista [turno 2]'), 'Analista [turno 2]')
  assert.equal(presentarResponsable('Nombre declarado'), 'Nombre declarado')
  assert.equal(presentarResponsable(null), 'No informado')
})

test('el cambio es visual; se conserva el responsable completo en el envío y no se atribuye todo a Microsoft', async () => {
  const source = await readFile(new URL('../src/evaluacion_crediticia/componentes/EvaluationDetail.jsx', import.meta.url), 'utf8')
  assert.ok(source.includes('responsable: user.responsable'))
  assert.ok(source.includes('retry.current ||= { ...form'))
  assert.ok(source.includes('value={user.nombre || presentarResponsable(form.responsable)}'))
  assert.ok(source.includes('presentarResponsable(r.responsable)'))
  assert.ok(source.includes('Las nuevas revisiones usan tu cuenta autenticada'))
  assert.ok(!source.includes('identidad verificada con Microsoft'))
})
