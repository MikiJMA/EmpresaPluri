import { useEffect, useState } from 'react'
import { prepararSesion, iniciarSesion, cerrarSesion, verificarUsuario } from './cliente'
import { UsuarioContext } from './contexto'
import PantallaAcceso from './PantallaAcceso'
import { EVENTO_SESION_VENCIDA } from '../interfaz/marca.mjs'
import '../styles/Acceso.css'

export default function Acceso({ children }) {
  const [user, setUser] = useState(null)
  const [busy, setBusy] = useState(true)
  const [error, setError] = useState('')
  const [ready, setReady] = useState(false)
  const [wrongOrigin, setWrongOrigin] = useState(false)
  useEffect(() => {
    let cancelled = false
    function expired() { setUser(null); setError('Tu sesión requiere verificación. Vuelve a iniciar sesión.') }
    window.addEventListener(EVENTO_SESION_VENCIDA, expired)
    prepararSesion().then(async ({ msal, config }) => {
      if (cancelled) return
      setReady(true)
      if (window.location.origin !== new URL(config.redirectUri).origin) { setWrongOrigin(true); return }
      if (msal.getActiveAccount()) {
        const verified = await verificarUsuario()
        if (!cancelled) setUser(verified)
      }
    }).catch(err => { if (!cancelled) setError(err.message?.startsWith('Acceso denegado') ? err.message : 'No se pudo verificar el acceso. Revisa la conexión y vuelve a iniciar sesión; si continúa, recarga la página.') })
      .finally(() => { if (!cancelled) setBusy(false) })
    return () => { cancelled = true; window.removeEventListener(EVENTO_SESION_VENCIDA, expired) }
  }, [])

  async function act(action) {
    setBusy(true); setError('')
    try { await action() }
    catch { setError('No se pudo completar el acceso con Microsoft. Recarga la página e intenta nuevamente.'); setBusy(false) }
  }

  if (user) return <UsuarioContext.Provider value={user}>
    <aside className="session-bar" aria-label="Sesión"><span>{user.nombre} · {user.roles.join(', ')}</span>
      <button type="button" disabled={busy} onClick={() => { setUser(null); act(cerrarSesion) }}>Cerrar sesión</button></aside>
    {children}
  </UsuarioContext.Provider>

  return <PantallaAcceso busy={busy} ready={ready} error={error} wrongOrigin={wrongOrigin}
    onLogin={() => act(iniciarSesion)} onLogout={() => act(cerrarSesion)} />
}
