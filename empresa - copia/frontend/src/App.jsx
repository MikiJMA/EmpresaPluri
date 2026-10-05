import { useContext, useRef, useState } from 'react'
import './styles/App.css'
import { evaluarCredito } from './evaluacion_crediticia/servicios/creditApi'
import EvaluationForm from './evaluacion_crediticia/componentes/EvaluationForm'
import EvaluationResult from './evaluacion_crediticia/componentes/EvaluationResult'
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

const initial = { rfc: '', ingresos_mensuales: '', gastos_mensuales: '', score_buro_actual: '', deuda_actual: '', pagos_mensuales_creditos: '', dias_atraso_actual: '' }

export default function App() {
  const user = useContext(UsuarioContext)
  const [seccion, setSeccion] = useState('evaluacion')
  const [form, setForm] = useState(initial)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const clave = useRef(null)
  const [revision, setRevision] = useState(0)
  const [submitted, setSubmitted] = useState(null)
  const [explicacion, setExplicacion] = useState(null)
  const [generarExplicacion] = useState(() => crearGeneradorExplicaciones(solicitarExplicacion))
  const intentoVisible = useRef(0)

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
    <MarcoAplicacion user={user} seccion={seccion} onSeccionChange={setSeccion}>
      <IndicadoresEscenario result={result} submitted={submitted} />
      <div className="demo-banner"><span className="info-icon" aria-hidden="true">i</span><p><strong>Modo demostración</strong><span> Usa datos ficticios. El riesgo se calcula con reglas ilustrativas; Azure OpenAI explica el resultado. El modelo de Azure ML se consulta por separado.</span></p></div>
      <div className="workspace" id="evaluacion">
        <EvaluationForm form={form} busy={busy} error={error} change={change} submit={submit} />
        <EvaluationResult result={result} busy={busy} submitted={submitted} explicacion={explicacion} />
      </div>
      <div id="historial"><EvaluationHistory revision={revision} /></div>
      <div id="seguimiento"><Dashboard revision={revision} /></div>
      <div id="laboratorio"><AzureMLDemo /></div>
      <IndicadoresFinancieros />
      <BuscadorDocumentos />
    </MarcoAplicacion>
  )
}
