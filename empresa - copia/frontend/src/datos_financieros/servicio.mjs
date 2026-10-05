const series = { banxico: ['SF43718', 'SF61745'], banco_mundial: ['FP.CPI.TOTL.ZG', 'NY.GDP.MKTP.KD.ZG'] }
const estados = ['disponible', 'parcial', 'sin_configurar', 'error']
const fechaValida = value => typeof value === 'string' && Number.isFinite(Date.parse(value))

export function validarIndicadores(payload) {
  const invalid = () => { throw new Error('Los indicadores no tienen el formato esperado.') }
  if (payload?.pais !== 'MX' || typeof payload.aviso !== 'string' || payload.cache_segundos !== 3600 ||
      !Array.isArray(payload.proveedores) || payload.proveedores.length !== 2) invalid()
  const seen = new Set()
  for (const provider of payload.proveedores) {
    if (!provider || !Object.hasOwn(series, provider.id) || seen.has(provider.id) ||
        !estados.includes(provider.estado) || typeof provider.nombre !== 'string' || typeof provider.mensaje !== 'string' ||
        !fechaValida(provider.consulta_utc) || !fechaValida(provider.proxima_consulta_utc) ||
        typeof provider.en_cache !== 'boolean' || !Array.isArray(provider.indicadores)) invalid()
    seen.add(provider.id)
    const available = ['disponible', 'parcial'].includes(provider.estado)
    if (provider.indicadores.length !== (available ? 2 : 0)) invalid()
    const codes = new Set()
    for (const item of provider.indicadores) {
      if (!item || !series[provider.id].includes(item.serie) || codes.has(item.serie) ||
          !['nombre', 'unidad', 'frecuencia'].every(key => typeof item[key] === 'string') ||
          !(item.valor === null || (typeof item.valor === 'number' && Number.isFinite(item.valor))) ||
          item.estado !== (item.valor === null ? 'sin_dato' : 'disponible') ||
          !(item.periodo === null || (typeof item.periodo === 'string' &&
            (provider.id === 'banco_mundial' ? /^\d{4}$/.test(item.periodo) : /^\d{4}-\d{2}-\d{2}$/.test(item.periodo))))) invalid()
      const expected = provider.id === 'banxico'
        ? 'https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp'
        : `https://data.worldbank.org/indicator/${item.serie}?locations=MX`
      if (item.fuente_url !== expected || (item.valor !== null && item.periodo === null)) invalid()
      codes.add(item.serie)
    }
  }
  return payload
}

export function crearServicioFinanciero(fetchApi, baseApi) {
  return async signal => {
    const response = await fetchApi(`${baseApi.replace(/\/$/, '')}/api/v1/datos-financieros/indicadores`,
      { method: 'GET', signal })
    if (!response.ok) throw new Error('No se pudieron consultar los indicadores. Intenta nuevamente.')
    let payload
    try { payload = await response.json() } catch { throw new Error('Los indicadores no tienen el formato esperado.') }
    return validarIndicadores(payload)
  }
}

export function formatearValor(value) {
  return value === null ? 'Sin dato' : new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 4 }).format(value)
}

export function formatearPeriodo(period) {
  if (period === null) return 'No informado'
  if (/^\d{4}$/.test(period)) return `Año ${period}`
  return new Intl.DateTimeFormat('es-MX', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${period}T00:00:00Z`))
}

export function formatearConsulta(timestamp) {
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'UTC' }).format(new Date(timestamp)) + ' UTC'
}
