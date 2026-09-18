const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

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
