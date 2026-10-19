import { MARCA } from './marca.mjs'
import IconoMarca from './IconoMarca'
import { SECCIONES } from './secciones.mjs'
const titulos = {
  seguimiento: 'Resumen de evaluaciones',
  evaluacion: 'Evaluación de riesgo crediticio',
  historial: 'Historial y revisión manual',
  creditos: 'Créditos, pagos y alertas · DEMO',
  laboratorio: 'Laboratorio académico · IA predictiva',
  indicadores: 'Indicadores financieros',
  documentos: 'Documentos de demostración',
}

export default function MarcoAplicacion({ user, seccion, onSeccionChange, children }) {
  const nombre = user?.nombre || 'Cuenta autorizada'
  const iniciales = nombre.trim().split(/\s+/).slice(0, 2).map(parte => parte[0]).join('').toUpperCase()
  const seccionActual = SECCIONES.find(([id]) => id === seccion)?.[1] || 'Evaluaciones'
  const titulo = seccion === 'seguimiento' && user?.nombre?.trim() ? `Hola, ${nombre.trim().split(/\s+/)[0]}` : titulos[seccion] || titulos.evaluacion
  return <main className="enterprise-app">
    <a className="enterprise-skip" href="#contenido-principal">Ir al contenido</a>
    <aside className="enterprise-sidebar" aria-label="Navegación principal">
      <div>
        <a className="enterprise-brand" href="/" onClick={event => onSeccionChange('seguimiento', event)}>
          <span className="enterprise-brand-icon" aria-hidden="true">
            <IconoMarca size={24} />
          </span>
          <span>{MARCA}<small>ANÁLISIS CREDITICIO</small></span>
        </a>
        <nav className="enterprise-navigation" aria-label="Secciones">
          {SECCIONES.map(([id, label, path, ruta]) => <a key={id} href={ruta} className={seccion === id ? 'active' : ''}
            aria-current={seccion === id ? 'location' : undefined} onClick={event => onSeccionChange(id, event)}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d={path} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>{label}
          </a>)}
        </nav>
        <div className="enterprise-sidebar-note"><span className="enterprise-dot" /> Entorno de demostración<p>Escenarios ficticios.<br />Revisión humana requerida.</p></div>
      </div>
      <div className="enterprise-profile"><span className="enterprise-avatar" aria-hidden="true">{iniciales}</span><div><strong>{nombre}</strong><small>{user?.roles?.join(' · ') || 'Acceso autenticado'}</small></div></div>
    </aside>

    <div className="enterprise-main">
      <header className="enterprise-topbar">
        <div><p>{MARCA} / {seccionActual}</p><h1>{titulo}</h1></div>
      </header>
      <div className="enterprise-content" id="contenido-principal">
        {children}
        <footer><span>{MARCA} · Prototipo académico</span><span>{user?.proveedor === 'local' ? 'Acceso con cuenta local' : user?.proveedor === 'microsoft' ? 'Acceso con Microsoft Entra ID' : 'Acceso autenticado'} · No autoriza créditos</span></footer>
      </div>
    </div>
  </main>
}
