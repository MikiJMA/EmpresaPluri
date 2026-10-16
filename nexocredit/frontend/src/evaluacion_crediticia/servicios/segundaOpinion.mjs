import { construirEscenario, esPrediccionML, validarEstadoML } from '../../azure_ml/estadoConexion.mjs'
import { leerRespuesta } from './contratos.mjs'

const esUUID = value => typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)
const clavesRespuesta = ['evaluacion_id', 'riesgo_por_reglas', 'version_reglas', 'modelo', 'guardada', 'advertencia']

export function validarSegundaOpinion(data, evaluacion, estado) {
  const valido = data && typeof data === 'object' && !Array.isArray(data)
    && Object.keys(data).length === clavesRespuesta.length && clavesRespuesta.every(k => Object.hasOwn(data, k))
    && esUUID(data.evaluacion_id) && data.evaluacion_id === evaluacion.id
    && ['Bajo', 'Medio', 'Alto'].includes(data.riesgo_por_reglas)
    && data.riesgo_por_reglas === evaluacion.nivel_riesgo_preliminar
    && data.version_reglas === evaluacion.version_modelo
    && data.guardada === false && typeof data.advertencia === 'string'
    && data.advertencia.trim().length > 0 && data.advertencia.length <= 4000
    && esPrediccionML(data.modelo, estado)
  if (!valido) throw new Error('La segunda opinión no tiene el contrato esperado o corresponde a otra evaluación. No se muestra una predicción inválida.')
  return data
}

// El transporte autenticado se inyecta desde React. No conserva tokens, RFC o importes MXN.
export function crearServicioSegundaOpinion(fetchAutenticado, base) {
  const api = base.replace(/\/$/, '')
  return {
    async consultarEstado(signal) {
      const response = await fetchAutenticado(`${api}/api/v1/ml/estado`, {
        signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]),
      })
      return leerRespuesta(response, validarEstadoML, 'estado del modelo')
    },
    async consultar(evaluacion, valores, estado, signal) {
      if (evaluacion?.guardado !== true || !esUUID(evaluacion.id)) throw new Error('Primero guarda una evaluación válida para consultar la segunda opinión.')
      if (estado?.configurado !== true || !['local', 'azure'].includes(estado.proveedor)) throw new Error('El modelo no está disponible. No se simula una segunda opinión.')
      const payload = construirEscenario(valores)
      const response = await fetchAutenticado(`${api}/api/v1/evaluaciones/${evaluacion.id}/segunda-opinion`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
        signal: AbortSignal.any([signal, AbortSignal.timeout(35000)]),
      })
      return leerRespuesta(response, data => validarSegundaOpinion(data, evaluacion, estado), 'segunda opinión')
    },
  }
}
