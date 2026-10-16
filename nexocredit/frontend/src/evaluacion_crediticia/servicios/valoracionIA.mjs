import { esFechaHora, leerRespuesta } from './contratos.mjs'

const riesgos = ['Bajo', 'Medio', 'Alto']
const campos = ['ingresos_mensuales', 'gastos_mensuales', 'deuda_actual', 'pagos_mensuales_creditos', 'dias_atraso_actual', 'score_buro_actual']
const unidades = { margen_mensual: 'MXN', pagos_ingreso: '%', deuda_ingreso: 'meses', atraso_dias: 'días', score_capturado: 'puntos' }
const recomendaciones = ['confirmar_captura', 'revisar_ingresos_gastos', 'revisar_deuda_pagos', 'revisar_atrasos', 'revision_humana']
const objeto = v => v && typeof v === 'object' && !Array.isArray(v)
const numero = v => typeof v === 'number' && Number.isFinite(v)
const texto = (v, max) => typeof v === 'string' && v.trim().length > 0 && v.length <= max
const esUUID = v => typeof v === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v)
const igualNumero = (a, b) => numero(a) && numero(b) && Math.abs(a - b) <= 1e-7
// Python round y JS pueden resolver empates de centésimas de forma diferente.
// Verificar la precisión declarada contra el cociente, no imponer otro redondeo.
const cocienteRedondeado = (a, b) => numero(a) && numero(b) && Math.abs(a - b) <= 0.00500001

export function validarEstadoValoracion(data) {
  if (!objeto(data) || !['ollama', 'deshabilitado', 'no_valido'].includes(data.proveedor)
    || typeof data.configurado !== 'boolean' || data.conexion_verificada !== false
    || data.tipo !== 'valoracion-generativa-no-predictiva' || !texto(data.motivo, 2000)
    || (data.configurado && (data.proveedor !== 'ollama' || !texto(data.modelo, 128)))) {
    throw new Error('El estado del evaluador IA no tiene un formato válido.')
  }
  return data
}

export function validarValoracion(data, evaluacion, captura, estado) {
  const falla = () => { throw new Error('La valoración IA no coincide con la solicitud guardada o tiene un formato inválido. No se muestra un riesgo inventado.') }
  const claves = ['evaluacion_id', 'riesgo_por_reglas', 'version_reglas', 'reglas_modificadas',
    'nivel_riesgo_ia', 'factores', 'recomendaciones', 'datos_evaluados', 'proveedor', 'modelo',
    'tipo', 'generada_por_ia', 'fecha_generacion', 'aviso']
  if (!objeto(data) || Object.keys(data).length !== claves.length || !claves.every(k => Object.hasOwn(data, k))
    || !esUUID(data.evaluacion_id) || data.evaluacion_id !== evaluacion.id
    || data.riesgo_por_reglas !== evaluacion.nivel_riesgo_preliminar || data.version_reglas !== evaluacion.version_modelo
    || data.reglas_modificadas !== false || !riesgos.includes(data.nivel_riesgo_ia)
    || data.proveedor !== 'ollama' || data.modelo !== estado.modelo || data.generada_por_ia !== true
    || data.tipo !== 'valoracion-generativa-no-predictiva' || !esFechaHora(data.fecha_generacion)
    || !texto(data.aviso, 2000) || !objeto(data.datos_evaluados)) falla()
  const datos = data.datos_evaluados
  if (Object.keys(datos).length !== 9 || !campos.every(k => {
    const original = captura?.[k]
    return original !== null && original !== undefined && String(original).trim() !== '' && igualNumero(datos[k], Number(original))
  }) || datos.ingresos_mensuales <= 0 || datos.ingresos_mensuales > 1e9
    || !['gastos_mensuales', 'deuda_actual', 'pagos_mensuales_creditos'].every(k => datos[k] >= 0 && datos[k] <= 1e9)
    || datos.pagos_mensuales_creditos > datos.gastos_mensuales
    || !Number.isInteger(datos.dias_atraso_actual) || datos.dias_atraso_actual < 0 || datos.dias_atraso_actual > 36500
    || (datos.dias_atraso_actual > 0 && datos.deuda_actual === 0)
    || !Number.isInteger(datos.score_buro_actual) || datos.score_buro_actual < 0 || datos.score_buro_actual > 1000
    || !igualNumero(datos.margen_mensual, evaluacion.margen_libre)
    || !cocienteRedondeado(datos.pagos_ingreso, 100 * datos.pagos_mensuales_creditos / datos.ingresos_mensuales)
    || !cocienteRedondeado(datos.deuda_ingreso, datos.deuda_actual / datos.ingresos_mensuales)) falla()
  const valores = { ...datos, atraso_dias: datos.dias_atraso_actual, score_capturado: datos.score_buro_actual }
  if (!Array.isArray(data.factores) || data.factores.length < 1 || data.factores.length > 5
    || new Set(data.factores.map(f => f?.codigo)).size !== data.factores.length
    || !data.factores.every(f => objeto(f) && Object.keys(f).length === 4 && Object.hasOwn(unidades, f.codigo)
      && texto(f.etiqueta, 120) && f.unidad === unidades[f.codigo] && igualNumero(f.valor, valores[f.codigo]))
    || !Array.isArray(data.recomendaciones) || data.recomendaciones.length < 1 || data.recomendaciones.length > 5
    || new Set(data.recomendaciones.map(r => r?.codigo)).size !== data.recomendaciones.length
    || !data.recomendaciones.every(r => objeto(r) && Object.keys(r).length === 2 && recomendaciones.includes(r.codigo) && texto(r.texto, 300))
    || !data.recomendaciones.some(r => r.codigo === 'revision_humana')) falla()
  return data
}

export function crearServicioValoracion(fetchAutenticado, base) {
  const api = base.replace(/\/$/, '')
  return {
    async estado(signal) {
      const response = await fetchAutenticado(`${api}/api/v1/valoracion-ia/estado`, { signal: AbortSignal.any([signal, AbortSignal.timeout(10000)]) })
      return leerRespuesta(response, validarEstadoValoracion, 'estado de valoración IA')
    },
    async consultar(evaluacion, captura, estado) {
      if (evaluacion?.guardado !== true || !esUUID(evaluacion.id) || estado?.configurado !== true) {
        throw new Error('Se necesita una evaluación guardada y el evaluador Ollama configurado.')
      }
      // Sólo el UUID viaja desde la pantalla: el servidor lee SU copia de los datos guardados.
      const response = await fetchAutenticado(`${api}/api/v1/evaluaciones/${evaluacion.id}/valoracion-ia`,
        { method: 'POST', signal: AbortSignal.timeout(200000) })
      return leerRespuesta(response, data => validarValoracion(data, evaluacion, captura, estado), 'valoración IA')
    },
  }
}

export function crearGeneradorValoraciones(solicitar) {
  const intentos = new Map()
  return (evaluacion, captura, estado, reintentar = false) => {
    const anterior = intentos.get(evaluacion.id)
    if (anterior && !(reintentar && anterior.fallo) && Date.now() - anterior.fecha < 86400000) return anterior.promesa
    const intento = { fecha: Date.now(), fallo: false }
    intento.promesa = Promise.resolve().then(() => solicitar(evaluacion, captura, estado)).catch(error => { intento.fallo = true; throw error })
    intentos.set(evaluacion.id, intento)
    return intento.promesa
  }
}

export const vistaInicialValoracion = () => ({ estado: 'comprobando', configuracion: null, resultado: null, error: '' })
export function crearControlValoracion({ evaluacion, captura, servicio, generar, emitir }) {
  let cerrado = false, ocupado = false
  let configuracion
  const controller = new AbortController()
  const actualizar = data => { if (!cerrado) emitir(data) }
  const fallar = error => actualizar({ estado: 'error', configuracion, resultado: null,
    error: error instanceof TypeError || error?.name === 'TimeoutError'
      ? 'No se completó la valoración IA. El riesgo por reglas sigue guardado. No se reintentó automáticamente.'
      : error instanceof Error ? error.message : 'No se completó la valoración IA.' })
  async function consultar(reintentar = false) {
    if (cerrado || ocupado || !configuracion?.configurado) return
    ocupado = true
    actualizar({ estado: 'generando', configuracion, resultado: null, error: '' })
    try {
      const resultado = await generar(evaluacion, captura, configuracion, reintentar)
      actualizar({ estado: 'lista', configuracion, resultado, error: '' })
    } catch (error) { fallar(error) } finally { ocupado = false }
  }
  return {
    async iniciar() {
      if (cerrado || ocupado) return
      ocupado = true
      try {
        configuracion = await servicio.estado(controller.signal)
        if (cerrado) return
        if (!configuracion.configurado) { actualizar({ estado: 'no_disponible', configuracion, resultado: null, error: '' }); return }
      } catch (error) { if (!cerrado) fallar(error); return } finally { ocupado = false }
      return consultar()
    },
    reintentar() { return configuracion?.configurado ? consultar(true) : this.iniciar() },
    cerrar() { cerrado = true; controller.abort() },
  }
}
