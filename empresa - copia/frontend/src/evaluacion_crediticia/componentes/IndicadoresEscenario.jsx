import { importe, valorCapturado } from './metricasEscenario.mjs'

export default function IndicadoresEscenario({ result, submitted }) {
  const valores = [
    ['Score capturado', valorCapturado(result, submitted, 'score_buro_actual') ?? '—', 'Escala demo: 0–1000 · No verificado'],
    ['Ingreso mensual', importe(valorCapturado(result, submitted, 'ingresos_mensuales')), 'Capturado · MXN'],
    ['Deuda actual', importe(valorCapturado(result, submitted, 'deuda_actual')), 'Capturada · MXN'],
    ['Margen disponible', importe(result?.margen_libre), 'Ingresos menos gastos · MXN'],
  ]
  return <section className="enterprise-kpis" aria-label="Datos del último escenario evaluado">
    {valores.map(([label, value, note]) => <div className="enterprise-kpi" key={label}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>)}
  </section>
}
