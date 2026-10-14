import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { formatearPesos } from '../src/interfaz/moneda.mjs'
import { importe } from '../src/evaluacion_crediticia/componentes/metricasEscenario.mjs'

test('los resúmenes MXN muestran pesos enteros sin cambiar el número original', () => {
  const valor = 18333.33
  assert.equal(formatearPesos(valor), '$18,333')
  assert.equal(importe(valor), '$18,333')
  assert.equal(formatearPesos(18333.67), '$18,334')
  assert.equal(formatearPesos('50000.50'), '$50,001')
  assert.equal(valor, 18333.33)
  assert.equal(formatearPesos(valor, { decimales: 2 }), '$18,333.33')
})

test('cero no equivale a ausencia y los detalles exactos mantienen centavos', () => {
  assert.equal(formatearPesos(0), '$0')
  assert.equal(formatearPesos(null, { sinDatos: 'Sin datos' }), 'Sin datos')
  for (const valor of [null, undefined, '', ' ', true, {}, Infinity, NaN]) assert.equal(formatearPesos(valor), '—')
  assert.equal(formatearPesos('0.10', { decimales: 2 }), '$0.10')
  assert.equal(formatearPesos(-100.25), '-$100')
})

test('dashboard redondea sólo al mostrar y no cambia captura, pagos ni métricas de fuentes', async () => {
  const source = await readFile(new URL('../src/dashboard/Dashboard.jsx', import.meta.url), 'utf8')
  assert.match(source, /formatearPesos\(value, \{ sinDatos: 'Sin datos' \}\)/)
  assert.match(source, /cálculos y datos guardados conservan centavos/)
  const form = await readFile(new URL('../src/evaluacion_crediticia/componentes/EvaluationForm.jsx', import.meta.url), 'utf8')
  assert.match(form, /step="0.01"/)
  const pagos = await readFile(new URL('../src/seguimiento_crediticio/DetalleCredito.jsx', import.meta.url), 'utf8')
  assert.match(pagos, /step="0.01"/)
  const fuentes = await readFile(new URL('../src/datos_financieros/servicio.mjs', import.meta.url), 'utf8')
  assert.match(fuentes, /maximumFractionDigits: 4/)
})
