import { MARCA } from './marca.mjs'
import IconoMarca from './IconoMarca'

const secciones = [
  ['seguimiento', 'Resumen', 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z'],
  ['evaluacion', 'Evaluaciones', 'M4 20V10M12 20V4M20 20v-7'],
  ['historial', 'Historial', 'M6 3h9l4 4v14H6zM9 12h6M9 16h6'],
  ['laboratorio', 'Azure ML', 'M9 3h6M10 3v6L4 19v2h16v-2L14 9V3M8 15h8'],
  ['indicadores', 'Indicadores financieros', 'M3 17l6-6 4 4 8-10M16 5h5v5M3 21h18'],
  ['documentos', 'Documentos', 'M4 5h6l2 2h8v14H4zM8 12h8M8 16h5'],
]

export default function MarcoAplicacion({ user, seccion, onSeccionChange, children }) {
  const nombre = user?.nombre || 'Cuenta Microsoft'
  const iniciales = nombre.trim().split(/\s+/).slice(0, 2).map(parte => parte[0]).join('').toUpperCase()
  return <main className="enterprise-app">
    <a className="enterprise-skip" href="#contenido-principal">Ir al contenido</a>
    <aside className="enterprise-sidebar" aria-label="Navegación principal">
      <div>
        <a className="enterprise-brand" href="#evaluacion" onClick={() => onSeccionChange('evaluacion')}>
          <span className="enterprise-brand-icon" aria-hidden="true">
            <IconoMarca size={24} />
          </span>
          <span>{MARCA}<small>ANÁLISIS CREDITICIO</small></span>
        </a>
        <nav className="enterprise-navigation" aria-label="Secciones">
          {secciones.map(([id, label, path]) => <a key={id} href={`#${id}`} className={seccion === id ? 'active' : ''}
            aria-current={seccion === id ? 'location' : undefined} onClick={() => onSeccionChange(id)}>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d={path} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>{label}
          </a>)}
        </nav>
        <div className="enterprise-sidebar-note"><span className="enterprise-dot" /> Entorno de demostración<p>Escenarios ficticios.<br />Revisión humana requerida.</p></div>
      </div>
      <div className="enterprise-profile"><span className="enterprise-avatar" aria-hidden="true">{iniciales}</span><div><strong>{nombre}</strong><small>{user?.roles?.join(' · ') || 'Acceso con Microsoft'}</small></div></div>
    </aside>

    <div className="enterprise-main">
      <header className="enterprise-topbar">
        <div><p>{MARCA} / Evaluaciones</p><h1>Evaluación de riesgo crediticio</h1></div>
      </header>
      <div className="enterprise-content" id="contenido-principal">
        {children}
        <footer><span>{MARCA} · Prototipo académico</span><span>Acceso con Microsoft Entra ID · No autoriza créditos</span></footer>
      </div>
    </div>
  </main>
}
