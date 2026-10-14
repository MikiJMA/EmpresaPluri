export const SAT_CURP_URL = 'https://wwwmat.sat.gob.mx/aplicacion/31274/consulta-tu-clave-de-rfc-mediante-curp'

export function crearRevisionIdentidad(fetchApi, baseApi) {
  return async (rfc, curp, signal) => {
    const response = await fetchApi(`${baseApi.replace(/\/$/, '')}/api/v1/identidad/revisar`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
      body: JSON.stringify({ rfc, curp: curp || null }),
    })
    if (!response.ok) throw new Error('No se pudo revisar el RFC y la CURP. Revisa su longitud y la conexión.')
    let data
    try { data = await response.json() } catch { throw new Error('La revisión de identidad no tiene el formato esperado.') }
    if (!['formato_correcto', 'formato_invalido', 'coherencia_basica', 'no_coincide'].includes(data?.estado) ||
        data.verificacion_oficial !== false || data.fuente_url !== SAT_CURP_URL || typeof data.mensaje !== 'string' ||
        data.mensaje.length > 500 || !Array.isArray(data.comprobaciones) || data.comprobaciones.length < 1 || data.comprobaciones.length > 3 ||
        !data.comprobaciones.every(i => i && ['RFC', 'CURP', 'Fecha'].includes(i.campo) && typeof i.correcto === 'boolean' && typeof i.detalle === 'string' && i.detalle.length <= 300)) {
      throw new Error('La revisión de identidad no tiene el formato esperado.')
    }
    return data
  }
}
