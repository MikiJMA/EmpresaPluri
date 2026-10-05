const pesos = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' })

export function valorCapturado(result, submitted, name) {
  if (!result || submitted?.[name] == null || submitted[name] === '') return null
  const value = Number(submitted[name])
  return Number.isFinite(value) ? value : null
}

export function importe(value) {
  return value == null || !Number.isFinite(Number(value)) ? '—' : pesos.format(Number(value))
}
