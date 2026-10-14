import { fetchAutenticado as fetch } from '../../autenticacion/cliente'
import { leerRespuesta, validarEvaluacion, validarHistorial, validarDetalle, validarRevision, validarDashboard } from './contratos.mjs'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export async function consultarDetalle(id, signal) {
  const response = await fetch(`${api}/api/v1/evaluaciones/${id}`, { signal: AbortSignal.any([signal, AbortSignal.timeout(15000)]) })
  return leerRespuesta(response, validarDetalle, 'detalle')
}

export async function guardarRevision(id, payload) {
  const response = await fetch(`${api}/api/v1/evaluaciones/${id}/revisiones`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: AbortSignal.timeout(15000) })
  return leerRespuesta(response, validarRevision, 'revisión')
}

export async function consultarDashboard(filters, signal) {
  const params = new URLSearchParams()
  for (const key of ['desde', 'hasta', 'riesgo']) if (filters[key]) params.set(key, filters[key])
  const response = await fetch(`${api}/api/v1/dashboard?${params}`, { signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]) })
  return leerRespuesta(response, validarDashboard, 'dashboard')
}

/** Cliente HTTP de evaluación: envía el escenario y conserva los errores de validación. */
export async function evaluarCredito(form, clave) {
  const response = await fetch(`${api}/api/v1/evaluar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': clave },
    signal: AbortSignal.timeout(15000),
    body: JSON.stringify({
      ...form,
      ingresos_mensuales: Number(form.ingresos_mensuales),
      gastos_mensuales: Number(form.gastos_mensuales),
      score_buro_actual: Number(form.score_buro_actual),
      deuda_actual: Number(form.deuda_actual),
      pagos_mensuales_creditos: Number(form.pagos_mensuales_creditos),
      dias_atraso_actual: Number(form.dias_atraso_actual),
    }),
  })

  return leerRespuesta(response, validarEvaluacion, 'evaluación')
}

export async function consultarHistorial(offset, signal) {
  const response = await fetch(`${api}/api/v1/evaluaciones?limite=10&offset=${offset}`, {
    signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]),
  })
  return leerRespuesta(response, validarHistorial, 'historial')
}
