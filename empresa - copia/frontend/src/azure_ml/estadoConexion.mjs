// El estado /estado comprueba configuración, no la conexión con Azure.
// Una consulta correcta acredita únicamente la respuesta de esa sesión.
export function mensajeConexionAzureML(configurado, mensajeConfiguracion, consulta = 'pendiente') {
  if (configurado !== true) return mensajeConfiguracion
  if (consulta === 'consultando') return 'Consultando Azure ML. Espera la respuesta del servicio…'
  if (consulta === 'correcta') return 'Conexión con Azure ML comprobada en esta sesión. Última consulta completada correctamente.'
  if (consulta === 'fallida') return 'No se completó la última consulta a Azure ML. No hay una predicción disponible para ese intento.'
  return mensajeConfiguracion
}

export function esPrediccionAzureML(data) {
  return data !== null && typeof data === 'object' && !Array.isArray(data)
    && typeof data.incumplimiento_predicho === 'boolean'
    && data.origen === 'Azure Machine Learning' && data.modo === 'academico'
    && typeof data.modelo_configurado === 'string' && data.modelo_configurado.trim().length > 0
    && typeof data.advertencia === 'string' && data.advertencia.trim().length > 0
}
