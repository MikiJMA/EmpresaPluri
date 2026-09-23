import { useEffect, useState } from 'react'
import { consultarDashboard } from '../evaluacion_crediticia/servicios/creditApi'
import './Dashboard.css'

const initial = { desde: '', hasta: '', riesgo: '' }
const pesos = value => value == null ? 'Sin datos' : new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(value))

export default function Dashboard({ revision }) {
  const [draft, setDraft] = useState(initial)
  const [query, setQuery] = useState({ ...initial, version: 0 })
  const [state, setState] = useState({ data: null, error: '' })
  useEffect(() => {
    const controller = new AbortController()
    consultarDashboard(query, controller.signal)
      .then(data => { if (!controller.signal.aborted) setState({ data, error: '', query, revision }) })
      .catch(error => { if (!controller.signal.aborted) setState({ data: null, error: error.message, query, revision }) })
    return () => controller.abort()
  }, [query, revision])
  const loading = state.query !== query || state.revision !== revision
  const data = state.data
  function change(e) { setDraft(value => ({ ...value, [e.target.name]: e.target.value })) }
  function apply(e) { e.preventDefault(); setQuery({ ...draft, version: query.version + 1 }) }
  const invalid = draft.desde && draft.hasta && draft.desde > draft.hasta
  return <section className="dashboard card" aria-labelledby="dashboard-title" aria-busy={loading}>
    <h2 id="dashboard-title">Dashboard de evaluaciones</h2>
    <p>Resumen de todas las evaluaciones guardadas, no solo de la página del historial. Riesgos de demostración, no probabilidades de incumplimiento.</p>
    <form className="dashboard-filters" onSubmit={apply}>
      <label>Desde (UTC)<input type="date" name="desde" value={draft.desde} onChange={change} /></label>
      <label>Hasta (UTC)<input type="date" name="hasta" value={draft.hasta} onChange={change} /></label>
      <label>Riesgo<select name="riesgo" value={draft.riesgo} onChange={change}><option value="">Todos</option>{['Bajo', 'Medio', 'Alto'].map(r => <option key={r}>{r}</option>)}</select></label>
      <button disabled={!!invalid} type="submit">Aplicar / actualizar</button>
      <button type="button" onClick={() => { setDraft(initial); setQuery({ ...initial, version: query.version + 1 }) }}>Limpiar filtros</button>
    </form>
    {invalid && <p role="alert" className="error">La fecha inicial no puede ser posterior a la final.</p>}
    <p className="dashboard-scope">Filtros aplicados al dashboard: {query.desde || 'sin fecha inicial'} → {query.hasta || 'sin fecha final'} · {query.riesgo || 'todos los riesgos'}. Fechas inclusivas en UTC. El historial inferior no se filtra.</p>
    {loading ? <p role="status">Cargando dashboard…</p> : state.error ? <p role="alert" className="error">{state.error}</p> : data && <>
      <div className="dashboard-metrics">
        <div><span>Total de evaluaciones</span><strong data-testid="dashboard-total">{data.total}</strong><small>No representa clientes únicos</small></div>
        <div><span>Margen mensual promedio</span><strong>{pesos(data.margen_promedio)}</strong><small>Ingresos menos gastos</small></div>
        <div><span>Deuda actual promedio</span><strong>{pesos(data.deuda_promedio)}</strong><small>Sobre {data.con_deuda_capturada} evaluaciones con deuda capturada; incluye ceros</small></div>
      </div>
      {!data.total ? <p>No hay evaluaciones para estos filtros.</p> : <div className="dashboard-distribution" aria-label="Distribución por riesgo">
        <h3>Distribución por riesgo preliminar</h3>
        {[['Bajo', 'bajo'], ['Medio', 'medio'], ['Alto', 'alto']].map(([label, key]) => {
          const percent = 100 * data[key] / data.total
          return <div key={key} className="dashboard-risk"><span>{label}</span><div className="dashboard-track" aria-hidden="true"><div className={key} style={{ width: `${percent}%` }} /></div><span>{data[key]} · {percent.toFixed(1)}%</span></div>
        })}
      </div>}
    </>}
  </section>
}
