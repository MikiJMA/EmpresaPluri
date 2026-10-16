export const tiposCredito = [
  ['departamental', 'Tarjeta departamental'], ['bancaria', 'Tarjeta bancaria'], ['nomina', 'Crédito de nómina'],
  ['personal', 'Crédito personal'], ['automotriz', 'Crédito automotriz'], ['vivienda', 'Crédito de vivienda'],
  ['grupal', 'Crédito grupal'], ['aplicacion', 'Préstamo por aplicación'], ['otro', 'Otro crédito formal'],
]
export function perfilMexicoVacio() {
  return { ingreso_laboral: '', periodicidad: '', ingreso_variable: '', presupuesto: '', gastos_cubiertos: '', ahorro_emergencia: '', creditos: [] }
}
export function prepararPerfilMexico(perfil) {
  if (perfil == null) return null
  const campos = ['ingreso_laboral', 'periodicidad', 'ingreso_variable', 'presupuesto', 'gastos_cubiertos', 'ahorro_emergencia']
  if (campos.some(campo => perfil[campo] === '' || perfil[campo] == null)) throw new Error('Completa las preguntas del modelo mexicano o desactívalo. No se sustituyen respuestas por cero.')
  if (!Array.isArray(perfil.creditos) || !perfil.creditos.length ||
      new Set(perfil.creditos).size !== perfil.creditos.length ||
      perfil.creditos.some(c => !tiposCredito.some(([tipo]) => tipo === c))) throw new Error('Selecciona al menos un crédito formal para el modelo mexicano.')
  const resultado = Object.fromEntries(campos.map(campo => [campo, Number(perfil[campo])]))
  if (!Number.isFinite(resultado.ingreso_laboral) || resultado.ingreso_laboral <= 0 || resultado.ingreso_laboral > 98000 ||
      Object.entries({ periodicidad: 4, ingreso_variable: 2, presupuesto: 2, gastos_cubiertos: 2, ahorro_emergencia: 5 })
        .some(([campo, max]) => !Number.isInteger(resultado[campo]) || resultado[campo] < 1 || resultado[campo] > max)) throw new Error('Revisa los valores del perfil mexicano.')
  return { ...resultado, creditos: [...perfil.creditos].sort() }
}

export function esAnalisisMexico(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) return false
  const n = data.metricas_prueba
  return data.modelo_id === 'nexocredit-enif2024-logistica-v1' && /^[a-f0-9]{64}$/.test(data.modelo_sha256) &&
    data.pais === 'México' && data.objetivo === 'algun_atraso_reportado' && data.tipo === 'modelo_estadistico_entrenado' &&
    typeof data.atraso_reportado_estimado === 'boolean' && data.reglas_score_utilizadas === false &&
    data.probabilidad_impago_futuro === null && data.requiere_azure === false && data.requiere_ollama === false &&
    typeof data.estimacion_asociativa === 'number' && Number.isFinite(data.estimacion_asociativa) &&
    data.estimacion_asociativa >= 0 && data.estimacion_asociativa <= 1 &&
    typeof data.umbral === 'number' && data.umbral > 0 && data.umbral < 1 &&
    data.clase === (data.atraso_reportado_estimado ? 'perfil_asociado_a_atraso' : 'perfil_no_asociado_a_atraso') &&
    (data.atraso_reportado_estimado === (data.estimacion_asociativa >= data.umbral) || Math.abs(data.estimacion_asociativa - data.umbral) <= .0000005) &&
    typeof data.limites === 'string' && data.limites.length > 0 && data.limites.length < 4000 &&
    data.fuente === 'https://www.inegi.org.mx/contenidos/programas/enif/2024/microdatos/enif_2024_bd_csv.zip' &&
    !!n && Number.isSafeInteger(n.filas) && n.filas > 0 && ['auc_roc', 'exactitud', 'sensibilidad', 'precision_positiva', 'f1']
      .every(k => typeof n[k] === 'number' && Number.isFinite(n[k]) && n[k] >= 0 && n[k] <= 1) &&
    typeof data.exactitud_siempre_sin_atraso === 'number' && data.exactitud_siempre_sin_atraso >= 0 && data.exactitud_siempre_sin_atraso <= 1 &&
    (data.control_uso == null || esControlPiloto(data.control_uso)) &&
    (data.comparacion_modelos == null || esComparacionPiloto(data.comparacion_modelos))
}

export function esControlPiloto(control) {
  return !!control && typeof control === 'object' && !Array.isArray(control) && control.modo === 'piloto_sombra' &&
    control.decision_automatizada_habilitada === false && control.uso_con_clientes_reales_habilitado === false &&
    control.validacion_empresarial === 'pendiente' && control.objetivo_empresarial_validado === false &&
    Array.isArray(control.motivos_no_promocion) && control.motivos_no_promocion.length > 0 && control.motivos_no_promocion.length <= 10 &&
    control.motivos_no_promocion.every(t => typeof t === 'string' && t.length > 0 && t.length <= 500)
}

export function esComparacionPiloto(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data) || data.promocion_automatica !== false) return false
  if (data.estado === 'no_disponible') return typeof data.motivo === 'string' && data.motivo.length > 0 && data.motivo.length < 1000
  if (data.estado !== 'completado' || data.protocolo !== 'nexocredit-piloto-comparacion-v1' ||
      !/^[a-f0-9]{64}$/.test(data.reporte_sha256) || data.modelo_servido_modificado !== false ||
      !Number.isSafeInteger(data.filas_desarrollo) || data.filas_desarrollo <= 0 || data.prueba_historica_excluida !== 783 ||
      typeof data.metodo !== 'string' || typeof data.limites !== 'string' || data.limites.length > 4000) return false
  return ['logistica', 'bosque', 'gradient_boosting', 'seleccion_anidada'].every(nombre => {
    const m = data.resultados?.[nombre]
    const ic = m?.intervalos_95_aproximados_por_upm
    const intervalo = (valores, min) => Array.isArray(valores) && valores.length === 2 && valores.every(v => typeof v === 'number' && Number.isFinite(v) && v >= min && v <= 1) && valores[0] <= valores[1]
    return !!m && ['auc_roc', 'average_precision', 'brier', 'sensibilidad', 'precision_positiva', 'f1'].every(k =>
      typeof m[k] === 'number' && Number.isFinite(m[k]) && m[k] >= 0 && m[k] <= 1) &&
      !!ic && ['auc_roc', 'average_precision', 'brier'].every(k => intervalo(ic[k], 0)) &&
      intervalo(ic.delta_auc_logistica, -1) &&
      m.mejora_auc_demostrada_respecto_logistica === (nombre !== 'logistica' && ic.delta_auc_logistica[0] > 0)
  })
}
