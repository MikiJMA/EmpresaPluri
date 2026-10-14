import { presentarResponsable } from '../evaluacion_crediticia/componentes/presentarResponsable.mjs'
import { formatearPesos } from '../interfaz/moneda.mjs'
const moneda=value=>new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(Number(value))
export function PanelCredito({data}) {
  const r=data.resumen
  return <>
    <div className="ledger-metrics">{[['Total pactado',r.total_pactado],['Pagado',r.total_pagado],['Saldo pendiente',r.saldo_pendiente],['Saldo vencido',r.saldo_vencido]].map(([titulo,valor])=><div key={titulo}><span>{titulo} · MXN</span><strong title={moneda(valor)}>{formatearPesos(valor)}</strong></div>)}</div>
    <p className="form-footnote">Resumen redondeado a pesos. El detalle de cuotas y abonos conserva centavos para comprobar saldos exactos.</p>
    <p>Corte UTC: {r.fecha_corte} · Atraso máximo pendiente: {r.dias_atraso_maximo} días.</p>
    <p>Cuotas vencidas completas: {r.cuotas_completas_vencidas} de {r.cuotas_vencidas}. Puntualidad: {r.puntualidad_cuotas_vencidas_pct===null?'Sin cuotas vencidas':`${r.puntualidad_cuotas_vencidas_pct}%`}. Una cuota completada tarde no cuenta como puntual.</p>
    <div className="ledger-scroll"><table><caption>Plan y saldo por cuota</caption><thead><tr><th>Vencimiento</th><th>Pactado</th><th>Pagado</th><th>Saldo</th><th>Estado</th></tr></thead><tbody>{r.cuotas.map(c=><tr key={c.id}><td>{c.vencimiento}</td><td>{moneda(c.importe)}</td><td>{moneda(c.pagado)}</td><td>{moneda(c.saldo)}</td><td>{c.estado}{c.dias_atraso>0?` · ${c.dias_atraso} días`:''}</td></tr>)}</tbody></table></div>
    <details><summary>Indicadores de la captura original</summary><ul>{[['Pagos / ingresos',data.indicadores.pagos_sobre_ingresos_pct,'%'],['Gastos / ingresos',data.indicadores.gastos_sobre_ingresos_pct,'%'],['Deuda / ingreso mensual',data.indicadores.deuda_sobre_ingreso_mensual_veces,' veces']].map(([titulo,valor,unidad])=><li key={titulo}>{titulo}: {valor===null?'No capturado':valor+unidad}</li>)}</ul><p>{data.indicadores.aviso}</p></details>
    <h4>Acciones de seguimiento</h4><ul>{r.acciones_seguimiento.map(a=><li key={a}>{a}</li>)}</ul><p className="form-footnote">{r.aviso}</p>
    <details><summary>Historial de abonos ({data.pagos.length})</summary>{data.pagos.length?<ul>{data.pagos.map(p=><li key={p.id}>{p.fecha_pago}: {moneda(p.importe)} · cuota {r.cuotas.find(c=>c.id===p.cuota_id)?.vencimiento}</li>)}</ul>:<p>No hay pagos registrados. Esto no equivale a consultar una cuenta bancaria.</p>}</details>
  </>
}

export function PanelAuditoria({data}) {
  return <div className="ledger-scroll"><table><caption>Eventos del seguimiento · sólo Administrador</caption><thead><tr><th>Fecha UTC</th><th>Acción</th><th>Responsable</th></tr></thead><tbody>{data.items.map(e=><tr key={e.id}><td>{new Date(e.fecha).toLocaleString('es-MX',{timeZone:'UTC'})}</td><td>{e.accion.replaceAll('_',' ')}</td><td>{presentarResponsable(e.responsable)}</td></tr>)}</tbody></table></div>
}
