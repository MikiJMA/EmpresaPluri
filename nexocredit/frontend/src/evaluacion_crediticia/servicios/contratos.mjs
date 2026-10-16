import { esAnalisisMexico } from './modeloMexico.mjs'
const riesgos = ['Bajo', 'Medio', 'Alto']
const estados = ['Pendiente', 'Aprobada', 'Rechazada']
const uuid = value => typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)
const objeto = value => !!value && typeof value === 'object' && !Array.isArray(value)
const texto = (value, max = 4000) => typeof value === 'string' && value.length <= max
const numero = value => typeof value === 'number' && Number.isFinite(value)
const importe = (value, min = 0) => numero(value) && value >= min && value <= 1000000000
const margen = value => importe(value, -1000000000)
const entero = (value, min = 0, max = Number.MAX_SAFE_INTEGER) => Number.isSafeInteger(value) && value >= min && value <= max
function fecha(value) {
  if (typeof value !== 'string') return false
  const partes = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,9})?(Z|[+-]\d{2}:\d{2})$/.exec(value)
  if (!partes) return false
  const [year, month, day, hour, minute, second] = partes.slice(1, 7).map(Number)
  const bisiesto = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)
  const dias = [31, bisiesto ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  const zona = partes[7]
  return year >= 1 && month >= 1 && month <= 12 && day >= 1 && day <= dias[month - 1] &&
    hour <= 23 && minute <= 59 && second <= 59 &&
    (zona === 'Z' || (Number(zona.slice(1, 3)) <= 23 && Number(zona.slice(4)) <= 59)) && Number.isFinite(Date.parse(value))
}
export const esFechaHora = fecha
function comprobar(ok, contexto) {
  if (!ok) throw new Error(`La respuesta de ${contexto} no tiene el formato esperado. Intenta actualizar; no se muestran datos inválidos.`)
}

export function esEvaluacion(data, persistida = true) {
  return objeto(data) && texto(data.rfc, 8192) && margen(data.margen_libre) && riesgos.includes(data.nivel_riesgo_preliminar) &&
    (!persistida || data.modo === 'demostracion') && texto(data.version_modelo, 120) && data.version_modelo.length > 0 && texto(data.mensaje) &&
    Array.isArray(data.factores) && data.factores.length > 0 && data.factores.length <= 30 && data.factores.every(i => texto(i)) &&
    typeof data.guardado === 'boolean' && (!data.guardado || !persistida || (uuid(data.id) && fecha(data.fecha))) &&
    (data.analisis_mexico == null || esAnalisisMexico(data.analisis_mexico))
}
export function validarEvaluacion(data) { comprobar(esEvaluacion(data), 'evaluación'); return data }

export function esFilaHistorial(data) {
  return objeto(data) && texto(data.id, 64) && data.id.length > 0 && fecha(data.fecha) && texto(data.rfc, 8192) &&
    margen(data.margen_libre) && riesgos.includes(data.nivel_riesgo_preliminar)
}
export function validarHistorial(data) {
  comprobar(objeto(data) && Array.isArray(data.items) && data.items.length <= data.limite && data.items.every(i => esEvaluacion(i) && i.guardado && esFilaHistorial(i)) &&
    typeof data.hay_mas === 'boolean' && entero(data.limite, 1, 100) && entero(data.offset, 0, 1000000), 'historial')
  return data
}
export function validarRevision(data) {
  comprobar(objeto(data) && uuid(data.id) && uuid(data.evaluacion_id) && entero(data.version, 1) && estados.includes(data.estado) &&
    texto(data.observaciones, 2000) && texto(data.responsable, 120) && fecha(data.fecha), 'revisión')
  return data
}
export function validarDetalle(data) {
  validarEvaluacion(data)
  const solicitud = data.solicitud
  comprobar(data.guardado && objeto(solicitud) && texto(solicitud.rfc, 8192) && solicitud.rfc === data.rfc &&
    importe(solicitud.ingresos_mensuales) && solicitud.ingresos_mensuales > 0 && importe(solicitud.gastos_mensuales) &&
    entero(solicitud.score_buro_actual, 0, 1000) && ['deuda_actual', 'pagos_mensuales_creditos'].every(k => solicitud[k] == null || importe(solicitud[k])) &&
    (solicitud.dias_atraso_actual == null || entero(solicitud.dias_atraso_actual, 0, 36500)) &&
    estados.includes(data.estado_revision) && entero(data.version_revision) && Array.isArray(data.revisiones), 'detalle')
  data.revisiones.forEach(validarRevision)
  comprobar(data.revisiones.length === data.version_revision &&
    data.revisiones.every((r, index) => r.evaluacion_id === data.id && r.version === data.version_revision - index) &&
    new Set(data.revisiones.map(r => r.id)).size === data.revisiones.length &&
    data.estado_revision === (data.revisiones[0]?.estado ?? 'Pendiente'), 'detalle')
  return data
}
export function validarDashboard(data) {
  comprobar(objeto(data) && ['total', 'bajo', 'medio', 'alto', 'con_deuda_capturada'].every(k => entero(data[k])) &&
    data.bajo + data.medio + data.alto === data.total && data.con_deuda_capturada <= data.total &&
    (data.total === 0 ? data.margen_promedio === null : margen(data.margen_promedio)) &&
    (data.con_deuda_capturada === 0 ? data.deuda_promedio === null : importe(data.deuda_promedio)), 'dashboard')
  return data
}
export function esExplicacion(data) {
  return objeto(data) && texto(data.explicacion) && data.explicacion.trim().length > 0 && texto(data.aviso) && texto(data.implementacion, 128) &&
    ['azure', 'ollama', 'local'].includes(data.proveedor) && typeof data.generada_por_ia === 'boolean' &&
    data.generada_por_ia === (data.proveedor !== 'local') && Array.isArray(data.fuentes) && data.fuentes.length > 0 && data.fuentes.length <= 10 &&
    data.fuentes.every(i => objeto(i) && ['id', 'titulo', 'seccion', 'version', 'fuente'].every(k => texto(i[k], 500)))
}
export function esExplicacionRenderizable(data) {
  return objeto(data) && texto(data.explicacion) && texto(data.aviso) && texto(data.implementacion, 128) &&
    Array.isArray(data.fuentes) && data.fuentes.length <= 10 && data.fuentes.every(i => objeto(i) && ['id', 'titulo', 'seccion', 'version'].every(k => texto(i[k], 500)))
}
export function validarExplicacion(data) { comprobar(esExplicacion(data), 'explicación'); return data }

export async function leerRespuesta(response, validar, contexto) {
  let data
  try { data = await response.json() } catch { throw new Error(`No se pudo leer la respuesta de ${contexto}. Intenta de nuevo.`) }
  if (!response.ok) {
    throw new Error(objeto(data) && texto(data.detail, 1000) && data.detail ? data.detail : `No se pudo completar ${contexto}. Revisa los datos y la conexión.`)
  }
  return validar(data)
}
