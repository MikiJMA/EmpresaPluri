import ScoreAyuda from './ScoreAyuda'
import PerfilMexico from './PerfilMexico'
import { erroresFinancieros } from '../servicios/coherenciaFinanciera.mjs'

const financialFields = [
  { name: 'ingresos_mensuales', label: 'Ingresos mensuales', placeholder: '30,000.00', min: '0.01' },
  { name: 'gastos_mensuales', label: 'Gastos mensuales', placeholder: '10,000.00', min: '0' },
  { name: 'deuda_actual', label: 'Deuda actual total', placeholder: 'Ej. 50,000.00', min: '0' },
  { name: 'pagos_mensuales_creditos', label: 'Pagos mensuales de créditos', placeholder: 'Ej. 2,500.00', min: '0' },
]

export default function EvaluationForm({ form, busy, error, change, submit, identidad }) {
  const inconsistencias = erroresFinancieros(form)
  function enviar(event) {
    if (inconsistencias.length) { event.preventDefault(); return }
    submit(event)
  }
  return (
    <section className="card form-card">
      <div className="card-heading"><div><h2>Datos del solicitante</h2><p>Escenario ficticio · RFC y datos financieros obligatorios</p></div><span className="enterprise-panel-tag">MXN</span></div>
      <form onSubmit={enviar}>
        <fieldset disabled={busy}>
          <div className="field-group">
            <label htmlFor="rfc">RFC del solicitante <span>*</span></label>
            <input id="rfc" name="rfc" value={form.rfc} onChange={change} maxLength={13} autoCapitalize="characters" spellCheck={false} placeholder="Ej. AAAA010101AA1" required />
          </div>
          {identidad}
          <div className="form-divider"><span>Información financiera</span><span>MXN</span></div>
          <div className="financial-fields">
            {financialFields.map(({ name, label, placeholder, min }) => (
              <div className="field-group" key={name}>
                <label htmlFor={name}>{label} <span>*</span></label>
                <div className="input-affix"><span aria-hidden="true">$</span><input id={name} name={name} type="number" min={min} max="1000000000" step="0.01" placeholder={placeholder} value={form[name]} onChange={change} required /></div>
              </div>
            ))}
          </div>
          <div className="field-group score-field">
            <label htmlFor="dias_atraso_actual">Días de atraso actual <span>*</span></label>
            <input id="dias_atraso_actual" name="dias_atraso_actual" type="number" min="0" max="36500" step="1" placeholder="0 si estás al corriente" value={form.dias_atraso_actual} onChange={change} required aria-describedby="credit-help" />
          </div>
          <details className="enterprise-field-help"><summary>Cómo capturar deuda, pagos y atraso</summary><p id="credit-help" className="form-footnote">Deuda: saldo pendiente total. Pagos: suma mensual de tus créditos. Atraso: días del pago vencido más antiguo aún pendiente; 0 si estás al corriente. Captura 0 en deuda y pagos si no tienes créditos. Los gastos mensuales deben incluir los pagos de créditos. Estos tres datos se guardan, pero aún no modifican el riesgo demo.</p></details>
          {inconsistencias.length > 0 && <div id="financial-errors" role="alert" className="error">{inconsistencias.map(texto => <p key={texto}>{texto}</p>)}</div>}
          <div className="field-group score-field">
            <label htmlFor="score_buro_actual">Score capturado <span>*</span><small>Escala demo: 0–1000</small></label>
            <input id="score_buro_actual" name="score_buro_actual" type="number" min="0" max="1000" step="1" placeholder="Ej. 700" value={form.score_buro_actual} onChange={change} required aria-describedby="score-help score-help-disclaimer" />
            <ScoreAyuda valor={form.score_buro_actual} />
          </div>
          <PerfilMexico perfil={form.perfil_enif} change={change} />
          <button type="submit" disabled={inconsistencias.length > 0} aria-describedby={inconsistencias.length ? 'financial-errors' : undefined}><span>{busy ? 'Evaluando escenario…' : 'Evaluar escenario'}</span><span aria-hidden="true">{busy ? '◌' : '→'}</span></button>
          <p className="form-footnote">Al guardar, se generará automáticamente una explicación con el proveedor configurado: Azure OpenAI, Ollama o reglas locales. Solo usa ingresos, gastos, score y resultado, sin RFC. Azure puede generar consumo de pago; Ollama ejecuta el modelo en tu equipo. Usa solo datos ficticios.</p>
          <p className="form-footnote">RFC y datos financieros obligatorios. La CURP es opcional y solo se usa para revisar.</p>
        </fieldset>
      </form>
      {error && <p role="alert" className="error">{error}</p>}
    </section>
  )
}
