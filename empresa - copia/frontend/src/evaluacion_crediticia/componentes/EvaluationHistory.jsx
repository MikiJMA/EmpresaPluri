import { useEffect, useState } from 'react'
import { consultarHistorial } from '../servicios/creditApi'
import '../../styles/History.css'
import EvaluationDetail from './EvaluationDetail'

export default function EvaluationHistory({ revision }) {
  const [offset, setOffset] = useState(0)
  const [selected, setSelected] = useState(null)
  const [refresh, setRefresh] = useState(0)
  const [data, setData] = useState({ items: [], hay_mas: false })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    consultarHistorial(offset, controller.signal)
      .then(value => { if (!controller.signal.aborted) { setData(value); setError('') } })
      .catch(err => { if (!controller.signal.aborted) setError(err.message || 'No se pudo cargar el historial.') })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [offset, refresh, revision])

  function cambiarPagina(next) { setLoading(true); setOffset(next) }

  return (
    <section className="history card" aria-busy={loading}>
      <div className="history-heading">
        <div><h2>Historial de evaluaciones</h2><p>Evaluaciones guardadas, de la más reciente a la más antigua.</p></div>
        <button type="button" disabled={loading} onClick={() => { setLoading(true); setOffset(0); setRefresh(value => value + 1) }}>Actualizar</button>
      </div>
      {loading ? <p role="status">Cargando historial…</p> : error ? <p role="alert" className="error">{error}</p> : (
        <>
          {data.items.length ? <div className="history-scroll"><table>
            <caption className="sr-history">Evaluaciones guardadas en PostgreSQL</caption>
            <thead><tr><th>Fecha</th><th>Solicitante</th><th>Margen disponible</th><th>Riesgo</th><th>Revisión</th></tr></thead>
            <tbody>{data.items.map(item => <tr key={item.id}>
              <td>{new Date(item.fecha).toLocaleString('es-MX')}</td><td>{item.rfc}</td>
              <td>{new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(item.margen_libre)}</td>
              <td>{item.nivel_riesgo_preliminar}</td>
              <td><button type="button" disabled={!!selected} onClick={() => setSelected(item.id)}>Ver detalle</button></td>
            </tr>)}</tbody>
          </table></div> : <p>Aún no hay evaluaciones en esta página.</p>}
          <nav className="history-pages" aria-label="Páginas del historial">
            <button type="button" disabled={offset === 0} onClick={() => cambiarPagina(Math.max(0, offset - 10))}>Anterior</button>
            <span>Página {Math.floor(offset / 10) + 1}</span>
            <button type="button" disabled={!data.hay_mas} onClick={() => cambiarPagina(offset + 10)}>Siguiente</button>
          </nav>
        </>
      )}
      {selected && <EvaluationDetail key={selected} id={selected} close={() => setSelected(null)} />}
    </section>
  )
}
