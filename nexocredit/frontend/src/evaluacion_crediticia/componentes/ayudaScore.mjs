// Orientación versionada; el resultado definitivo procede de la API.
export const VERSION_REGLAS_ACTUAL = 'reglas-demo-v2'
export const RANGOS_SCORE_DEMO = [
  ['0–499', 'Riesgo Alto. Un buen margen no lo reduce.'],
  ['500–679', 'Riesgo Medio. Si el margen es de $7,000 MXN o menos, sube a Alto.'],
  ['680–1000', 'Riesgo Bajo con margen mayor a $15,000 MXN; Medio con más de $7,000 y hasta $15,000; Alto con $7,000 o menos.'],
]

export const RANGOS_MARGEN_DEMO = [
  ['Hasta $7,000', 'El riesgo final es Alto, con cualquier score.'],
  ['Más de $7,000 y hasta $15,000', 'El riesgo final es al menos Medio; un score de 0–499 conserva Alto.'],
  ['Más de $15,000', 'Se conserva el riesgo del score: Alto, Medio o Bajo. El margen no lo mejora.'],
]
const scoreV1 = [
  ['0–679', 'Reglas anteriores: Medio con margen mayor a $7,000 MXN; Alto con $7,000 o menos.'],
  ['680–1000', 'Reglas anteriores: Bajo con margen mayor a $15,000 MXN; Medio con más de $7,000 y hasta $15,000; Alto con $7,000 o menos.'],
]
const margenV1 = [
  ['Hasta $7,000', 'Riesgo Alto con cualquier score.'],
  ['Más de $7,000 y hasta $15,000', 'Riesgo Medio con cualquier score.'],
  ['Más de $15,000', 'Bajo con score de 680–1000; Medio con score de 0–679.'],
]
export function rangosParaVersion(version = VERSION_REGLAS_ACTUAL) {
  if (version === VERSION_REGLAS_ACTUAL) return { score: RANGOS_SCORE_DEMO, margen: RANGOS_MARGEN_DEMO }
  if (version === 'reglas-demo-v1') return { score: scoreV1, margen: margenV1 }
  return null
}
export function explicarScore(valor, version = VERSION_REGLAS_ACTUAL) {
  if (valor == null || (typeof valor === 'string' && !valor.trim())) {
    return 'Captura un score de 0 a 1000. El riesgo también depende de tu margen mensual.'
  }
  const score = typeof valor === 'string' || typeof valor === 'number' ? Number(valor) : NaN
  if (!Number.isInteger(score) || score < 0 || score > 1000) {
    return 'El score debe ser un número entero entre 0 y 1000.'
  }
  if (version === 'reglas-demo-v1') return score < 680
    ? `Score ${score}: con las reglas anteriores será Medio si el margen supera $7,000 MXN; en otro caso, Alto.`
    : `Score ${score}: con las reglas anteriores será Bajo con margen mayor a $15,000 MXN; Medio con más de $7,000 y hasta $15,000; Alto con $7,000 o menos.`
  if (version !== VERSION_REGLAS_ACTUAL) return 'No hay una guía disponible para esta versión de reglas.'
  if (score < 500) return `Tu score ${score} está en 0–499: riesgo Alto, aunque tengas un buen margen.`
  if (score < 680) return `Tu score ${score} está en 500–679: riesgo Medio; sube a Alto si el margen es de $7,000 MXN o menos.`
  return `Tu score ${score} está en 680–1000: puede dar Bajo. El margen insuficiente puede elevarlo a Medio o Alto.`
}

export function explicarMargen(valor, version = VERSION_REGLAS_ACTUAL) {
  if (valor == null || (typeof valor === 'string' && !valor.trim())) {
    return 'El margen es ingresos menos gastos. Se calcula al evaluar.'
  }
  const margen = typeof valor === 'number' ? valor : NaN
  if (!Number.isFinite(margen)) return 'No hay un margen válido disponible.'
  if (!rangosParaVersion(version)) return 'No hay una guía disponible para esta versión de reglas.'
  if (margen <= 7000) return 'Este margen es de $7,000 MXN o menos: el riesgo final es Alto con cualquier score.'
  if (version === 'reglas-demo-v1') return margen <= 15000
    ? 'Con las reglas anteriores, este margen da riesgo Medio con cualquier score.'
    : 'Con las reglas anteriores, este margen permite Bajo con score de al menos 680; con un score menor corresponde Medio.'
  if (margen <= 15000) return 'Este margen supera $7,000 y no supera $15,000 MXN: el riesgo será Medio o Alto según el score; no puede ser Bajo.'
  return 'Este margen supera $15,000 MXN: no eleva el riesgo del score, pero tampoco lo reduce.'
}
