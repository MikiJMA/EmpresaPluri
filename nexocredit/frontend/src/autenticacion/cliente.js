import { EVENTO_SESION_VENCIDA, MARCA } from '../interfaz/marca.mjs'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
let configuration
let initialization
// La sesión local existe solo en memoria: no contraseña ni JWT en localStorage.
let localSession
let intentoLocal = 0

export function prepararSesion() {
  if (!configuration) configuration = (async () => {
    const response = await fetch(`${api}/api/v1/auth/config`, { signal: AbortSignal.timeout(10000) })
    if (!response.ok) throw new Error('No se pudo cargar la configuración de acceso.')
    const config = await response.json()
    return { config }
  })().catch(error => { configuration = undefined; throw error })
  return configuration
}

export function prepararMicrosoft() {
  if (!initialization) initialization = (async () => {
    const { config } = await prepararSesion()
    const { PublicClientApplication } = await import('@azure/msal-browser')
    const msal = new PublicClientApplication({
      auth: { clientId: config.clientId, authority: `https://login.microsoftonline.com/${config.tenantId}`,
        redirectUri: config.redirectUri, postLogoutRedirectUri: config.redirectUri,
        navigateToLoginRequestUrl: false },
      cache: { cacheLocation: 'sessionStorage' },
    })
    await msal.initialize()
    const result = await msal.handleRedirectPromise()
    if (result?.account) msal.setActiveAccount(result.account)
    else if (!msal.getActiveAccount() && msal.getAllAccounts().length === 1) msal.setActiveAccount(msal.getAllAccounts()[0])
    return { msal, config }
  })().catch(error => { initialization = undefined; throw error })
  return initialization
}

export async function iniciarSesion() {
  limpiarSesionLocal()
  const { msal, config } = await prepararMicrosoft()
  await msal.loginRedirect({ scopes: [config.scope], prompt: 'select_account' })
}

export async function cerrarSesion() {
  if (localSession) { limpiarSesionLocal(); return }
  const { msal } = await prepararMicrosoft()
  await msal.logoutRedirect({ account: msal.getActiveAccount() })
}

export function limpiarSesionLocal() { localSession = undefined; intentoLocal += 1 }

export async function iniciarSesionLocal(usuario, password) {
  limpiarSesionLocal()
  const intento = intentoLocal
  const response = await fetch(`${api}/api/v1/auth/local/login`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, redirect: 'error',
    signal: AbortSignal.timeout(15000), body: JSON.stringify({ usuario, password }),
  })
  const data = await response.json()
  if (intentoLocal !== intento) throw new Error('Este intento de acceso fue reemplazado por uno más reciente.')
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo iniciar sesión local.')
  if (typeof data.access_token !== 'string' || data.token_type !== 'bearer'
      || !Number.isFinite(data.expires_in) || data.expires_in <= 0) {
    throw new Error('La respuesta del acceso local no tiene el formato esperado.')
  }
  localSession = { token: data.access_token, expiresAt: Date.now() + data.expires_in * 1000 }
  const sesionCreada = localSession
  try { return await verificarUsuario() }
  catch (error) { if (localSession === sesionCreada) limpiarSesionLocal(); throw error }
}

export async function fetchAutenticado(url, options = {}) {
  const expected = new URL(`${api}/api/`, window.location.origin)
  const target = new URL(url, window.location.origin)
  if (target.origin !== expected.origin || !target.pathname.startsWith(expected.pathname)) {
    throw new Error(`La solicitud no pertenece a la API de ${MARCA}.`)
  }
  let accessToken
  const sesionUtilizada = localSession
  const intentoUtilizado = intentoLocal
  try {
    if (localSession) {
      if (Date.now() >= localSession.expiresAt) throw new Error('Sesión local vencida')
      accessToken = localSession.token
    } else {
      const { msal, config } = await prepararMicrosoft()
      const account = msal.getActiveAccount()
      if (!account) throw new Error('Sin sesión')
      const token = await msal.acquireTokenSilent({ account, scopes: [config.scope] })
      accessToken = token.accessToken
    }
  } catch {
    if (localSession === sesionUtilizada && intentoLocal === intentoUtilizado) {
      limpiarSesionLocal()
      window.dispatchEvent(new Event(EVENTO_SESION_VENCIDA))
    }
    throw new Error('Vuelve a iniciar sesión para continuar.')
  }
  const headers = new Headers(options.headers)
  headers.set('Authorization', `Bearer ${accessToken}`)
  const response = await fetch(url, { ...options, headers, redirect: 'error' })
  if (response.status === 401) {
    if (localSession === sesionUtilizada && intentoLocal === intentoUtilizado) {
      limpiarSesionLocal()
      window.dispatchEvent(new Event(EVENTO_SESION_VENCIDA))
    }
    throw new Error('La sesión no es válida. Inicia sesión nuevamente.')
  }
  if (response.status === 403) throw new Error(`Acceso denegado. Tu usuario necesita un rol autorizado de ${MARCA}.`)
  return response
}

export async function verificarUsuario() {
  const response = await fetchAutenticado(`${api}/api/v1/auth/me`, { signal: AbortSignal.timeout(20000) })
  if (!response.ok) throw new Error('El servidor no pudo verificar tu identidad. Intenta más tarde.')
  return response.json()
}
