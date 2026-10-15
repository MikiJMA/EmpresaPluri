import { useRef, useState } from 'react'
import { registrarPago, actualizarAlertas, atenderAlerta } from './servicio'
import { PanelCredito } from './PanelCredito'

const moneda=value=>new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(Number(value))

export default function DetalleCredito({data,onData}) {
  const [busy,setBusy]=useState(false),[error,setError]=useState('')
  const [pago,setPago]=useState({cuota_id:'',importe:'',fecha_pago:new Date().toISOString().slice(0,10)})
  const [notas,setNotas]=useState({})
  const pagoKey=useRef(null),atencionKeys=useRef({})
  function cambio(event){pagoKey.current=null;setPago(prev=>({...prev,[event.target.name]:event.target.value}));setError('')}
  async function ejecutar(fn){setBusy(true);setError('');try{onData(await fn());return true}catch(e){setError(e.message || 'No se completó el seguimiento.');return false}finally{setBusy(false)}}
  async function pagar(event){
    event.preventDefault();pagoKey.current ||= crypto.randomUUID()
    if(await ejecutar(()=>registrarPago(data.id,{...pago,id:pagoKey.current}))){pagoKey.current=null;setPago(prev=>({...prev,importe:'',cuota_id:''}))}
  }
  async function atender(a){
    atencionKeys.current[a.id] ||= crypto.randomUUID()
    if(await ejecutar(()=>atenderAlerta(a.id,{id:atencionKeys.current[a.id],version_anterior:a.version,observaciones:notas[a.id] || ''}))){atencionKeys.current[a.id]=null;setNotas(prev=>({...prev,[a.id]:''}))}
  }
  return <div className="ledger-detail" aria-busy={busy}>
    <h3>{data.concepto}</h3><PanelCredito data={data}/>
    <h4>Registrar pago ficticio</h4><form onSubmit={pagar}><fieldset disabled={busy} className="ledger-grid">
      <label>Cuota<select name="cuota_id" value={pago.cuota_id} onChange={cambio} required><option value="">Selecciona una cuota</option>{data.resumen.cuotas.filter(c=>Number(c.saldo)>0).map(c=><option key={c.id} value={c.id}>{c.vencimiento} · saldo {moneda(c.saldo)}</option>)}</select></label>
      <label>Importe recibido · MXN<input name="importe" type="number" min="0.01" max="1000000000" step="0.01" value={pago.importe} onChange={cambio} required/></label>
      <label>Fecha de pago UTC<input name="fecha_pago" type="date" min={data.fecha_apertura} max={new Date().toISOString().slice(0,10)} value={pago.fecha_pago} onChange={cambio} required/></label>
      <button type="submit">Registrar abono</button>
    </fieldset></form>
    <div className="ledger-heading"><h4>Alertas de cuotas vencidas</h4><button type="button" disabled={busy} onClick={()=>ejecutar(()=>actualizarAlertas(data.id))}>Actualizar vencimientos</button></div>
    <p className="form-footnote">Última revisión de alertas: {data.alertas_revisadas || 'Sin revisión'}. Se recalculan al crear el plan, registrar pagos o pulsar actualizar; no existe vigilancia automática en segundo plano. Atendida no significa pagada.</p>
    {data.alertas.length?data.alertas.map(a=><article className={`ledger-alert ledger-alert-${a.estado.toLowerCase()}`} key={a.id}>
      <strong>{a.estado} · cuota {data.resumen.cuotas.find(c=>c.id===a.cuota_id)?.vencimiento}</strong>
      <p>Saldo en última revisión: {moneda(a.saldo)} · {a.dias_atraso} días de atraso.</p>
      {a.observaciones&&<p>{a.observaciones}</p>}
      {a.estado!=='Resuelta'&&<>
        <label>Motivo de atención<textarea maxLength={1000} value={notas[a.id]||''} disabled={busy}
          onChange={e=>{atencionKeys.current[a.id]=null;setNotas(prev=>({...prev,[a.id]:e.target.value}))}}/></label>
        <button type="button" disabled={busy || !(notas[a.id]||'').trim()} onClick={()=>atender(a)}>Registrar atención</button>
      </>}
    </article>):<p>No se han detectado alertas en el último recálculo.</p>}
    {error&&<p role="alert" className="error">{error}</p>}
  </div>
}
