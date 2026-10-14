import { useEffect, useState } from 'react'
import { fetchAutenticado } from '../autenticacion/cliente'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export default function EstadoProveedores() {
  const [estado, setEstado] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    const controller = new AbortController()
    fetchAutenticado(`${api}/api/v1/proveedores/estado`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(10000)]) })
      .then(async response => {
        if (!response.ok) throw new Error('No se pudo leer la selección de servicios.')
        const data = await response.json()
        if (!controller.signal.aborted) setEstado(data)
      })
      .catch(err => { if (!controller.signal.aborted) setError(err.message) })
    return () => controller.abort()
  }, [])
  return <details className="provider-selection">
    <summary>Proveedores actuales</summary>
    {error && <p role="alert">{error}</p>}
    {!estado && !error && <p role="status">Leyendo la configuración del servidor…</p>}
    {estado && <ul>{[['explicaciones', 'Explicaciones'], ['documentos', 'Documentos'], ['ml', 'Laboratorio ML']].map(([key, label]) =>
      <li key={key}>{label}: {estado[key]?.origen || estado[key]?.proveedor || 'No disponible'} · {estado[key]?.configurado ? 'Configuración presente' : 'No habilitado'}.</li>)}</ul>}
    <p>La selección no acredita conectividad. Las llaves se editan en el archivo privado del servidor, nunca aquí.</p>
  </details>
}
