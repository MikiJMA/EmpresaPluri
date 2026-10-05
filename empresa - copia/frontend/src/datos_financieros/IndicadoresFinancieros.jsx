import { useEffect, useState } from 'react'
import { fetchAutenticado } from '../autenticacion/cliente'
import { crearServicioFinanciero } from './servicio.mjs'
import PanelFinanciero from './PanelFinanciero'
import './Finanzas.css'

const servicio = crearServicioFinanciero(fetchAutenticado, (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'))

export default function IndicadoresFinancieros() {
  const [revision, setRevision] = useState(0)
  const [resultado, setResultado] = useState({ estado: 'cargando' })
  useEffect(() => {
    const controller = new AbortController()
    const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(35000)])
    servicio(signal).then(
      data => { if (!controller.signal.aborted) setResultado({ estado: 'lista', data }) },
      err => { if (!controller.signal.aborted) setResultado({ estado: 'error',
        error: err instanceof TypeError || signal.aborted ? 'No se pudo completar la consulta. Revisa la conexión e intenta nuevamente.' : err.message }) },
    )
    return () => controller.abort()
  }, [revision])
  function reintentar() {
    setResultado({ estado: 'cargando' })
    setRevision(value => value + 1)
  }
  return <PanelFinanciero {...resultado} reintentar={reintentar} />
}
