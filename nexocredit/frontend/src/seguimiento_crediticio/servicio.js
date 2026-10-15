import { fetchAutenticado as fetch } from '../autenticacion/cliente'
import { leerRespuesta } from '../evaluacion_crediticia/servicios/contratos.mjs'
import { validarCreditos, validarCredito, validarAuditoria, validarEvaluacionesDisponibles } from './contratos.mjs'
const api=(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/,'')
async function pedir(path, validar, signal, body) {
  const timeout=AbortSignal.timeout(15000)
  const response=await fetch(`${api}/api/v1/${path}`,{method:body===undefined?'GET':'POST',signal:signal?AbortSignal.any([signal,timeout]):timeout,
    ...(body===undefined?{}:{headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})})
  return leerRespuesta(response,validar,'seguimiento')
}
export const listarCreditos=(offset,signal)=>pedir(`seguimiento/creditos?limite=20&offset=${offset}`,validarCreditos,signal)
export const cargarCredito=(id,signal)=>pedir(`seguimiento/creditos/${id}`,validarCredito,signal)
export const crearCredito=body=>pedir('seguimiento/creditos',validarCredito,undefined,body)
export const registrarPago=(id,body)=>pedir(`seguimiento/creditos/${id}/pagos`,validarCredito,undefined,body)
export const actualizarAlertas=id=>pedir(`seguimiento/creditos/${id}/actualizar-alertas`,validarCredito,undefined,{})
export const atenderAlerta=(id,body)=>pedir(`seguimiento/alertas/${id}/atender`,validarCredito,undefined,body)
export const cargarEvaluaciones=(offset,signal)=>pedir(`evaluaciones?limite=20&offset=${offset}`,validarEvaluacionesDisponibles,signal)
export const cargarAuditoria=(offset,signal)=>pedir(`seguimiento/auditoria?limite=20&offset=${offset}`,validarAuditoria,signal)
