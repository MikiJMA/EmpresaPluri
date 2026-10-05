import { textoMarca } from '../interfaz/marca.mjs'

export default function Explicacion({ estado }) {
  const data = estado?.data
  const error = estado?.error
  const busy = estado?.estado === 'generando'
  return <div className="bento-cell enterprise-ai-panel" aria-busy={busy}>
    <h3>Explicación con Azure OpenAI</h3>
    <p>La explicación se genera automáticamente después de guardar la evaluación. Se envían ingresos, gastos, score y resultado a Azure, sin RFC, junto con la guía demo de Azure AI Search. Solo datos ficticios; cada nueva evaluación puede generar consumo de pago.</p>
    <p role="status">{busy ? 'Generando explicación con IA…' : data ? 'Explicación generada automáticamente' : 'Explicación no disponible'}</p>
    {error && <p role="alert">{error} La evaluación permanece guardada y no se reintentará la explicación automáticamente.</p>}
    {data && <div aria-live="polite">
      <p style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{textoMarca(data.explicacion)}</p>
      {data.fuentes.map(item => <p key={item.id}>Guía utilizada: {textoMarca(item.titulo)} · {item.seccion} · versión de fuente {item.version}</p>)}
      <small>Los nombres de marca se adaptan a esta interfaz; se conservan las referencias de fuente.</small>
      <small>{data.aviso} Implementación: {data.implementacion}</small>
    </div>}
  </div>
}
