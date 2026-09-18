// Campos financieros del formulario de evaluación crediticia.
const financialFields = [
  { name: 'ingresos_mensuales', label: 'Ingresos mensuales', placeholder: '30,000.00', min: '0.01' },
  { name: 'gastos_mensuales', label: 'Gastos mensuales', placeholder: '10,000.00', min: '0' },
]

export default function EvaluationForm({ form, busy, error, change, submit }) {
  return (
    <section className="card form-card">
      <div className="card-heading"><span className="section-number">01</span><div><h2>Nueva evaluación</h2><p>Completa los datos de tu escenario.</p></div></div>
      <form onSubmit={submit}>
        <fieldset disabled={busy}>
          <div className="field-group">
            <label htmlFor="rfc">RFC del solicitante <span>*</span></label>
            <input id="rfc" name="rfc" value={form.rfc} onChange={change} placeholder="Ej. AAAA010101AA1" required />
          </div>
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
            <label htmlFor="score_buro_actual">Score capturado <span>*</span><small>Escala demo: 0–1000</small></label>
            <input id="score_buro_actual" name="score_buro_actual" type="number" min="0" max="1000" step="1" placeholder="Ej. 700" value={form.score_buro_actual} onChange={change} required />
          </div>
          <button type="submit"><span>{busy ? 'Evaluando escenario…' : 'Evaluar escenario'}</span><span aria-hidden="true">{busy ? '◌' : '→'}</span></button>
          <p className="form-footnote">Todos los campos son obligatorios.</p>
        </fieldset>
      </form>
      {error && <p role="alert" className="error">{error}</p>}
    </section>
  )
}
