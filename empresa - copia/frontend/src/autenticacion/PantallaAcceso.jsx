import { MARCA } from '../interfaz/marca.mjs'
import IconoMarca from '../interfaz/IconoMarca'

export default function PantallaAcceso({ busy, ready, error, wrongOrigin, onLogin, onLogout }) {
  return <main className="access-screen">
    <svg className="access-network" viewBox="0 0 1280 800" preserveAspectRatio="xMidYMid slice" fill="none" aria-hidden="true" focusable="false">
      <g stroke="#6366f1" strokeOpacity=".22" strokeWidth="1.2">
        <line x1="90" y1="120" x2="310" y2="230" />
        <line x1="310" y1="230" x2="240" y2="430" />
        <line x1="310" y1="230" x2="520" y2="110" />
        <line x1="240" y1="430" x2="120" y2="640" />
        <line x1="240" y1="430" x2="430" y2="690" />
        <line x1="960" y1="90" x2="1130" y2="250" />
        <line x1="1130" y1="250" x2="1040" y2="470" />
        <line x1="1130" y1="250" x2="1230" y2="130" />
        <line x1="1040" y1="470" x2="1200" y2="640" />
        <line x1="1040" y1="470" x2="880" y2="700" />
      </g>
      <g fill="#6366f1" fillOpacity=".35">
        <circle cx="90" cy="120" r="5" /><circle cx="310" cy="230" r="7" />
        <circle cx="520" cy="110" r="5" /><circle cx="240" cy="430" r="7" />
        <circle cx="120" cy="640" r="5" /><circle cx="430" cy="690" r="6" />
        <circle cx="960" cy="90" r="5" /><circle cx="1130" cy="250" r="7" />
        <circle cx="1230" cy="130" r="5" /><circle cx="1040" cy="470" r="7" />
        <circle cx="1200" cy="640" r="5" /><circle cx="880" cy="700" r="6" />
      </g>
    </svg>

    <section className="access-card" aria-labelledby="access-title" aria-busy={busy}>
      <div className="access-card-body">
        <div className="access-brand">
          <span className="access-brand-icon"><IconoMarca size={28} /></span>
          <div className="access-brand-text">
            <span className="access-brand-name">{MARCA}</span>
            <span className="access-brand-env">Entorno de demostración</span>
          </div>
        </div>

        <h1 id="access-title">Accede con tu cuenta Microsoft</h1>
        <div className="access-info">
          <p>Las evaluaciones y el laboratorio requieren una cuenta autorizada con rol Analista o Administrador.</p>
        </div>

        {busy && <p className="access-status" role="status">Verificando sesión…</p>}
        {error && <p className="access-error" role="alert">{error}</p>}

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
      </div>

      <div className="access-security">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
          <path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6l7-3z" stroke="#6366f1" strokeWidth="1.6" strokeLinejoin="round" />
          <path d="M9 12l2 2 4-4" stroke="#6366f1" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p>Introduce tu contraseña únicamente en la página de Microsoft. No compartas tokens ni claves.</p>
      </div>
    </section>
  </main>
}
