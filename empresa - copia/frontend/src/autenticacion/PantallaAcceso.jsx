import { useState } from 'react'
import { MARCA } from '../interfaz/marca.mjs'
import IconoMarca from '../interfaz/IconoMarca'

export default function PantallaAcceso({ busy, ready, error, wrongOrigin, onLogin, onLogout,
  local = { habilitado: false, cuentas_disponibles: false }, onLocalLogin }) {
  const [usuario, setUsuario] = useState('')
  const [password, setPassword] = useState('')
  async function submitLocal(event) {
    event.preventDefault()
    const secreto = password
    setPassword('')
    await onLocalLogin(usuario.trim(), secreto)
  }
  return <main className="access-screen">
    <aside className="access-panel" aria-hidden="true">
      <svg className="access-waves" viewBox="0 0 700 800" preserveAspectRatio="none" fill="none" focusable="false">
        <g stroke="#fff" strokeOpacity="0.12" strokeWidth="1.5">
          <path d="M0 560 C150 500 250 640 400 580 S600 520 700 560" />
          <path d="M0 620 C150 560 250 700 400 640 S600 580 700 620" />
          <path d="M0 680 C150 620 250 760 400 700 S600 640 700 680" />
          <path d="M0 740 C150 680 250 820 400 760 S600 700 700 740" />
        </g>
      </svg>
      <div className="access-panel-content">
        <div className="access-panel-brand">
          <span className="access-brand-icon"><IconoMarca size={28} /></span>
          <b>{MARCA}</b>
        </div>
        <p className="access-quote">Acceso seguro para analistas y administradores.</p>
      </div>
    </aside>
    <section className="access-card" aria-labelledby="access-title" aria-busy={busy}>
      <div className="access-card-body">
        <div className="access-mobile-brand" aria-hidden="true">
          <span className="access-brand-icon"><IconoMarca size={28} /></span>
          <b>{MARCA}</b>
        </div>
        <span className="access-brand-env">{MARCA} · Entorno de demostración</span>

        <h1 id="access-title">Accede a tu espacio de análisis</h1>

        {busy && <p className="access-status" role="status">Verificando sesión…</p>}
        {error && <p className="access-error" role="alert">{error}</p>}

        {local.habilitado && <form className="access-local-form" onSubmit={submitLocal}>
          <h2>Acceso local</h2>
          <p>Sin depender de Microsoft. Solo cuentas creadas por el administrador de esta demo.</p>
          {!local.cuentas_disponibles && <p className="access-origin">Todavía no hay cuentas locales. Crea la primera con el acceso «Crear usuario local» de la carpeta de operación.</p>}
          <label htmlFor="local-usuario">Usuario local</label>
          <input id="local-usuario" name="username" autoComplete="username" required maxLength={64}
            value={usuario} disabled={busy || !ready || !local.cuentas_disponibles}
            onChange={event => setUsuario(event.target.value)} />
          <label htmlFor="local-password">Contraseña local (mínimo 6 caracteres)</label>
          <input id="local-password" name="password" type="password" autoComplete="current-password" required minLength={6} maxLength={128}
            value={password} disabled={busy || !ready || !local.cuentas_disponibles}
            onChange={event => setPassword(event.target.value)} />
          <button className="access-button access-primary access-local-submit" type="submit"
            disabled={busy || !ready || !local.cuentas_disponibles}>Entrar con cuenta local</button>
        </form>}
        {local.habilitado && <div className="access-divider"><span>o continúa con Microsoft</span></div>}

        <div className="access-actions">
          {wrongOrigin ? <p className="access-origin">Para iniciar sesión abre <a href="http://localhost:8080/">{MARCA} en localhost:8080</a>.</p> :
            <button className="access-button access-primary" type="button" disabled={!ready || busy} onClick={onLogin}>
              <span className="access-ms-chip" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 18 18" focusable="false">
                  <rect width="8.5" height="8.5" fill="#f25022" />
                  <rect x="9.5" width="8.5" height="8.5" fill="#7fba00" />
                  <rect y="9.5" width="8.5" height="8.5" fill="#00a4ef" />
                  <rect x="9.5" y="9.5" width="8.5" height="8.5" fill="#ffb900" />
                </svg>
              </span>
              <span className="access-button-text">Iniciar sesión con Microsoft</span>
            </button>}
          {!busy && ready && !wrongOrigin && <button className="access-button access-secondary" type="button" onClick={onLogout}>Cerrar sesión de Microsoft / cambiar cuenta</button>}
        </div>
        <div className="access-security">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
            <path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6l7-3z" stroke="#6366f1" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M9 12l2 2 4-4" stroke="#6366f1" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <p>La contraseña local se valida en tu servidor. La contraseña Microsoft se introduce únicamente en Microsoft. No compartas tokens ni llaves de servicios.</p>
        </div>
      </div>
    </section>
  </main>
}
