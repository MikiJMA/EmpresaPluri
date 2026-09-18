import { useRef, useState } from 'react'
import './styles/App.css'
import { evaluarCredito } from './evaluacion_crediticia/servicios/creditApi'
import EvaluationForm from './evaluacion_crediticia/componentes/EvaluationForm'
import EvaluationResult from './evaluacion_crediticia/componentes/EvaluationResult'
import EvaluationHistory from './evaluacion_crediticia/componentes/EvaluationHistory'

const initial = { rfc: '', ingresos_mensuales: '', gastos_mensuales: '', score_buro_actual: '' }

export default function App() {
  const [form, setForm] = useState(initial)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const clave = useRef(null)
  const [revision, setRevision] = useState(0)

  function change(event) {
    const { name, value } = event.target
    setForm(current => ({ ...current, [name]: value }))
    setResult(null)
    setError('')
    clave.current = null
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setResult(null)
    try {
      clave.current ||= crypto.randomUUID()
      const resultado = await evaluarCredito(form, clave.current)
      setResult(resultado)
      if (resultado.guardado) setRevision(current => current + 1)
    } catch (err) {
      setError(err instanceof TypeError || err.name === 'TimeoutError' ? 'No se pudo conectar con la API. Comprueba que el backend o los servicios Docker estén iniciados.' : err.message)
    } finally { setBusy(false) }
  }

  return (
    <main>
      <header className="topbar">
        <div className="brand"><span className="brand-mark" aria-hidden="true">P<span>・</span></span><div>PluriOne<small>Develop Talent & Technology</small></div></div>
        <div className="header-context"><span className="status-dot" /> Entorno de demostración</div>
      </header>
      <div className="page-content">
      <section className="intro">
        <div><p className="eyebrow">PLURIONE / ANÁLISIS CREDITICIO</p><h1>Claridad para cada<br /><span>evaluación.</span></h1><p>Explora un escenario financiero y comprende<br className="desktop-break" /> los factores detrás de su resultado.</p></div>
        <div className="intro-note"><span className="note-symbol" aria-hidden="true">↗</span><p>De los datos<br />a una visión más clara.</p><small>Captura · Evalúa · Comprende</small></div>
      </section>
      <div className="demo-banner"><span className="info-icon" aria-hidden="true">i</span><p><strong>Modo demostración</strong><span> Usa datos ficticios. La evaluación utiliza reglas ilustrativas, sin un modelo de IA entrenado.</span></p></div>
      <div className="workspace">
        <EvaluationForm form={form} busy={busy} error={error} change={change} submit={submit} />
        <EvaluationResult result={result} busy={busy} />
      </div>
      <EvaluationHistory revision={revision} />
      <footer><span>© PluriOne S.A. de C.V. · Proyecto de estadía</span><span>Evaluación orientativa · Revisión humana requerida</span></footer>
      </div>
    </main>
  )
}
