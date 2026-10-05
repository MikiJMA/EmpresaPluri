import { PublicClientApplication } from '@azure/msal-browser'
import { EVENTO_SESION_VENCIDA, MARCA } from '../interfaz/marca.mjs'

const api = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
let initialization

export function prepararSesion() {
  if (!initialization) initialization = (async () => {
    const response = await fetch(`${api}/api/v1/auth/config`, { signal: AbortSignal.timeout(10000) })
    if (!response.ok) throw new Error('No se pudo cargar la configuración de acceso.')
    const config = await response.json()
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
  })()
  return initialization
}

export async function iniciarSesion() {
  const { msal, config } = await prepararSesion()
  await msal.loginRedirect({ scopes: [config.scope], prompt: 'select_account' })
}

export async function cerrarSesion() {
  const { msal } = await prepararSesion()
  await msal.logoutRedirect({ account: msal.getActiveAccount() })
}

export async function fetchAutenticado(url, options = {}) {
  const { msal, config } = await prepararSesion()
  const expected = new URL(`${api}/api/`, window.location.origin)
  const target = new URL(url, window.location.origin)
  if (target.origin !== expected.origin || !target.pathname.startsWith(expected.pathname)) {
    throw new Error(`La solicitud no pertenece a la API de ${MARCA}.`)
  }
  let token
  try {
    const account = msal.getActiveAccount()
    if (!account) throw new Error('Sin sesión')
    token = await msal.acquireTokenSilent({ account, scopes: [config.scope] })
  } catch {
    window.dispatchEvent(new Event(EVENTO_SESION_VENCIDA))
    throw new Error('Vuelve a iniciar sesión con Microsoft para continuar.')
  }
  const headers = new Headers(options.headers)
  headers.set('Authorization', `Bearer ${token.accessToken}`)
  const response = await fetch(url, { ...options, headers, redirect: 'error' })
  if (response.status === 401) {
    window.dispatchEvent(new Event(EVENTO_SESION_VENCIDA))
    throw new Error('La sesión no es válida. Inicia sesión nuevamente.')
  }
  if (response.status === 403) throw new Error(`Acceso denegado. Tu usuario necesita un rol de ${MARCA} y el permiso access_as_user.`)
  return response
}

export async function verificarUsuario() {
  const response = await fetchAutenticado(`${api}/api/v1/auth/me`, { signal: AbortSignal.timeout(20000) })
  if (!response.ok) throw new Error('El servidor no pudo verificar tu identidad. Intenta más tarde.')
  return response.json()
}
