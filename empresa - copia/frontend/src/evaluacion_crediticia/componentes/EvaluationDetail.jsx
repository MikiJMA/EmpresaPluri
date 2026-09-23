import { useEffect, useRef, useState } from 'react'
import { consultarDetalle, guardarRevision } from '../servicios/creditApi'
import '../../styles/Detail.css'

const fields = { ingresos_mensuales: 'Ingresos mensuales', gastos_mensuales: 'Gastos mensuales', deuda_actual: 'Deuda actual', pagos_mensuales_creditos: 'Pagos mensuales de créditos', dias_atraso_actual: 'Días de atraso', score_buro_actual: 'Score capturado' }
export default function EvaluationDetail({ id, close }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [form, setForm] = useState({ estado: 'Pendiente', responsable: '', observaciones: '' })
  const retry = useRef(null)
  const title = useRef(null)
  useEffect(() => {
    title.current?.focus()
    const controller = new AbortController()
    consultarDetalle(id, controller.signal).then(value => {
      if (!controller.signal.aborted) { setData(value); setForm(f => ({ ...f, estado: value.estado_revision })) }
    }).catch(err => { if (!controller.signal.aborted) setError(err.message) })
    return () => controller.abort()
  }, [id])
  function change(e) { retry.current = null; setNotice(''); setForm(f => ({ ...f, [e.target.name]: e.target.value })) }
  async function save(e) {
    e.preventDefault(); setBusy(true); setError(''); setNotice('')
    try {
      retry.current ||= { ...form, id: crypto.randomUUID(), version_anterior: data.version_revision }
      const saved = await guardarRevision(id, retry.current)
      setData(old => ({ ...old, estado_revision: saved.estado, version_revision: saved.version, revisiones: [saved, ...old.revisiones.filter(r => r.id !== saved.id)] }))
      retry.current = null
      setNotice('Revisión guardada. Es un dictamen de demostración, no una autorización real.')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <section className="evaluation-detail" aria-labelledby="detail-title">
    <h2 id="detail-title" ref={title} tabIndex={-1}>Detalle y revisión manual</h2>
    <button type="button" disabled={busy} onClick={close}>Cerrar detalle</button>
    <p className="notice">Solo demostración. No hay autenticación: el responsable es un nombre declarado, no una identidad verificada. No usar para autorizar créditos reales.</p>
    {error && <p role="alert" className="error">{error}</p>}
    {!data && !error && <p role="status">Cargando detalle…</p>}
    {data && <>
      <p>Solicitante: <strong>{data.rfc}</strong> · {new Date(data.fecha).toLocaleString('es-MX')}</p>
      <dl className="detail-fields">{Object.entries(fields).map(([key, label]) => <div key={key}><dt>{label}</dt><dd>{data.solicitud[key] == null ? 'No capturado' : key.includes('dias') || key.includes('score') ? data.solicitud[key] : new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(data.solicitud[key])}</dd></div>)}</dl>
      <p>Riesgo demo: <strong>{data.nivel_riesgo_preliminar}</strong> · Modelo: {data.version_modelo}</p>
      <p>Estado manual: <strong>{data.estado_revision}</strong> · Revisión {data.version_revision}</p>
      <form onSubmit={save}><fieldset disabled={busy}>
        <label htmlFor="revision-estado">Estado manual (demo)</label><select id="revision-estado" name="estado" value={form.estado} onChange={change}>{['Pendiente', 'Aprobada', 'Rechazada'].map(s => <option key={s}>{s}</option>)}</select>
        <label htmlFor="revision-responsable">Responsable declarado</label><input id="revision-responsable" name="responsable" maxLength={120} required value={form.responsable} onChange={change} />
        <label htmlFor="revision-observaciones">Observaciones / motivo</label><textarea id="revision-observaciones" name="observaciones" maxLength={2000} required value={form.observaciones} onChange={change} />
        <button type="submit" disabled={busy || !form.responsable.trim() || !form.observaciones.trim()}>{busy ? 'Guardando…' : 'Guardar revisión demo'}</button>
      </fieldset></form>
      {notice && <p role="status">{notice}</p>}
      <h3>Historial de revisiones</h3>
      {!data.revisiones.length ? <p>Sin revisiones manuales. Pendiente de revisar.</p> : <ol>{data.revisiones.map(r => <li key={r.id}><strong>{r.estado}</strong> · {new Date(r.fecha).toLocaleString('es-MX')} · {r.responsable}<p>{r.observaciones}</p></li>)}</ol>}
    </>}
  </section>
}
