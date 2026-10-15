import { fetchAutenticado } from '../autenticacion/cliente'
import { leerRespuesta, validarExplicacion } from '../evaluacion_crediticia/servicios/contratos.mjs'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export async function solicitarExplicacion(identificador) {
  try {
    const response = await fetchAutenticado(`${api}/api/v1/evaluaciones/${encodeURIComponent(identificador)}/explicacion`, {
      method: 'POST', signal: AbortSignal.timeout(80000),
    })
    return await leerRespuesta(response, validarExplicacion, 'explicación')
  } catch (err) {
    if (err instanceof TypeError || err.name === 'TimeoutError') {
      throw new Error('No se completó la explicación. El intento puede generar consumo; no se reintentará automáticamente.', { cause: err })
    }
    throw err
  }
}
