import { useEffect, useRef, useState } from 'react'
import { fetchAutenticado as fetch } from '../autenticacion/cliente'
import { COLUMNAS_UCI, construirEscenario, esPrediccionML, validarEstadoML } from './estadoConexion.mjs'
import PanelLaboratorio from './PanelLaboratorio'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const exampleValues = Object.fromEntries(COLUMNAS_UCI.map(name => [name,
  String(name === 'LIMIT_BAL' ? 200000 : name.startsWith('BILL_AMT') ? 22000 - Number(name.slice(8)) * 2000 : name.startsWith('PAY_AMT') ? 3000 : 0),
]))

export default function AzureMLDemo() {
  const [values, setValues] = useState(Object.fromEntries(COLUMNAS_UCI.map(name => [name, ''])))
  const [estado, setEstado] = useState(null)
  const [status, setStatus] = useState('Comprobando configuración…')
  const [consulta, setConsulta] = useState('pendiente')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const intentoActual = useRef(0)
  const peticion = useRef(null)
  useEffect(() => {
    const controller = new AbortController()
    fetch(`${api}/api/v1/ml/estado`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(10000)]) })
      .then(response => { if (!response.ok) throw new Error(); return response.json() })
      .then(data => {
        if (controller.signal.aborted) return
        const config = validarEstadoML(data)
        setEstado(config)
        setStatus(config.motivo || (config.configurado ? 'Configuración presente; ejecución pendiente de una consulta correcta.' : 'El modelo seleccionado no está configurado. No se simulan resultados.'))
      })
      .catch(() => { if (!controller.signal.aborted) setStatus('No se pudo comprobar el laboratorio. Recarga después de iniciar la API.') })
    return () => { controller.abort(); intentoActual.current += 1; peticion.current?.abort() }
  }, [])

  function cambiar(name, value) {
    if (busy) return
    intentoActual.current += 1
    setValues(current => ({ ...current, [name]: value }))
    setResult(null); setError(''); setConsulta('pendiente')
  }
  function cargarEjemplo() {
    if (busy) return
    intentoActual.current += 1
    setValues({ ...exampleValues }); setResult(null); setError(''); setConsulta('pendiente')
  }
  async function submit(event) {
    event.preventDefault()
    if (!estado?.configurado || busy) return
    const intento = ++intentoActual.current
    setResult(null); setError('')
    let payload
    try { payload = construirEscenario(values) }
    catch (err) { setError(err.message); setConsulta('fallida'); return }
    const controller = new AbortController()
    peticion.current = controller
    setBusy(true); setConsulta('consultando')
    try {
      const response = await fetch(`${api}/api/v1/ml/predecir`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.any([controller.signal, AbortSignal.timeout(35000)]), body: JSON.stringify(payload),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo completar la consulta; revisa los valores UCI.')
      if (!esPrediccionML(data, estado)) throw new Error('La respuesta del modelo no tiene el contrato esperado. No hay predicción disponible.')
      if (intentoActual.current !== intento) return
      setResult(data); setConsulta('correcta')
    } catch (err) {
      if (intentoActual.current !== intento) return
      setConsulta('fallida')
      setError(err instanceof TypeError || err.name === 'TimeoutError' ? 'No se pudo completar la consulta. Comprueba la conexión.' : err.message)
    } finally {
      if (intentoActual.current === intento) setBusy(false)
      if (peticion.current === controller) peticion.current = null
    }
  }
  return <PanelLaboratorio values={values} estado={estado} status={status} consulta={consulta} busy={busy}
    error={error} result={result} submit={submit} change={cambiar} cargarEjemplo={cargarEjemplo} />
}
