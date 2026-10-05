import { formatearConsulta, formatearPeriodo, formatearValor } from './servicio.mjs'

const etiquetas = { disponible: 'Disponible', parcial: 'Datos parciales', sin_configurar: 'Requiere configuración', error: 'No disponible' }

export default function PanelFinanciero({ estado, data, error, reintentar }) {
  const loading = estado === 'cargando'
  return <section className="finance-panel" id="indicadores" aria-labelledby="titulo-indicadores" aria-busy={loading}>
    <header className="finance-heading">
      <div><p className="finance-eyebrow">CONTEXTO ECONÓMICO · MÉXICO</p><h2 id="titulo-indicadores">Indicadores financieros</h2></div>
      <button type="button" className="finance-refresh" onClick={reintentar} disabled={loading}>Volver a consultar</button>
    </header>
    <p className="finance-intro">Fuentes públicas, con el último periodo publicado. No son datos en tiempo real ni historial crediticio; no cambian el riesgo del escenario.</p>
    {loading && <p role="status">Consultando los indicadores financieros…</p>}
    {estado === 'error' && <p className="finance-error" role="alert">{error}</p>}
    {estado === 'lista' && data && <>
      <div className="finance-providers">
        {data.proveedores.map(provider => <article key={provider.id} className="finance-provider" aria-labelledby={`fuente-${provider.id}`}>
          <header><h3 id={`fuente-${provider.id}`}>{provider.nombre}</h3><span className={`finance-status finance-status-${provider.estado}`}>{etiquetas[provider.estado]}</span></header>
          <p className="finance-provider-message" role={provider.estado === 'error' ? 'status' : undefined}>{provider.mensaje}</p>
          {provider.indicadores.length > 0 && <div className="finance-values">
            {provider.indicadores.map(item => <div className="finance-value" key={item.serie}>
              <h4>{item.nombre}</h4><p className="finance-number">{formatearValor(item.valor)}{item.valor !== null && <small>{item.unidad}</small>}</p>
              <p>Periodo: <strong>{formatearPeriodo(item.periodo)}</strong></p>
              <p>{item.frecuencia}</p>
              <a href={item.fuente_url} target="_blank" rel="noopener noreferrer">Fuente · {item.serie}<span className="finance-sr-only"> (abre en otra pestaña)</span> ↗</a>
            </div>)}
          </div>}
          <div className="finance-provenance"><p>{provider.estado === 'sin_configurar' ? 'Configuración comprobada' : 'Último intento de consulta'}: {formatearConsulta(provider.consulta_utc)}</p>
            <p>{provider.en_cache ? 'Respuesta conservada en caché.' : 'Estado procesado por el servidor.'} Próxima renovación a partir de {formatearConsulta(provider.proxima_consulta_utc)}.</p></div>
        </article>)}
      </div>
      <p className="finance-footnote">{data.aviso} La caché del servidor conserva datos durante una hora; los fallos se reintentan después de un minuto. Volver a consultar no fuerza llamadas externas.</p>
    </>}
  </section>
}
