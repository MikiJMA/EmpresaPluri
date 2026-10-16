export const control = { modo: 'piloto_sombra', decision_automatizada_habilitada: false,
  uso_con_clientes_reales_habilitado: false, validacion_empresarial: 'pendiente', objetivo_empresarial_validado: false,
  motivos_no_promocion: ['Sin historial empresarial autorizado.', 'Sin validación temporal y costes aprobados.'] }

const metrica = (auc, ap, brier, delta) => ({ auc_roc: auc, average_precision: ap, brier,
  sensibilidad: .65, precision_positiva: .30, f1: .41, mejora_auc_demostrada_respecto_logistica: false,
  intervalos_95_aproximados_por_upm: { auc_roc: [.61, .67], average_precision: [.33, .40], brier: [.16, .19], delta_auc_logistica: delta } })
export const comparacion = { estado: 'completado', protocolo: 'nexocredit-piloto-comparacion-v1',
  reporte_sha256: '50de28cba9113d3751bdfbc66d3857e40bfc3fba293f21c77e1fcb047ce70ea5',
  filas_desarrollo: 3123, prueba_historica_excluida: 783, modelo_servido_modificado: false, promocion_automatica: false,
  metodo: 'Validación anidada agrupada 5x3', limites: 'No habilita decisiones ni uso con clientes reales.',
  resultados: { logistica: metrica(.6422234762851914, .36262512877844033, .17276417193658145, [0, 0]),
    bosque: metrica(.6484455216556047, .36247897189905837, .17203390186845569, [-.00637849756522625, .0184771866465438]),
    gradient_boosting: metrica(.6468207428304263, .3619689648634382, .17218600660034616, [-.00489756908356303, .0138429029657721]),
    seleccion_anidada: metrica(.6446019192823691, .35804399271656934, .17244063115581196, [-.00669350005647704, .0107159461130785]) } }
