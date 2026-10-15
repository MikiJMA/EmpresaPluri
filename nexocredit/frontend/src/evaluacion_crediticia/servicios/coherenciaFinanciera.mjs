// Validación de captura, no reglas de riesgo ni verificación de datos reales.
export function erroresFinancieros(form) {
  const leer = key => {
    const value = form[key]
    if (typeof value !== 'number' && typeof value !== 'string') return null
    if (typeof value === 'string' && !value.trim()) return null
    const number = Number(value)
    return Number.isFinite(number) && number >= 0 ? number : null
  }
  const gastos = leer('gastos_mensuales')
  const pagos = leer('pagos_mensuales_creditos')
  const deuda = leer('deuda_actual')
  const atraso = leer('dias_atraso_actual')
  const errores = []
  if (pagos !== null && gastos !== null && pagos > gastos) errores.push('Los pagos de créditos no pueden superar los gastos mensuales, que deben incluirlos.')
  if (deuda === 0 && atraso !== null && atraso > 0) errores.push('Si existe atraso pendiente, la deuda actual debe ser mayor que cero.')
  return errores
}
