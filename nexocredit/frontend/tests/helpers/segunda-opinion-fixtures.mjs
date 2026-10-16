import { COLUMNAS_UCI } from '../../src/azure_ml/estadoConexion.mjs'
import { ejemploUCI } from '../../src/evaluacion_crediticia/servicios/controlSegundaOpinion.mjs'

export const evaluacion = { id: '0ef0fa1b-2248-4125-8f62-c472a001e517', guardado: true, fecha: '2026-10-15T10:00:00Z',
  rfc: 'FICTICIO-NO-ENVIAR', margen_libre: 20000, nivel_riesgo_preliminar: 'Bajo', modo: 'demostracion',
  version_modelo: 'reglas-demo-v2', factores: ['Regla demo'], mensaje: 'No autoriza créditos.' }
export const metricas = { filas: 5955, matriz_confusion: [[3418, 1278], [492, 767]], auc: 0.7150479917676206,
  exactitud: 0.7027707808564232, sensibilidad: 0.6092136616362193, precision: 0.3750611246943765,
  f1: 0.4642857142857143, baseline_exactitud: 0.7885810243492863 }
export const estado = { proveedor: 'local', configurado: true, origen: 'scikit-learn local', columnas: COLUMNAS_UCI,
  modelo_sha256: '259b997587543c3466f665a8b62577465014c2c867ebdbfba61544b2d364b8a4',
  modelo_configurado: 'nexocredit-uci-logistica-v1', metricas_prueba: metricas }
export const modelo = { ...estado, modo: 'academico', incumplimiento_predicho: false,
  advertencia: 'Clasificación académica; no validada para México.', variables_fuera_rango_entrenamiento: [] }
export const respuesta = { evaluacion_id: evaluacion.id, riesgo_por_reglas: 'Bajo', version_reglas: 'reglas-demo-v2',
  modelo, guardada: false, advertencia: 'Escenario independiente no guardado; no cambia el riesgo por reglas.' }
export const valores = { ...ejemploUCI }
export const http = data => ({ ok: true, json: async () => data })
export function pendiente() {
  let resolver, rechazar
  const promesa = new Promise((resolve, reject) => { resolver = resolve; rechazar = reject })
  return { promesa, resolver, rechazar }
}
