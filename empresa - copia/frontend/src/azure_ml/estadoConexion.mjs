// El estado /estado comprueba configuración, no la conexión con Azure.
// Una consulta correcta acredita únicamente la respuesta de esa sesión.
export function mensajeConexionAzureML(configurado, mensajeConfiguracion, consulta = 'pendiente', proveedor = 'azure') {
  if (configurado !== true) return mensajeConfiguracion
  if (proveedor === 'local') {
    if (consulta === 'consultando') return 'Ejecutando el modelo local. No se consulta Azure…'
    if (consulta === 'correcta') return 'Inferencia local completada correctamente en esta sesión. Sin consulta Azure.'
    if (consulta === 'fallida') return 'No se completó la inferencia local. No hay una predicción disponible para ese intento.'
    return mensajeConfiguracion
  }
  if (consulta === 'consultando') return 'Consultando Azure ML. Espera la respuesta del servicio…'
  if (consulta === 'correcta') return 'Conexión con Azure ML comprobada en esta sesión. Última consulta completada correctamente.'
  if (consulta === 'fallida') return 'No se completó la última consulta a Azure ML. No hay una predicción disponible para ese intento.'
  return mensajeConfiguracion
}

export const COLUMNAS_UCI = ['LIMIT_BAL', 'PAY_0', ...Array.from({ length: 5 }, (_, i) => `PAY_${i + 2}`),
  ...Array.from({ length: 6 }, (_, i) => `BILL_AMT${i + 1}`), ...Array.from({ length: 6 }, (_, i) => `PAY_AMT${i + 1}`)]

export function construirEscenario(valores) {
  if (!valores || Object.keys(valores).length !== 19) throw new Error('Captura las 19 variables UCI.')
  const salida = {}
  for (const name of COLUMNAS_UCI) {
    if (typeof valores[name] !== 'string' || !/^-?\d+$/.test(valores[name])) throw new Error('Los 19 valores deben ser enteros; ningún campo puede quedar vacío.')
    const value = Number(valores[name])
    if (!Number.isSafeInteger(value) || value < -2147483648 || value > 2147483647
      || (name === 'LIMIT_BAL' && value <= 0) || (name.startsWith('PAY_AMT') && value < 0)
      || (name.startsWith('PAY_') && !name.startsWith('PAY_AMT') && (value < -2 || value > 9))) {
      throw new Error('Revisa los límites de las variables UCI.')
    }
    salida[name] = value
  }
  return { valores: salida }
}

export function metricasValidas(m) {
  if (!m || !Number.isInteger(m.filas) || m.filas !== 5955) return false
  for (const key of ['auc', 'exactitud', 'sensibilidad', 'precision', 'f1', 'baseline_exactitud']) {
    if (typeof m[key] !== 'number' || !Number.isFinite(m[key]) || m[key] < 0 || m[key] > 1) return false
  }
  if (!Array.isArray(m.matriz_confusion) || m.matriz_confusion.length !== 2
    || m.matriz_confusion.some(row => !Array.isArray(row) || row.length !== 2 || row.some(n => !Number.isInteger(n) || n < 0))) return false
  const [[tn, fp], [fn, tp]] = m.matriz_confusion
  return tn + fp + fn + tp === m.filas && tp + fn > 0
    && Math.abs(m.exactitud - (tn + tp) / m.filas) < 1e-9 && Math.abs(m.sensibilidad - tp / (tp + fn)) < 1e-9
}

const texto = value => typeof value === 'string' && value.trim().length > 0 && value.length <= 1000
const sha = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value)

export function validarEstadoML(data) {
  if (!data || typeof data.configurado !== 'boolean' || !['azure', 'local', 'deshabilitado'].includes(data.proveedor)
    || !Array.isArray(data.columnas) || data.columnas.length !== 19 || data.columnas.some((n, i) => n !== COLUMNAS_UCI[i])) throw new Error('El estado del laboratorio no tiene un contrato válido.')
  if (data.proveedor === 'local' && data.configurado && (!sha(data.modelo_sha256) || !texto(data.modelo_configurado)
    || data.origen !== 'scikit-learn local' || !metricasValidas(data.metricas_prueba))) throw new Error('No se pudo validar el modelo local ni sus métricas.')
  return data
}

export function esPrediccionML(data, estado) {
  if (!estado?.configurado) return false
  if (estado.proveedor === 'azure') return esPrediccionAzureML(data) && data.proveedor === 'azure'
  return estado.proveedor === 'local' && data !== null && typeof data === 'object' && !Array.isArray(data)
    && typeof data.incumplimiento_predicho === 'boolean' && data.proveedor === 'local'
    && data.origen === 'scikit-learn local' && data.modo === 'academico' && texto(data.advertencia)
    && sha(data.modelo_sha256) && data.modelo_sha256 === estado.modelo_sha256
    && data.modelo_configurado === estado.modelo_configurado && metricasValidas(data.metricas_prueba)
    && Array.isArray(data.variables_fuera_rango_entrenamiento) && data.variables_fuera_rango_entrenamiento.length <= 19
    && data.variables_fuera_rango_entrenamiento.every(n => COLUMNAS_UCI.includes(n))
    && new Set(data.variables_fuera_rango_entrenamiento).size === data.variables_fuera_rango_entrenamiento.length
}

export function esPrediccionAzureML(data) {
  return data !== null && typeof data === 'object' && !Array.isArray(data)
    && typeof data.incumplimiento_predicho === 'boolean'
    && data.origen === 'Azure Machine Learning' && data.modo === 'academico'
    && typeof data.modelo_configurado === 'string' && data.modelo_configurado.trim().length > 0
    && typeof data.advertencia === 'string' && data.advertencia.trim().length > 0
}
