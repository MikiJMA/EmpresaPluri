import { useEffect, useState } from 'react'
import { fetchAutenticado } from '../autenticacion/cliente'
import { crearServicioDocumentos } from './servicio.mjs'
import PanelDocumentos from './PanelDocumentos'
import './Documentos.css'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const servicio = crearServicioDocumentos(fetchAutenticado, api)

function mensajeError(err) {
  return err instanceof TypeError || err.name === 'TimeoutError'
    ? 'No se pudieron recuperar los documentos. Comprueba la conexión.' : err.message
}

export default function BuscadorDocumentos() {
  const [consulta, setConsulta] = useState('')
  const [resultados, setResultados] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [catalogo, setCatalogo] = useState({ estado: 'cargando' })
  const [intentoCatalogo, setIntentoCatalogo] = useState(0)
  const [proveedorBusqueda, setProveedorBusqueda] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(14000)])
    servicio.listarConOrigen(signal).then(
      data => { if (!controller.signal.aborted) setCatalogo({ estado: 'lista', fragmentos: data.resultados, proveedor: data.proveedor || 'azure' }) },
      err => { if (!controller.signal.aborted) setCatalogo({ estado: 'error', error: mensajeError(err) }) },
    )
    return () => controller.abort()
  }, [intentoCatalogo])

  function reintentar() {
    setCatalogo({ estado: 'cargando' })
    setIntentoCatalogo(current => current + 1)
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true); setError(''); setResultados(null)
    try {
      const data = await servicio.buscarConOrigen(consulta, AbortSignal.timeout(14000))
      setResultados(data.resultados)
      setProveedorBusqueda(data.proveedor || 'azure')
    } catch (err) {
      setError(mensajeError(err))
    } finally { setBusy(false) }
  }

  return <PanelDocumentos consulta={consulta} busy={busy} error={error} resultados={resultados}
    proveedorBusqueda={proveedorBusqueda}
    catalogo={catalogo} submit={submit} reintentar={reintentar}
    onConsultaChange={value => { setConsulta(value); setResultados(null); setError('') }} />
}
