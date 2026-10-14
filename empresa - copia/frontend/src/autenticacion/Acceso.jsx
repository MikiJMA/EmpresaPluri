import { useEffect, useRef, useState } from 'react'
import { prepararSesion, prepararMicrosoft, iniciarSesion, iniciarSesionLocal, cerrarSesion, limpiarSesionLocal, verificarUsuario } from './cliente'
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
  const [local, setLocal] = useState({ habilitado: false, cuentas_disponibles: false })
  const intentoSesion = useRef(0)
  useEffect(() => {
    let cancelled = false
    const inicio = intentoSesion.current
    function expired() { intentoSesion.current += 1; limpiarSesionLocal(); setUser(null); setBusy(false); setError('Tu sesión requiere verificación. Vuelve a iniciar sesión.') }
    window.addEventListener(EVENTO_SESION_VENCIDA, expired)
    prepararSesion().then(async ({ config }) => {
      if (cancelled) return
      setReady(true)
      setLocal(config.local || { habilitado: false, cuentas_disponibles: false })
      // El acceso local no depende de que Microsoft responda o tenga una sesión.
      setBusy(false)
      if (window.location.origin !== new URL(config.redirectUri).origin) { setWrongOrigin(true); return }
      try {
        const intento = intentoSesion.current
        const { msal } = await prepararMicrosoft()
        if (!cancelled && intentoSesion.current === intento && msal.getActiveAccount()) {
          const verified = await verificarUsuario()
          if (!cancelled && intentoSesion.current === intento) setUser(verified)
        }
      } catch { /* Un fallo cloud no impide usar las cuentas locales. */ }
    }).catch(err => { if (!cancelled) setError(err.message?.startsWith('Acceso denegado') ? err.message : 'No se pudo verificar el acceso. Revisa la conexión y vuelve a iniciar sesión; si continúa, recarga la página.') })
      .finally(() => { if (!cancelled && intentoSesion.current === inicio) setBusy(false) })
    return () => { cancelled = true; window.removeEventListener(EVENTO_SESION_VENCIDA, expired) }
  }, [])

  async function act(action) {
    const intento = ++intentoSesion.current
    setBusy(true); setError('')
    try { await action() }
    catch { if (intentoSesion.current === intento) setError('No se pudo completar el acceso con Microsoft. Puedes usar tu cuenta local o intentarlo nuevamente.') }
    finally { if (intentoSesion.current === intento) setBusy(false) }
  }

  async function localLogin(usuario, password) {
    const intento = ++intentoSesion.current
    setBusy(true); setError('')
    try { const verified = await iniciarSesionLocal(usuario, password); if (intentoSesion.current === intento) setUser(verified) }
    catch (err) { if (intentoSesion.current === intento) setError(err instanceof TypeError || err.name === 'TimeoutError' ? 'No se pudo conectar con el servidor local.' : err.message) }
    finally { if (intentoSesion.current === intento) setBusy(false) }
  }

  if (user) return <UsuarioContext.Provider value={user}>
    <aside className="session-bar" aria-label="Sesión"><span>{user.nombre} · {user.roles.join(', ')} · {user.proveedor === 'local' ? 'Cuenta local' : 'Microsoft'}</span>
      <button type="button" disabled={busy} onClick={() => { setUser(null); act(cerrarSesion) }}>Cerrar sesión</button></aside>
    {children}
  </UsuarioContext.Provider>

  return <PantallaAcceso busy={busy} ready={ready} error={error} wrongOrigin={wrongOrigin}
    local={local} onLocalLogin={localLogin}
    onLogin={() => act(iniciarSesion)} onLogout={() => act(cerrarSesion)} />
}
