const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export async function consultarDetalle(id, signal) {
  const response = await fetch(`${api}/api/v1/evaluaciones/${id}`, { signal: AbortSignal.any([signal, AbortSignal.timeout(15000)]) })
  if (!response.ok) throw new Error('No se pudo cargar el detalle. Cierra y vuelve a intentarlo.')
  return response.json()
}

export async function guardarRevision(id, payload) {
  const response = await fetch(`${api}/api/v1/evaluaciones/${id}/revisiones`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: AbortSignal.timeout(15000) })
  if (!response.ok) {
    const data = await response.json()
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Revisa los campos capturados.')
  }
  return response.json()
}

export async function consultarDashboard(filters, signal) {
  const params = new URLSearchParams()
  for (const key of ['desde', 'hasta', 'riesgo']) if (filters[key]) params.set(key, filters[key])
  const response = await fetch(`${api}/api/v1/dashboard?${params}`, { signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]) })
  if (!response.ok) throw new Error('No se pudo cargar el dashboard. Revisa los filtros y la conexión con PostgreSQL.')
  return response.json()
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

  if (!response.ok) {
    if (response.status === 503 || response.status === 409) {
      const data = await response.json()
      throw new Error(data.detail)
    }
    throw new Error(response.status === 422
      ? 'Revisa el RFC y los valores capturados. La API rechazó los datos.'
      : 'El servicio no pudo completar la evaluación. Intenta de nuevo.')
  }

  return response.json()
}

export async function consultarHistorial(offset, signal) {
  const response = await fetch(`${api}/api/v1/evaluaciones?limite=10&offset=${offset}`, {
    signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]),
  })
  if (!response.ok) throw new Error('No se pudo consultar el historial. Comprueba que PostgreSQL y el backend estén iniciados.')
  return response.json()
}
