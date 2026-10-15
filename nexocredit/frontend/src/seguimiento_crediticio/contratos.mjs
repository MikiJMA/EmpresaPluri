import { validarHistorial, esFechaHora } from '../evaluacion_crediticia/servicios/contratos.mjs'

const uuid = v => typeof v === 'string' && /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(v)
const texto = (v, max=1000) => typeof v === 'string' && v.length <= max
const entero = v => Number.isSafeInteger(v) && v >= 0
export function centavos(v) {
  if (typeof v !== 'string' || !/^\d{1,10}\.\d{2}$/.test(v)) throw new Error('Importe de seguimiento inválido.')
  const n=BigInt(v.replace('.',''))
  if (n > 100000000000n) throw new Error('Importe de seguimiento fuera de límite.')
  return n
}
const dinero = v => { try { centavos(v); return true } catch { return false } }
function fecha(v) {
  if (typeof v !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(v) || Number(v.slice(0,4)) < 1) return false
  const parsed=new Date(`${v}T00:00:00Z`)
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0,10) === v
}
const porcentaje = v => v === null || (dinero(v) && centavos(v) <= 10000n)
const ratio = v => v === null || typeof v === 'string' && /^\d{1,340}\.\d{2}$/.test(v)
function exigir(ok) { if (!ok) throw new Error('La respuesta de seguimiento no cumple el contrato. No se muestran cifras inválidas.') }

export function validarCreditos(data) {
  exigir(data && Array.isArray(data.items) && entero(data.limite) && data.limite>=1 && data.limite<=100 && data.items.length<=data.limite && entero(data.offset) && data.offset<=1000000 && typeof data.hay_mas === 'boolean' &&
    data.items.every(i=>i && uuid(i.id) && uuid(i.evaluacion_id) && texto(i.concepto,100) && fecha(i.fecha_apertura) && dinero(i.monto_total_pactado)))
  return data
}
export function validarCredito(data) {
  exigir(data && uuid(data.id) && uuid(data.evaluacion_id) && texto(data.concepto,100) && fecha(data.fecha_apertura) && (data.alertas_revisadas===null || fecha(data.alertas_revisadas)))
  const r=data.resumen
  exigir(r && fecha(r.fecha_corte) && r.moneda==='MXN' && ['total_pactado','total_pagado','saldo_pendiente','saldo_vencido'].every(k=>dinero(r[k])) &&
    entero(r.dias_atraso_maximo) && entero(r.cuotas_vencidas) && entero(r.cuotas_completas_vencidas) && entero(r.cuotas_pagadas_a_tiempo) &&
    porcentaje(r.cumplimiento_cuotas_vencidas_pct) && porcentaje(r.puntualidad_cuotas_vencidas_pct) &&
    Array.isArray(r.cuotas) && r.cuotas.length>=1 && r.cuotas.length<=60 && Array.isArray(r.acciones_seguimiento) && r.acciones_seguimiento.every(i=>texto(i)) && texto(r.aviso))
  exigir(centavos(r.total_pagado)+centavos(r.saldo_pendiente)===centavos(r.total_pactado) && centavos(r.saldo_vencido)<=centavos(r.saldo_pendiente) &&
    r.cuotas_completas_vencidas<=r.cuotas_vencidas && r.cuotas_pagadas_a_tiempo<=r.cuotas_completas_vencidas &&
    (r.cuotas_vencidas===0 ? r.cumplimiento_cuotas_vencidas_pct===null && r.puntualidad_cuotas_vencidas_pct===null : r.cumplimiento_cuotas_vencidas_pct!==null && r.puntualidad_cuotas_vencidas_pct!==null))
  r.cuotas.forEach(c=>exigir(c && uuid(c.id) && fecha(c.vencimiento) && ['importe','pagado','saldo'].every(k=>dinero(c[k])) &&
    centavos(c.pagado)+centavos(c.saldo)===centavos(c.importe) && entero(c.dias_atraso) && ['Pagada','Vencida','Pendiente'].includes(c.estado)))
  exigir(new Set(r.cuotas.map(c=>c.id)).size===r.cuotas.length && r.cuotas.reduce((n,c)=>n+centavos(c.importe),0n)===centavos(r.total_pactado) &&
    r.cuotas.reduce((n,c)=>n+centavos(c.pagado),0n)===centavos(r.total_pagado))
  const i=data.indicadores
  exigir(i && texto(i.aviso) && ['pagos_sobre_ingresos_pct','gastos_sobre_ingresos_pct','deuda_sobre_ingreso_mensual_veces'].every(k=>ratio(i[k])) &&
    (i.margen_capturado===null || typeof i.margen_capturado==='string' && /^-?\d{1,10}\.\d{2}$/.test(i.margen_capturado)))
  exigir(Array.isArray(data.pagos) && data.pagos.length<=500 && data.pagos.every(p=>p && uuid(p.id) && p.credito_id===data.id && r.cuotas.some(c=>c.id===p.cuota_id) && fecha(p.fecha_pago) && dinero(p.importe)) &&
    Array.isArray(data.alertas) && data.alertas.length<=60 && data.alertas.every(a=>a && uuid(a.id) && a.credito_id===data.id && r.cuotas.some(c=>c.id===a.cuota_id) &&
      a.tipo==='CUOTA_VENCIDA' && ['Pendiente','Atendida','Resuelta'].includes(a.estado) && dinero(a.saldo) && entero(a.dias_atraso) && entero(a.version) && a.version>=1 && texto(a.observaciones)))
  exigir(centavos(r.total_pactado)>0n && new Set(data.pagos.map(p=>p.id)).size===data.pagos.length &&
    data.pagos.every(p=>centavos(p.importe)>0n && p.fecha_pago>=data.fecha_apertura && p.fecha_pago<=r.fecha_corte))
  r.cuotas.forEach((c,index)=>{
    const dias=Math.max(0,Math.round((Date.parse(`${r.fecha_corte}T00:00:00Z`)-Date.parse(`${c.vencimiento}T00:00:00Z`))/86400000))
    const atraso=centavos(c.saldo)>0n?dias:0
    exigir(centavos(c.importe)>0n && c.vencimiento>=data.fecha_apertura && (index===0 || c.vencimiento>r.cuotas[index-1].vencimiento) &&
      c.dias_atraso===atraso && c.estado===(centavos(c.saldo)===0n?'Pagada':atraso?'Vencida':'Pendiente') &&
      data.pagos.filter(p=>p.cuota_id===c.id).reduce((n,p)=>n+centavos(p.importe),0n)===centavos(c.pagado))
  })
  const vencidas=r.cuotas.filter(c=>c.vencimiento<r.fecha_corte)
  const completas=vencidas.filter(c=>centavos(c.saldo)===0n).length
  const puntuales=vencidas.filter(c=>data.pagos.filter(p=>p.cuota_id===c.id && p.fecha_pago<=c.vencimiento).reduce((n,p)=>n+centavos(p.importe),0n)===centavos(c.importe)).length
  function pct(n,d){if(!d)return null;const scaled=(BigInt(n)*10000n+BigInt(d)/2n)/BigInt(d);const s=scaled.toString().padStart(3,'0');return `${s.slice(0,-2)}.${s.slice(-2)}`}
  exigir(r.cuotas_vencidas===vencidas.length && r.cuotas_completas_vencidas===completas && r.cuotas_pagadas_a_tiempo===puntuales &&
    r.dias_atraso_maximo===Math.max(...r.cuotas.map(c=>c.dias_atraso)) &&
    r.cuotas.filter(c=>c.dias_atraso>0).reduce((n,c)=>n+centavos(c.saldo),0n)===centavos(r.saldo_vencido) &&
    r.cumplimiento_cuotas_vencidas_pct===pct(completas,vencidas.length) && r.puntualidad_cuotas_vencidas_pct===pct(puntuales,vencidas.length))
  return data
}
export const validarEvaluacionesDisponibles = validarHistorial
export function validarAuditoria(data) {
  exigir(data && Array.isArray(data.items) && data.items.length<=100 && typeof data.hay_mas==='boolean' && entero(data.offset) && entero(data.limite) &&
    data.items.every(e=>e && uuid(e.id) && uuid(e.credito_id) && ['credito_creado','pago_registrado','alerta_recalculada','alerta_atendida'].includes(e.accion) && texto(e.responsable,120) && esFechaHora(e.fecha)))
  return data
}
