import { useContext, useEffect, useRef, useState } from 'react'
import './styles/App.css'
import { evaluarCredito } from './evaluacion_crediticia/servicios/creditApi'
import EvaluationForm from './evaluacion_crediticia/componentes/EvaluationForm'
import { perfilMexicoVacio } from './evaluacion_crediticia/servicios/modeloMexico.mjs'
import RevisarIdentidad from './evaluacion_crediticia/componentes/RevisarIdentidad'
import EvaluationResult from './evaluacion_crediticia/componentes/EvaluationResult'
import SegundaOpinionModelo from './evaluacion_crediticia/componentes/SegundaOpinionModelo'
import ValoracionIASolicitud from './evaluacion_crediticia/componentes/ValoracionIASolicitud'
import { crearGeneradorValoraciones } from './evaluacion_crediticia/servicios/valoracionIA.mjs'
import { servicioValoracion } from './evaluacion_crediticia/servicios/valoracionIACliente'
import EvaluationHistory from './evaluacion_crediticia/componentes/EvaluationHistory'
import Dashboard from './dashboard/Dashboard'
import AzureMLDemo from './azure_ml/AzureMLDemo'
import BuscadorDocumentos from './azure_search/BuscadorDocumentos'
import IndicadoresFinancieros from './datos_financieros/IndicadoresFinancieros'
import { crearGeneradorExplicaciones } from './azure_openai/generacion.mjs'
import { solicitarExplicacion } from './azure_openai/servicio'
import './styles/Bento.css'
import MarcoAplicacion from './interfaz/MarcoAplicacion'
import IndicadoresEscenario from './evaluacion_crediticia/componentes/IndicadoresEscenario'
import { UsuarioContext } from './autenticacion/contexto'
import './styles/Enterprise.css'
import './styles/ScoreAyuda.css'
import './styles/Identidad.css'
import './styles/SegundaOpinion.css'
import './styles/ModeloMexico.css'
import EstadoProveedores from './interfaz/EstadoProveedores'
import SeguimientoCreditos from './seguimiento_crediticio/SeguimientoCreditos'
import ResumenInicio from './interfaz/ResumenInicio'
import { rutaDeSeccion, seccionDesdeHash, seccionDesdeRuta } from './interfaz/secciones.mjs'

const initial = { rfc: '', ingresos_mensuales: '', gastos_mensuales: '', score_buro_actual: '', deuda_actual: '', pagos_mensuales_creditos: '', dias_atraso_actual: '', perfil_enif: perfilMexicoVacio() }

export default function App() {
  const user = useContext(UsuarioContext)
  const [seccion, setSeccion] = useState(() => seccionDesdeHash(window.location.hash) || seccionDesdeRuta(window.location.pathname) || 'seguimiento')
  const [form, setForm] = useState(initial)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const clave = useRef(null)
  const [revision, setRevision] = useState(0)
  const [submitted, setSubmitted] = useState(null)
  const [explicacion, setExplicacion] = useState(null)
  const [generarExplicacion] = useState(() => crearGeneradorExplicaciones(solicitarExplicacion))
  const [generarValoracionIA] = useState(() => crearGeneradorValoraciones(servicioValoracion.consultar))
  const intentoVisible = useRef(0)

  useEffect(() => {
    function sincronizarRuta() {
      const destinoAnterior = seccionDesdeHash(window.location.hash)
      const destino = destinoAnterior || seccionDesdeRuta(window.location.pathname)
      if (destinoAnterior) window.history.replaceState(null, '', rutaDeSeccion(destinoAnterior))
      if (destino) setSeccion(destino)
      else {
        window.history.replaceState(null, '', '/')
        setSeccion('seguimiento')
      }
    }
    sincronizarRuta()
    window.addEventListener('popstate', sincronizarRuta)
    window.addEventListener('hashchange', sincronizarRuta)
    return () => {
      window.removeEventListener('popstate', sincronizarRuta)
      window.removeEventListener('hashchange', sincronizarRuta)
    }
  }, [])

  function irASeccion(destino, event) {
    if (event) {
      if (event.button && event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
      event.preventDefault()
    }
    const ruta = rutaDeSeccion(destino)
    if (window.location.pathname !== ruta || window.location.hash) window.history.pushState(null, '', ruta)
    setSeccion(destino)
    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  function nuevaEvaluacion() {
    if (busy) return
    intentoVisible.current += 1
    setForm(initial)
    setSubmitted(null)
    setResult(null)
    setExplicacion(null)
    setError('')
    clave.current = null
    irASeccion('evaluacion')
  }

  function change(event) {
    intentoVisible.current += 1
    const { name, value } = event.target
    setForm(current => ({ ...current, [name]: value }))
    setResult(null)
    setExplicacion(null)
    setError('')
    clave.current = null
  }

  async function submit(event) {
    event.preventDefault()
    const intento = ++intentoVisible.current
    setBusy(true)
    setError('')
    setResult(null)
    setExplicacion(null)
    try {
      clave.current ||= crypto.randomUUID()
      const resultado = await evaluarCredito(form, clave.current)
      setSubmitted({ ...form })
      setResult(resultado)
      if (resultado.guardado) setRevision(current => current + 1)
      if (resultado.guardado && resultado.id) {
        setExplicacion({ estado: 'generando' })
        // Separado del guardado: un fallo de IA no hace fallar la evaluación.
        // El contador evita que una respuesta antigua aparezca en otro escenario.
        generarExplicacion(resultado.id).then(
          data => { if (intentoVisible.current === intento) setExplicacion({ estado: 'lista', data }) },
          err => { if (intentoVisible.current === intento) setExplicacion({ estado: 'error', error: err.message }) },
        )
      }
    } catch (err) {
      setError(err instanceof TypeError || err.name === 'TimeoutError' ? 'No se pudo conectar con la API. Comprueba que el backend o los servicios Docker estén iniciados.' : err.message)
    } finally { setBusy(false) }
  }

  return (
    <MarcoAplicacion user={user} seccion={seccion} onSeccionChange={irASeccion}>
      {seccion === 'seguimiento' && <div id="seguimiento">
        <ResumenInicio onSeccionChange={irASeccion} onNuevaEvaluacion={nuevaEvaluacion} busy={busy} />
        <Dashboard revision={revision} />
      </div>}
      {seccion === 'evaluacion' && <>
        <IndicadoresEscenario result={result} submitted={submitted} />
        <div className="workspace" id="evaluacion">
          <EvaluationForm form={form} busy={busy} error={error} change={change} submit={submit} identidad={<RevisarIdentidad rfc={form.rfc} bloqueado={busy} />} />
          <EvaluationResult result={result} busy={busy} submitted={submitted} explicacion={explicacion}
            valoracionIA={result?.guardado && result?.id && !busy ? <ValoracionIASolicitud key={result.id} evaluacion={result} captura={submitted} generar={generarValoracionIA} /> : null}
            segundaOpinion={result?.guardado && result?.id && !busy ? <SegundaOpinionModelo key={result.id} evaluacion={result} /> : null} />
        </div>
      </>}
      {seccion === 'historial' && <div id="historial"><EvaluationHistory revision={revision} /></div>}
      {seccion === 'creditos' && <SeguimientoCreditos activo revision={revision}/>}
      {seccion === 'laboratorio' && <div id="laboratorio"><AzureMLDemo /></div>}
      {seccion === 'indicadores' && <IndicadoresFinancieros />}
      {seccion === 'documentos' && <BuscadorDocumentos />}
      <div className="demo-banner"><span className="info-icon" aria-hidden="true">i</span><p><strong>Piloto empresarial en sombra</strong><span> Pruebas controladas con escenarios ficticios y datos públicos. Modelo ENIF, reglas y valoración Ollama se muestran por separado. Sin decisiones automatizadas ni validación empresarial de impagos futuros.</span></p></div>
      <EstadoProveedores />
    </MarcoAplicacion>
  )
}
