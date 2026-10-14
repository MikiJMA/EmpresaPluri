// Solo presentación: el identificador autenticado completo sigue en el registro.
export function presentarResponsable(valor) {
  if (typeof valor !== 'string') return 'No informado'
  const nombre = valor.replace(/\s+\[(?:local:)?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\]\s*$/i, '').trim()
  return nombre || 'No informado'
}
