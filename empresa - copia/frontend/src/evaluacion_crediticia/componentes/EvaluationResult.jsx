// Resultados de la API y captura enviada; nunca cifras ficticias precargadas.
import Explicacion from '../../azure_openai/Explicacion'
import { importe, valorCapturado } from './metricasEscenario.mjs'
const riskClasses = { Bajo: 'risk-low', Medio: 'risk-medium', Alto: 'risk-high' }

export default function EvaluationResult({ result, busy, submitted, explicacion }) {
  const captured = name => valorCapturado(result, submitted, name)
  const score = captured('score_buro_actual')
  return <section className="enterprise-result" aria-label="Resultado del análisis" aria-live="polite" aria-busy={busy}>
    <div className="card enterprise-risk-panel">
      <div className="card-heading"><h2>Resumen de riesgo</h2><span className={`risk-pill ${riskClasses[result?.nivel_riesgo_preliminar] || ''}`}>{busy ? 'Procesando' : result ? `Riesgo ${result.nivel_riesgo_preliminar}` : 'Sin resultado'}</span></div>
      <div className="enterprise-risk-body">
        <div className="enterprise-score-heading"><span>Score capturado</span><strong>{score === null ? '—' : `${score} / 1000`}</strong></div>
        {score === null ? <div className="enterprise-score-track" aria-hidden="true" /> : <div className="enterprise-score-track" role="meter" aria-label="Score capturado, no verificado" aria-valuemin={0} aria-valuemax={1000} aria-valuenow={score}><div style={{ width: `${Math.max(0, Math.min(100, score / 10))}%` }} /></div>}
        <p className="enterprise-score-note">{busy ? 'Evaluando el escenario…' : result ? 'Escala demo: 0–1000. No consultado en Buró.' : 'Completa el formulario para consultar tu escenario.'}</p>
        <div className="enterprise-secondary-metrics"><div><span>Pagos mensuales</span><strong>{importe(captured('pagos_mensuales_creditos'))}</strong></div><div><span>Días de atraso</span><strong>{captured('dias_atraso_actual') ?? '—'}</strong></div></div>
        <p className="enterprise-score-note">Deuda, pagos y atraso se conservan, pero no modifican el riesgo demo.</p>
        <h3>Factores determinantes</h3>
        {result ? <><p className="applicant">Identificador: <strong>{result.rfc}</strong></p><ol className="factors">{result.factores.map(factor => <li key={factor}>{factor}</li>)}</ol><p className="notice">{result.mensaje}</p><p className="save-status">{result.guardado ? `Guardada en el historial · ${new Date(result.fecha).toLocaleString('es-MX')}` : 'Evaluación sin guardar: PostgreSQL no está configurado.'}</p><p className="model-version">Versión: {result.version_modelo}</p></>
          : <p className="notice">Aquí aparecerán las reglas aplicadas. Sin resultados precargados: esta demostración no autoriza créditos.</p>}
        <p className="enterprise-risk-disclaimer">Probabilidad de incumplimiento no disponible. Las reglas demo no calculan probabilidades ni sustituyen la revisión humana.</p>
      </div>
    </div>
    {result?.guardado && result?.id && !busy && <Explicacion estado={explicacion} />}
  </section>
}
