import { useEffect, useState } from 'react'
import { fetchAutenticado as fetch } from '../autenticacion/cliente'
import { esPrediccionAzureML, mensajeConexionAzureML } from './estadoConexion.mjs'

const columns = ['LIMIT_BAL', 'PAY_0', ...Array.from({ length: 5 }, (_, i) => `PAY_${i + 2}`), ...Array.from({ length: 6 }, (_, i) => `BILL_AMT${i + 1}`), ...Array.from({ length: 6 }, (_, i) => `PAY_AMT${i + 1}`)]
const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const exampleValues = Object.fromEntries(columns.map(name => [name,
  String(name === 'LIMIT_BAL' ? 200000 : name.startsWith('BILL_AMT') ? 22000 - Number(name.slice(8)) * 2000 : name.startsWith('PAY_AMT') ? 3000 : 0),
]))

export default function AzureMLDemo() {
  const [values, setValues] = useState(Object.fromEntries(columns.map(name => [name, ''])))
  const [configured, setConfigured] = useState(false)
  const [status, setStatus] = useState('Comprobando configuración…')
  const [consulta, setConsulta] = useState('pendiente')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  useEffect(() => {
    const controller = new AbortController()
    fetch(`${api}/api/v1/azure-ml/estado`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(10000)]) })
      .then(response => { if (!response.ok) throw new Error(); return response.json() })
      .then(data => {
        setConfigured(data.configurado === true)
        setStatus(data.configurado ? 'Configuración presente; conexión pendiente de una consulta correcta.' : 'Azure ML todavía no está configurado. No se simulan resultados.')
      })
      .catch(() => { if (!controller.signal.aborted) setStatus('No se pudo comprobar la configuración. Recarga la página después de iniciar la API.') })
    return () => controller.abort()
  }, [])

  async function submit(event) {
    event.preventDefault()
    setBusy(true); setError(''); setResult(null); setConsulta('consultando')
    try {
      const response = await fetch(`${api}/api/v1/azure-ml/predecir`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: AbortSignal.timeout(35000),
        body: JSON.stringify({ valores: Object.fromEntries(columns.map(name => [name, Number(values[name])])) }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Revisa los 19 valores: deben ser enteros dentro de los límites indicados.')
      if (!esPrediccionAzureML(data)) throw new Error('La respuesta de Azure ML no tiene el formato esperado. No hay una predicción disponible.')
      setResult(data)
      setConsulta('correcta')
    } catch (err) {
      setConsulta('fallida')
      setError(err instanceof TypeError || err.name === 'TimeoutError' ? 'No se pudo completar la consulta. Comprueba la conexión.' : err.message)
    }
    finally { setBusy(false) }
  }

  return <section className="card" style={{ marginTop: 24 }} aria-labelledby="azure-heading">
    <h2 id="azure-heading">Laboratorio académico · Azure ML</h2>
    <p>Separado de la evaluación anterior. Usa exclusivamente escenarios ficticios con las 19 variables UCI. Importes en dólares taiwaneses (NTD), no pesos mexicanos. Datos originales: Taiwán, 2005.</p>
    <p role="status">{mensajeConexionAzureML(configured, status, consulta)}</p>
    <details><summary>Abrir formulario UCI</summary>
      <p>LIMIT_BAL: límite de crédito. PAY_0, PAY_2…6: estados de pago de septiembre a abril; códigos originales de −2 a 9, no días de atraso. BILL_AMT1…6: saldos de septiembre a abril (pueden ser negativos). PAY_AMT1…6: pagos de septiembre a abril (no negativos).</p>
      <form onSubmit={submit}>
        <button type="button" disabled={busy} onClick={() => {
          setValues({ ...exampleValues }); setResult(null); setError('')
        }}>Cargar ejemplo ficticio</button>
        <p>Rellena o reemplaza los 19 campos con un escenario ficticio en NTD. No envía ninguna consulta; puedes editarlo antes de consultar Azure.</p>
        <fieldset disabled={busy}><legend>19 valores enteros obligatorios</legend><div className="financial-fields">
          {columns.map(name => <label key={name} htmlFor={`uci-${name}`}>{name}
            <input id={`uci-${name}`} type="number" step="1" required value={values[name]}
              min={name === 'LIMIT_BAL' ? 1 : name.startsWith('PAY_AMT') ? 0 : name.startsWith('PAY_') ? -2 : -2147483648}
              max={name.startsWith('PAY_') && !name.startsWith('PAY_AMT') ? 9 : 2147483647}
              onChange={event => { setValues(current => ({ ...current, [name]: event.target.value })); setResult(null); setError('') }} />
          </label>)}
        </div></fieldset>
        <button disabled={!configured || busy}>{busy ? 'Consultando Azure…' : 'Consultar modelo en Azure'}</button>
      </form>
    </details>
    {error && <p className="error" role="alert">{error}</p>}
    {result && <div role="status"><h3>Clase predicha: {result.incumplimiento_predicho ? 'Incumplimiento' : 'No incumplimiento'}</h3><p>Origen: {result.origen}. Modelo académico UCI; el identificador configurado se conserva en la API y no se renombra por la marca de la interfaz.</p><p>{result.advertencia}</p></div>}
    <p className="notice">No autoriza ni rechaza créditos. En la evaluación guardada detectó el 32 % de los incumplimientos. Esta consulta no se guarda en el historial del formulario principal.</p>
  </section>
}
