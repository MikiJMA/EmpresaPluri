// Marca de presentación. No cambia registros Entra, recursos Azure ni datos guardados.
export const MARCA = 'NexoCredit'
export const EVENTO_SESION_VENCIDA = 'sesion-vencida'

const marcaAnterior = /\bPluriOne(?:\s+S\.?A\.?\s+de\s+C\.?V\.?)?(?![\w-])/gi

export function textoMarca(texto) {
  return texto.replace(marcaAnterior, MARCA)
}

export function presentarDocumentoDemo(item) {
  // Solo adaptamos nuestras dos guías demo, nunca documentos ajenos o expedientes.
  if (!['alcance-proyecto-v1', 'guia-demostracion-v1'].includes(item.fuente)) return item
  const contenido = item.contenido
    .replace(/Se plantea para PluriOne S\.A\. de C\.V\., cuyo nombre comercial es Develop Talent & Technology, dedicada a servicios de consultoría, desarrollo de software y capacitación TI\./g,
      `Esta vista utiliza la marca demostrativa ${MARCA}; no identifica una razón social ni acredita aprobación empresarial.`)
    .replace(/El modelo configurado es `plurione-uci-voting-candidato:1`\./g,
      'Se consulta un modelo académico UCI publicado en Azure ML. El identificador técnico se conserva en la API, no se renombra por el cambio de marca.')
    .replace(marcaAnterior, 'la entidad destinataria')
  return { ...item, titulo: textoMarca(item.titulo), contenido, presentacion_adaptada: true }
}
