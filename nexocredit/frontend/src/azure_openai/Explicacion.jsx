import { textoMarca } from '../interfaz/marca.mjs'
import { esExplicacionRenderizable } from '../evaluacion_crediticia/servicios/contratos.mjs'

export default function Explicacion({ estado }) {
  const data = estado?.data
  const error = estado?.error
  if (data && !esExplicacionRenderizable(data)) return <div className="card" role="alert">La explicación recibida no tiene formato válido. Tu evaluación sigue guardada; no se reintentó la generación.</div>
  const busy = estado?.estado === 'generando'
  const proveedor = data?.proveedor
  const origen = proveedor === 'ollama' ? 'Ollama local' : proveedor === 'local' ? 'Reglas locales (sin IA generativa)' : proveedor === 'azure' ? 'Azure OpenAI' : 'Proveedor configurado'
  return <div className="bento-cell enterprise-ai-panel" aria-busy={busy}>
    <h3>Explicación del escenario</h3>
    <p>Se genera automáticamente después de guardar la evaluación, usando ingresos, gastos, score y resultado, sin RFC ni identidad. Solo datos ficticios. El proveedor se selecciona en la configuración privada del servidor; no se cambia automáticamente si falla.</p>
    <p className="form-footnote">El texto y sus referencias se conservan en una caché privada de PostgreSQL y se reutilizan durante 24 horas. Vencer no los borra automáticamente. Máximo diez nuevos intentos por cuenta y hora; consultar una explicación vigente no inicia otra generación.</p>
    {data && <p>Proveedor: {origen}. {proveedor === 'azure' ? 'La consulta puede generar consumo de pago en Azure.' : proveedor === 'ollama' ? 'El modelo se ejecuta en tu equipo, sin enviar la solicitud a Azure.' : proveedor === 'local' ? 'Explicación determinista de las reglas demo; no fue generada por un modelo de IA.' : ''}</p>}
    <p role="status">{busy ? 'Generando explicación con el proveedor seleccionado…' : data ? 'Explicación generada automáticamente' : 'Explicación no disponible'}</p>
    {error && <p role="alert">{error} La evaluación permanece guardada y no se reintentará la explicación automáticamente.</p>}
    {data && <div aria-live="polite">
      <p style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{textoMarca(data.explicacion)}</p>
      {data.fuentes.map(item => <p key={item.id}>Guía utilizada: {textoMarca(item.titulo)} · {item.seccion} · versión de fuente {item.version}</p>)}
      <small>Los nombres de marca se adaptan a esta interfaz; se conservan las referencias de fuente.</small>
      <small>{data.aviso} Implementación: {data.implementacion}</small>
    </div>}
  </div>
}
