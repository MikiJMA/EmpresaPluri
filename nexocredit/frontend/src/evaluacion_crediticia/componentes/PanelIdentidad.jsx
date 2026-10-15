import { SAT_CURP_URL } from '../servicios/identidad.mjs'

export default function PanelIdentidad({ curp, change, revisar, busy, disabled, puedeRevisar = true, data, error }) {
  return <section className="identity-check" aria-label="Revisión de RFC con CURP">
    <label htmlFor="curp-revision">CURP para comparar <small>Opcional · Solo revisión</small></label>
    <input id="curp-revision" type="text" name="curp_revision" value={curp} maxLength={18} autoCapitalize="characters" autoComplete="off" spellCheck={false}
      onChange={change} disabled={disabled} placeholder="18 caracteres de una CURP ficticia" aria-describedby="identity-privacy" />
    <div className="identity-actions">
      <button type="button" disabled={disabled || busy || !puedeRevisar} onClick={revisar}>{busy ? 'Revisando…' : 'Revisar formato y fecha'}</button>
      <a href={SAT_CURP_URL} target="_blank" rel="noopener noreferrer">Consultar RFC por CURP en el SAT ↗</a>
    </div>
    <p id="identity-privacy">La CURP solo se usa para esta revisión; no se guarda ni se envía a la IA. El botón SAT abre su sitio sin enviar datos automáticamente.</p>
    {busy && <p role="status">Comprobando el formato general y la fecha…</p>}
    {error && <p className="identity-warning" role="alert">{error}</p>}
    {data && <div className="identity-review" role="status">
      <strong>{['formato_invalido', 'no_coincide'].includes(data.estado) ? 'Revisa los datos' : 'Comprobación básica · No oficial'}</strong>
      <p>{data.mensaje}</p>
      <ul>{data.comprobaciones.map(item => <li key={item.campo}>{item.campo}: {item.detalle}</li>)}</ul>
    </div>}
    <p className="identity-disclaimer">No certifica identidad, homoclave ni inscripción. El nombre por sí solo no identifica un RFC único; para confirmar el RFC asociado a una CURP usa el SAT.</p>
  </section>
}
