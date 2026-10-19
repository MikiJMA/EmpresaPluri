import { SECCIONES } from './secciones.mjs'

const accesos = [
  ['evaluacion', 'Captura y análisis de escenarios.'],
  ['creditos', 'Planes ficticios y alertas trazables.'],
  ['laboratorio', 'IA local o Azure ML, por separado.'],
  ['indicadores', 'Banxico y Banco Mundial.'],
  ['historial', 'Evaluaciones anteriores.'],
  ['documentos', 'Guías y alcance del proyecto.'],
]

export default function ResumenInicio({ onSeccionChange, onNuevaEvaluacion, busy = false }) {
  return <section className="home-overview" aria-label="Accesos del resumen">
    <div className="home-hero">
      <div><h2>Evalúa un escenario de riesgo</h2>
        <p>Captura ingresos, gastos y score. El resultado se confirma al evaluar y no autoriza créditos.</p></div>
      <a className="home-new-evaluation" href="/evaluaciones" aria-disabled={busy || undefined}
        onClick={event => {
          if (busy) { event.preventDefault(); return }
          if (onNuevaEvaluacion) onNuevaEvaluacion()
          else onSeccionChange('evaluacion', event)
        }}>Nueva evaluación<span aria-hidden="true">→</span></a>
    </div>
    <div className="home-shortcuts">
      {accesos.map(([id, descripcion]) => {
        const [, titulo, path, ruta] = SECCIONES.find(([key]) => key === id)
        return <a className="home-shortcut" key={id} href={ruta} onClick={event => onSeccionChange(id, event)}>
          <span className="home-shortcut-icon" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" focusable="false">
            <path d={path} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg></span>
          <h3>{titulo}</h3><p>{descripcion}</p>
          <span className="home-shortcut-open">Abrir <span aria-hidden="true">→</span><span className="visually-hidden"> {titulo}</span></span>
        </a>
      })}
    </div>
  </section>
}
