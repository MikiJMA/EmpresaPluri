import { importe, valorCapturado } from './metricasEscenario.mjs'
import { formatearPesos } from '../../interfaz/moneda.mjs'
import { explicarScore, explicarMargen, rangosParaVersion, VERSION_REGLAS_ACTUAL } from './ayudaScore.mjs'

function Rangos({ titulo, rangos }) {
  return <div className="scenario-guide"><h3>{titulo}</h3><dl>
    {rangos.map(([rango, significado]) => <div key={rango}><dt>{rango}</dt><dd>{significado}</dd></div>)}
  </dl></div>
}

export default function IndicadoresEscenario({ result, submitted }) {
  const score = valorCapturado(result, submitted, 'score_buro_actual')
  const margen = result?.margen_libre ?? null
  const version = result?.version_modelo ?? VERSION_REGLAS_ACTUAL
  const rangos = rangosParaVersion(version)
  const valores = [
    ['Ingreso mensual', importe(valorCapturado(result, submitted, 'ingresos_mensuales')), 'Capturado · MXN'],
    ['Deuda actual', importe(valorCapturado(result, submitted, 'deuda_actual')), 'Capturada · MXN'],
  ]
  return <section className="enterprise-kpis enterprise-kpis-explained" aria-label="Datos del último escenario evaluado">
    <div className="enterprise-kpi" aria-label="Score capturado y significado">
      <span>Score capturado</span><strong>{score ?? '—'}</strong><small>Escala demo: 0–1000 · No verificado</small>
      <p className="scenario-reading">{explicarScore(score, version)}</p>
      <small>{version === 'reglas-demo-v1' ? 'Evaluación anterior · No recalculada · reglas-demo-v1' : version}</small>
      {rangos && <Rangos titulo="Qué significa cada rango" rangos={rangos.score} />}
      {rangos && <aside className="scenario-example" aria-label="Ejemplo ficticio de score y margen">
        <b>Ejemplo ficticio: margen de $20,000 MXN</b>
        <p>Score <b>200 → {version === 'reglas-demo-v1' ? 'Medio' : 'Alto'}</b>. Score <b>500 → Medio</b>. Score <b>700 → Bajo</b>.</p>
      </aside>}
      <p className="scenario-caution">{version === 'reglas-demo-v2'
        ? 'Un score de 0–499 siempre da Alto. Un score alto no garantiza Bajo: el margen insuficiente puede elevar el riesgo.'
        : 'El score por sí solo no define Bajo, Medio o Alto.'} No es una consulta a Buró ni una probabilidad de incumplimiento.</p>
    </div>
    <div className="enterprise-kpi" aria-label="Margen disponible y significado">
      <span>Margen disponible</span><strong title={formatearPesos(margen, { decimales: 2 })}>{importe(margen)}</strong><small>Margen = ingresos − gastos · MXN</small>
      <p className="scenario-reading">{explicarMargen(margen, version)}</p>
      {rangos && <Rangos titulo="Qué significa cada margen" rangos={rangos.margen} />}
      <p className="scenario-caution">Vista redondeada a pesos; el cálculo conserva centavos. Los límites se aplican al valor exacto de la API. Son reglas demo; no autorizan créditos.</p>
    </div>
    {valores.map(([label, value, note]) => <div className="enterprise-kpi" key={label}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>)}
  </section>
}
