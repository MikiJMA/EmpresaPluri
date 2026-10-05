import { agruparGuias } from './servicio.mjs'
import { MARCA, presentarDocumentoDemo } from '../interfaz/marca.mjs'

export default function PanelDocumentos({ consulta, onConsultaChange, submit, busy, error, resultados, catalogo, reintentar }) {
  const fragmentos = (catalogo.fragmentos || []).map(presentarDocumentoDemo)
  const guias = agruparGuias(fragmentos)
  const encontrados = resultados?.map(presentarDocumentoDemo)
  const adaptado = [...fragmentos, ...(encontrados || [])].some(item => item.presentacion_adaptada)
  return <section className="card documents-panel" id="documentos" aria-labelledby="search-heading">
    <h2 id="search-heading">Documentos de demostración · Azure AI Search</h2>
    <p>Consulta el alcance del proyecto y la guía del prototipo. No son políticas oficiales de crédito. No introduzcas datos personales en el buscador.</p>
    <form onSubmit={submit} className="documents-search">
      <label htmlFor="consulta-documentos">Palabras clave (por ejemplo: margen, tecnologías o incumplimiento)</label>
      <input id="consulta-documentos" value={consulta} minLength={2} maxLength={200} required disabled={busy}
        onChange={event => onConsultaChange(event.target.value)} />
      <button type="submit" disabled={busy || consulta.trim().length < 2}>{busy ? 'Buscando…' : 'Buscar documentos'}</button>
    </form>
    {error && <p role="alert" className="error">{error}</p>}
    <div aria-live="polite" aria-busy={busy}>
      {busy && <p role="status">Buscando fragmentos en Azure AI Search…</p>}
      {resultados !== null && <div className="documents-results">
        <h3>Resultados de búsqueda</h3>
        <p>{resultados.length ? `${resultados.length} fragmentos recuperados de Azure AI Search.` : 'No se encontraron coincidencias. Prueba con menos palabras.'}</p>
        {encontrados.map(item => <article key={item.id} className="documents-fragment">
          <h4>{item.seccion}</h4>
          <p className="documents-source">Fuente: {item.titulo} · {item.fuente} · versión {item.version}</p>
          <p className="documents-text">{item.contenido}</p>
          <small>{item.aviso}</small>
        </article>)}
      </div>}
    </div>
    <div className="documents-catalog" aria-live="polite" aria-busy={catalogo.estado === 'cargando'}>
      <h3>Guías disponibles</h3>
      {catalogo.estado === 'cargando' && <p role="status">Cargando las guías desde Azure AI Search…</p>}
      {catalogo.estado === 'error' && <div><p role="alert" className="error">{catalogo.error}</p><button type="button" onClick={reintentar}>Reintentar carga de guías</button></div>}
      {catalogo.estado === 'lista' && <>
        <p>{guias.length ? `${guias.length} ${guias.length === 1 ? 'guía' : 'guías'} · ${catalogo.fragmentos.length} ${catalogo.fragmentos.length === 1 ? 'sección' : 'secciones'}. Abre una guía para leer su contenido.` : 'Todavía no hay guías disponibles en el índice de Azure AI Search.'}</p>
        <div className="documents-guides">{guias.map(guia => <article className="documents-guide" key={guia.key}>
          <h4>{guia.titulo}</h4>
          <p className="documents-source">Fuente: {guia.fuente} · versión {guia.version}</p>
          <p className="documents-excerpt">{guia.secciones[0].contenido.length > 240 ? `${guia.secciones[0].contenido.slice(0, 240)}…` : guia.secciones[0].contenido}</p>
          <details>
            <summary>Leer guía · {guia.secciones.length} {guia.secciones.length === 1 ? 'sección' : 'secciones'}</summary>
            {guia.secciones.map(item => <section className="documents-fragment" key={item.id}>
              <h5>{item.seccion}</h5><p className="documents-text">{item.contenido}</p>
            </section>)}
          </details>
          <small>{guia.aviso}</small>
        </article>)}</div>
      </>}
    </div>
    <p className="documents-note">{adaptado ? `Presentación de las guías demo adaptada a ${MARCA}; se conservan sus identificadores y la versión de fuente. El contenido original en Azure AI Search no se modifica.` : 'Contenido original recuperado de Azure AI Search.'} No genera respuestas con IA ni recomendaciones de aprobación.</p>
  </section>
}
