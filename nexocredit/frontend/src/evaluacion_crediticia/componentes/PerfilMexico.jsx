import { perfilMexicoVacio, tiposCredito } from '../servicios/modeloMexico.mjs'

const preguntas = [
  ['periodicidad', '¿Cada cuándo recibe ese ingreso?', [[1, 'Semana'], [2, 'Quincena'], [3, 'Mes'], [4, 'Año']]],
  ['ingreso_variable', '¿El ingreso laboral es fijo o variable?', [[1, 'Fijo'], [2, 'Variable']]],
  ['presupuesto', '¿Lleva un presupuesto o registro de ingresos y gastos?', [[1, 'Sí'], [2, 'No']]],
  ['gastos_cubiertos', 'En los últimos 12 meses, ¿el ingreso fue suficiente para cubrir sus gastos?', [[1, 'Sí'], [2, 'No']]],
  ['ahorro_emergencia', 'Sin ingresos, ¿cuánto tiempo cubriría sus gastos con ahorros?', [[1, 'Menos de una semana o sin ahorros'], [2, 'Una semana a menos de un mes'], [3, 'Un mes a menos de tres meses'], [4, 'Tres meses a menos de seis meses'], [5, 'Seis meses o más']]],
]

export default function PerfilMexico({ perfil, change }) {
  const actualizar = value => change({ target: { name: 'perfil_enif', value } })
  return <section className="perfil-mexico" aria-labelledby="perfil-mexico-titulo">
    <h3 id="perfil-mexico-titulo">Modelo mexicano · ENIF 2024</h3>
    <label className="modelo-mexico-toggle"><input type="checkbox" checked={!!perfil} onChange={e => actualizar(e.target.checked ? perfilMexicoVacio() : null)} /> Incluir análisis estadístico mexicano</label>
    <p className="form-footnote">Modelo entrenado con datos públicos de INEGI/CNBV. Estudia atrasos reportados, no predice impagos futuros. Sólo aplica a personas con ingreso laboral positivo y algún crédito formal. No consulta su expediente en INEGI ni Buró. Usa un escenario ficticio.</p>
    {perfil && <>
      <div className="field-group"><label htmlFor="enif-ingreso">Ingreso por trabajo en el periodo elegido *</label><input id="enif-ingreso" type="number" min="0.01" max="98000" step="0.01" required value={perfil.ingreso_laboral} onChange={e => actualizar({ ...perfil, ingreso_laboral: e.target.value })} aria-describedby="enif-ingreso-ayuda" /><p id="enif-ingreso-ayuda" className="form-footnote">No es el ingreso total del hogar. Si recibe $98,000 o más por periodo, capture 98000: es el tope del cuestionario ENIF. No se convierte automáticamente desde el ingreso mensual de arriba.</p></div>
      {preguntas.map(([campo, titulo, opciones]) => <div className="field-group" key={campo}><label htmlFor={`enif-${campo}`}>{titulo} *</label><select id={`enif-${campo}`} required value={perfil[campo]} onChange={e => actualizar({ ...perfil, [campo]: e.target.value })}><option value="">Seleccionar…</option>{opciones.map(([valor, texto]) => <option key={valor} value={valor}>{texto}</option>)}</select></div>)}
      <fieldset className="productos-mexico"><legend>Créditos formales que tiene · seleccione todos los que correspondan *</legend>{tiposCredito.map(([tipo, texto]) => <label key={tipo}><input type="checkbox" checked={perfil.creditos.includes(tipo)} onChange={e => actualizar({ ...perfil, creditos: e.target.checked ? [...perfil.creditos, tipo] : perfil.creditos.filter(t => t !== tipo) })} />{texto}</label>)}</fieldset>
      {!perfil.creditos.length && <p className="form-footnote">Seleccione al menos un crédito. Si no tiene ninguno o no conoce sus respuestas, desactive este análisis: no se inventa un perfil.</p>}
    </>}
  </section>
}
