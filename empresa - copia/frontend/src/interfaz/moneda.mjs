const formatos = [0, 2].map(decimales => new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: decimales, maximumFractionDigits: decimales,
}))
// Solo presentación: nunca calcular ni construir una petición con este texto.
export function formatearPesos(value, { decimales = 0, sinDatos = '—' } = {}) {
  if (value == null || typeof value === 'boolean' || (typeof value === 'string' && !value.trim())) return sinDatos
  if (!['number', 'string'].includes(typeof value) || !Number.isFinite(Number(value))) return sinDatos
  return formatos[decimales === 2 ? 1 : 0].format(Number(value))
}
