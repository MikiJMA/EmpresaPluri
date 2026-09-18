// Presentación del resultado devuelto por el backend.
const money = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' })
const riskClasses = { Bajo: 'risk-low', Medio: 'risk-medium', Alto: 'risk-high' }

export default function EvaluationResult({ result, busy }) {
  return (
    <section className={`card result ${result ? 'has-result' : ''}`} aria-live="polite" aria-busy={busy}>
      <div className="result-heading"><p className="eyebrow">RESUMEN DEL ANÁLISIS</p><span className="result-status">{busy ? 'Procesando' : result ? 'Completado' : 'Por evaluar'}</span></div>
      {result ? (
        <>
          <div className="risk-heading"><div><p className="result-label">Riesgo preliminar</p><h2>{result.nivel_riesgo_preliminar}</h2></div><span className={`risk-pill ${riskClasses[result.nivel_riesgo_preliminar] || ''}`}>● {result.nivel_riesgo_preliminar}</span></div>
          <p className="applicant">Solicitante <strong>{result.rfc}</strong></p>
          <div className="metric"><small>Margen mensual disponible</small><strong>{money.format(result.margen_libre)}</strong><span>Ingresos menos gastos mensuales</span></div>
          <h3>Factores de la evaluación</h3>
          <ul className="factors">{result.factores.map(factor => <li key={factor}>{factor}</li>)}</ul>
          <p className="notice">{result.mensaje}</p>
          <small className="model-version">Versión: {result.version_modelo}</small>
          <p className="save-status">{result.guardado
            ? `Guardada en el historial · ${new Date(result.fecha).toLocaleString('es-MX')}`
            : 'Evaluación sin guardar: PostgreSQL no está configurado.'}</p>
        </>
      ) : (
        <div className="empty-result">
          <div className={`analysis-illustration ${busy ? 'is-loading' : ''}`} aria-hidden="true"><div className="orbit" /><div className="mini-report"><span /><span /><div className="mini-bars"><i /><i /><i /><i /></div></div><div className="illustration-badge">↗</div></div>
          <h2>{busy ? 'Analizando tu escenario' : 'Tu próxima perspectiva\ncomienza aquí'}</h2>
          <p>{busy ? 'Estamos calculando el margen y aplicando las reglas de evaluación.' : 'Completa el formulario para visualizar el margen disponible y los factores de riesgo.'}</p>
          <div className="steps"><span><b>01</b> Captura</span><i>→</i><span><b>02</b> Evalúa</span><i>→</i><span><b>03</b> Revisa</span></div>
        </div>
      )}
    </section>
  )
}
