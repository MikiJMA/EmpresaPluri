import { COLUMNAS_UCI } from '../../azure_ml/estadoConexion.mjs'

export const ejemploUCI = Object.fromEntries(COLUMNAS_UCI.map(name => [name,
  String(name === 'LIMIT_BAL' ? 200000 : name.startsWith('BILL_AMT') ? 22000 - Number(name.slice(8)) * 2000 : name.startsWith('PAY_AMT') ? 3000 : 0),
]))

export function vistaInicialSegundaOpinion() {
  return { valores: Object.fromEntries(COLUMNAS_UCI.map(name => [name, ''])), estado: null,
    comprobando: true, busy: false, consulta: 'pendiente', error: '', resultado: null,
    status: 'Comprobando configuración del modelo; todavía no se ha solicitado inferencia.' }
}

const mensajeError = error => error instanceof TypeError || error?.name === 'TimeoutError'
  ? 'No se pudo completar la consulta. Comprueba la conexión y vuelve a intentarlo; tu evaluación guardada no cambia.'
  : error instanceof Error ? error.message : 'No se pudo completar la segunda opinión. Tu evaluación guardada no cambia.'

// Control independiente y cancelable; una evaluación nueva obtiene otra instancia.
export function crearControlSegundaOpinion({ evaluacion, servicio, emitir }) {
  let vista = vistaInicialSegundaOpinion()
  let cerrado = false
  let intento = 0
  let peticion
  const actualizar = changes => {
    if (cerrado) return
    vista = { ...vista, ...changes }
    emitir(vista)
  }
  async function comprobar() {
    if (cerrado || vista.busy || peticion) return
    if (!vista.comprobando) actualizar({ comprobando: true, error: '', resultado: null, consulta: 'pendiente',
      status: 'Comprobando configuración; no se solicita inferencia.' })
    const controller = new AbortController()
    peticion = controller
    const actual = ++intento
    try {
      const estado = await servicio.consultarEstado(controller.signal)
      if (cerrado || intento !== actual) return
      actualizar({ estado, comprobando: false, error: '', resultado: null, consulta: 'pendiente',
        status: estado.motivo || (estado.configurado ? 'Configuración presente; inferencia pendiente de tu confirmación.' : 'Modelo no disponible. No se simulan resultados.') })
    } catch (error) {
      if (cerrado || intento !== actual) return
      actualizar({ estado: null, comprobando: false, error: mensajeError(error), status: 'No se pudo comprobar el proveedor. Puedes volver a comprobarlo.' })
    } finally { if (peticion === controller) peticion = null }
  }
  return {
    iniciar: comprobar,
    comprobar,
    cambiar(name, value) {
      if (cerrado || vista.busy || !COLUMNAS_UCI.includes(name)) return
      actualizar({ valores: { ...vista.valores, [name]: value }, resultado: null, error: '', consulta: 'pendiente' })
    },
    cargarEjemplo() {
      if (cerrado || vista.busy) return
      actualizar({ valores: { ...ejemploUCI }, resultado: null, error: '', consulta: 'pendiente' })
    },
    async consultar() {
      if (cerrado || vista.busy || vista.comprobando || !vista.estado?.configurado || peticion) return
      const controller = new AbortController()
      peticion = controller
      const actual = ++intento
      actualizar({ busy: true, resultado: null, error: '', consulta: 'consultando' })
      try {
        const resultado = await servicio.consultar(evaluacion, vista.valores, vista.estado, controller.signal)
        if (cerrado || intento !== actual) return
        actualizar({ resultado, consulta: 'correcta' })
      } catch (error) {
        if (cerrado || intento !== actual) return
        actualizar({ resultado: null, error: mensajeError(error), consulta: 'fallida' })
      } finally {
        if (!cerrado && intento === actual) actualizar({ busy: false })
        if (peticion === controller) peticion = null
      }
    },
    cerrar() { cerrado = true; intento += 1; peticion?.abort(); peticion = null },
  }
}
