export const evaluacion = { id: '00000000-0000-4000-8000-000000000123', rfc: 'DEMO-IA', margen_libre: 20000,
  nivel_riesgo_preliminar: 'Bajo', version_modelo: 'reglas-demo-v2', guardado: true,
  fecha: '2026-10-15T12:00:00Z', modo: 'demostracion', factores: ['Reglas demo'], mensaje: 'Ejercicio académico' }
export const captura = { ingresos_mensuales: '30000', gastos_mensuales: '10000', deuda_actual: '50000',
  pagos_mensuales_creditos: '2500', dias_atraso_actual: '0', score_buro_actual: '900' }
export const estado = { proveedor: 'ollama', configurado: true, modelo: 'llama3.1:8b', conexion_verificada: false,
  tipo: 'valoracion-generativa-no-predictiva', motivo: 'Configuración presente; consulta pendiente.' }
export const resultado = { evaluacion_id: evaluacion.id, riesgo_por_reglas: 'Bajo', version_reglas: 'reglas-demo-v2',
  reglas_modificadas: false, nivel_riesgo_ia: 'Medio', proveedor: 'ollama', modelo: 'llama3.1:8b',
  tipo: 'valoracion-generativa-no-predictiva', generada_por_ia: true, fecha_generacion: '2026-10-15T12:00:00Z',
  datos_evaluados: { ingresos_mensuales: 30000, gastos_mensuales: 10000, deuda_actual: 50000, pagos_mensuales_creditos: 2500,
    dias_atraso_actual: 0, score_buro_actual: 900, margen_mensual: 20000, pagos_ingreso: 8.33, deuda_ingreso: 1.67 },
  factores: [{ codigo: 'deuda_ingreso', etiqueta: 'Deuda / ingreso mensual', valor: 1.67, unidad: 'meses' },
    { codigo: 'score_capturado', etiqueta: 'Score capturado', valor: 900, unidad: 'puntos' }],
  recomendaciones: [{ codigo: 'revision_humana', texto: 'Solicitar revisión humana.' }],
  aviso: 'Valoración generativa, no modelo predictivo validado. No autoriza créditos.' }
export const vista = { estado: 'lista', configuracion: estado, resultado, error: '' }
