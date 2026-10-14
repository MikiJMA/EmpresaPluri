import { useContext, useEffect, useRef, useState } from 'react'
import { UsuarioContext } from '../autenticacion/contexto'
import { listarCreditos,cargarCredito,crearCredito,cargarEvaluaciones,cargarAuditoria } from './servicio'
import DetalleCredito from './DetalleCredito'
import { PanelAuditoria } from './PanelCredito'
import './Seguimiento.css'

const dia=()=>new Date().toISOString().slice(0,10)
const inicial=()=>({evaluacion_id:'',concepto:'',fecha_apertura:dia(),monto_total_pactado:'',cuotas:[{vencimiento:dia(),importe:''}]})
export default function SeguimientoCreditos({activo,revision}) {
  const user=useContext(UsuarioContext)
  const [form,setForm]=useState(inicial),[lista,setLista]=useState({items:[],hay_mas:false}),[evaluaciones,setEvaluaciones]=useState({items:[],hay_mas:false})
  const [offset,setOffset]=useState(0),[evalOffset,setEvalOffset]=useState(0),[refresh,setRefresh]=useState(0)
  const [selected,setSelected]=useState(null),[detail,setDetail]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false)
  const [auditoria,setAuditoria]=useState(null),[auditOffset,setAuditOffset]=useState(0)
  const clave=useRef(null)
  const seleccionActual=useRef(null)
  const lecturaDetalle=useRef(0)
  useEffect(()=>{
    if(!activo)return
    const controller=new AbortController()
    Promise.all([listarCreditos(offset,controller.signal),cargarEvaluaciones(evalOffset,controller.signal)]).then(([l,e])=>{if(!controller.signal.aborted){setLista(l);setEvaluaciones(e);setError('')}}).catch(e=>{if(!controller.signal.aborted)setError(e.message)})
    return()=>controller.abort()
  },[activo,offset,evalOffset,refresh,revision])
  useEffect(()=>{
    if(!activo || !selected)return
    const controller=new AbortController()
    const intento=++lecturaDetalle.current
    cargarCredito(selected,controller.signal).then(d=>{if(!controller.signal.aborted && lecturaDetalle.current===intento && seleccionActual.current===d.id)setDetail(d)}).catch(e=>{if(!controller.signal.aborted && lecturaDetalle.current===intento)setError(e.message)})
    return()=>controller.abort()
  },[activo,selected])
  function elegir(id){seleccionActual.current=id;setDetail(null);setError('');setSelected(id)}
  function editar(next){clave.current=null;setForm(next);setError('')}
  async function crear(event){event.preventDefault();setBusy(true);setError('');try{clave.current ||= crypto.randomUUID();const d=await crearCredito({...form,id:clave.current});seleccionActual.current=d.id;setSelected(d.id);setDetail(d);setRefresh(n=>n+1)}catch(e){setError(e.message)}finally{setBusy(false)}}
  async function auditar(next=0){setBusy(true);setError('');try{setAuditoria(await cargarAuditoria(next));setAuditOffset(next)}catch(e){setError(e.message)}finally{setBusy(false)}}
  return <section id="creditos" className="card ledger">
    <div className="ledger-heading"><div><h2>Créditos y pagos · DEMO</h2><p>Planes ficticios, pagos parciales y alertas trazables. No registra desembolsos ni aprueba solicitudes.</p></div><button type="button" disabled={busy} onClick={()=>setRefresh(n=>n+1)}>Actualizar listado</button></div>
    {!activo&&<p>Abre «Créditos y pagos» en el menú para cargar esta sección.</p>}
    <details><summary>Crear un plan de cuotas ficticio</summary><p>Asocia una evaluación guardada. El monto es el total pactado del plan; no se calculan intereses, tasas o comisiones. Máximo 60 cuotas, una fecha por cuota.</p>
      <form onSubmit={crear}><fieldset disabled={busy}>
        <div className="ledger-grid"><label>Evaluación guardada<select required value={form.evaluacion_id} onChange={e=>editar({...form,evaluacion_id:e.target.value})}><option value="">Elige una evaluación</option>{evaluaciones.items.map(e=><option key={e.id} value={e.id}>{e.rfc} · {e.fecha.slice(0,10)} · {e.nivel_riesgo_preliminar}</option>)}</select></label><label>Concepto ficticio<input required maxLength={100} value={form.concepto} onChange={e=>editar({...form,concepto:e.target.value})} placeholder="Ej. Crédito de demostración"/></label><label>Apertura UTC<input required type="date" max={dia()} value={form.fecha_apertura} onChange={e=>editar({...form,fecha_apertura:e.target.value})}/></label><label>Total pactado · MXN<input required type="number" min="0.01" max="1000000000" step="0.01" value={form.monto_total_pactado} onChange={e=>editar({...form,monto_total_pactado:e.target.value})}/></label></div>
        <div className="ledger-heading"><button type="button" disabled={evalOffset===0} onClick={()=>setEvalOffset(n=>Math.max(0,n-20))}>Evaluaciones anteriores</button><button type="button" disabled={!evaluaciones.hay_mas} onClick={()=>setEvalOffset(n=>n+20)}>Más evaluaciones</button></div>
        {form.cuotas.map((c,n)=><div className="ledger-grid ledger-cuota" key={n}><label>Cuota {n+1} · vencimiento<input type="date" required min={form.fecha_apertura} value={c.vencimiento} onChange={e=>editar({...form,cuotas:form.cuotas.map((q,i)=>i===n?{...q,vencimiento:e.target.value}:q)})}/></label><label>Importe · MXN<input type="number" required min="0.01" max="1000000000" step="0.01" value={c.importe} onChange={e=>editar({...form,cuotas:form.cuotas.map((q,i)=>i===n?{...q,importe:e.target.value}:q)})}/></label><button type="button" disabled={form.cuotas.length===1} onClick={()=>editar({...form,cuotas:form.cuotas.filter((_,i)=>i!==n)})}>Quitar cuota {n+1}</button></div>)}
        <div className="ledger-heading"><button type="button" disabled={form.cuotas.length>=60} onClick={()=>editar({...form,cuotas:[...form.cuotas,{vencimiento:'',importe:''}]})}>Añadir cuota</button><button type="submit">Guardar plan ficticio</button></div><p className="form-footnote">La suma exacta de cuotas debe coincidir con el total y las fechas deben ser únicas y ordenadas. Guardar no cambia el score ni solicita IA.</p>
      </fieldset></form>
    </details>
    {error&&<p role="alert" className="error">{error}</p>}
    <div className="ledger-scroll"><table><caption>Planes registrados</caption><thead><tr><th>Concepto</th><th>Apertura UTC</th><th>Total pactado · MXN</th><th>Detalle</th></tr></thead><tbody>{lista.items.map(c=><tr key={c.id}><td>{c.concepto}</td><td>{c.fecha_apertura}</td><td>{Number(c.monto_total_pactado).toLocaleString('es-MX',{minimumFractionDigits:2})}</td><td><button type="button" disabled={busy} onClick={()=>elegir(c.id)}>Ver pagos y alertas</button></td></tr>)}</tbody></table></div>
    {!lista.items.length&&activo&&<p>No hay planes en esta página. Las evaluaciones anteriores no se convierten automáticamente en créditos.</p>}
    <nav className="ledger-heading" aria-label="Páginas de créditos"><button type="button" disabled={busy || offset===0} onClick={()=>setOffset(n=>Math.max(0,n-20))}>Anterior</button><span>Página {Math.floor(offset/20)+1}</span><button type="button" disabled={busy || !lista.hay_mas} onClick={()=>setOffset(n=>n+20)}>Siguiente</button></nav>
    {detail&&selected===detail.id&&<DetalleCredito key={detail.id} data={detail} onData={next=>{if(seleccionActual.current===next.id){lecturaDetalle.current+=1;setDetail(next)}}}/>}
    {user?.roles?.includes('Administrador')&&<details><summary>Auditoría global del seguimiento</summary><button type="button" disabled={busy} onClick={()=>auditar()}>Consultar eventos</button>{auditoria&&<><PanelAuditoria data={auditoria}/><button type="button" disabled={busy || auditOffset===0} onClick={()=>auditar(Math.max(0,auditOffset-20))}>Anteriores</button><button type="button" disabled={busy || !auditoria.hay_mas} onClick={()=>auditar(auditOffset+20)}>Más eventos</button></>}</details>}
  </section>
}
