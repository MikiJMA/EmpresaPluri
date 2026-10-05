import { fetchAutenticado } from '../autenticacion/cliente'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export async function solicitarExplicacion(identificador) {
  try {
    const response = await fetchAutenticado(`${api}/api/v1/evaluaciones/${encodeURIComponent(identificador)}/explicacion`, {
      method: 'POST', signal: AbortSignal.timeout(80000),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo generar la explicación.')
    return result
  } catch (err) {
    if (err instanceof TypeError || err.name === 'TimeoutError') {
      throw new Error('No se completó la explicación. El intento puede generar consumo; no se reintentará automáticamente.', { cause: err })
    }
    throw err
  }
}
