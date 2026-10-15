import { formatearPesos } from '../../interfaz/moneda.mjs'

export function valorCapturado(result, submitted, name) {
  if (!result || submitted?.[name] == null || submitted[name] === '') return null
  const value = Number(submitted[name])
  return Number.isFinite(value) ? value : null
}

export function importe(value) {
  return formatearPesos(value)
}
