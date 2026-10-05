// Cliente sin credenciales propias: todas las solicitudes usan fetchAutenticado.
export function crearServicioDocumentos(fetchApi, baseApi) {
  const base = `${baseApi.replace(/\/$/, '')}/api/v1/azure-search`
  async function consultar(ruta, options) {
    const response = await fetchApi(`${base}/${ruta}`, options)
    const data = await response.json()
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudieron recuperar los documentos.')
    if (!Array.isArray(data.resultados) || data.resultados.some(item =>
      !item || ['id', 'fuente', 'titulo', 'seccion', 'contenido', 'version', 'aviso'].some(field => typeof item[field] !== 'string'))) {
      throw new Error('La respuesta de documentos no tiene el formato esperado.')
    }
    return data.resultados
  }
  return {
    listar: signal => consultar('documentos', { method: 'GET', signal }),
    buscar: (consulta, signal) => consultar('buscar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
      body: JSON.stringify({ consulta: consulta.trim() }),
    }),
  }
}

export function agruparGuias(fragmentos) {
  const guias = new Map()
  for (const item of fragmentos) {
    const key = JSON.stringify([item.fuente, item.version])
    if (!guias.has(key)) guias.set(key, { key, titulo: item.titulo, fuente: item.fuente, version: item.version, aviso: item.aviso, secciones: [] })
    guias.get(key).secciones.push(item)
  }
  return [...guias.values()].map(guia => ({ ...guia,
    secciones: [...guia.secciones].sort((a, b) => a.seccion.localeCompare(b.seccion, 'es', { numeric: true })),
  }))
}
