import { explicarScore } from './ayudaScore.mjs'

export default function ScoreAyuda({ valor }) {
  return <div className="score-help">
    <p id="score-help" className="score-help-text" aria-live="polite">{explicarScore(valor)}</p>
    <p className="score-help-location">Consulta los rangos en las tarjetas «Score capturado» y «Margen disponible» de arriba.</p>
    <p id="score-help-disclaimer" className="score-help-disclaimer">Reglas demo; score capturado, no verificado. El resultado se confirma al evaluar, no autoriza créditos.</p>
  </div>
}
