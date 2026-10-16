import { esAnalisisMexico } from '../servicios/modeloMexico.mjs'

const porcentaje = n => new Intl.NumberFormat('es-MX', { style: 'percent', maximumFractionDigits: 0 }).format(n)
const modelos = { logistica: 'Regresión logística', bosque: 'Random Forest', gradient_boosting: 'Gradient boosting', seleccion_anidada: 'Selección anidada' }
export default function ResultadoMexico({ analisis }) {
  if (!analisis) return null
  if (!esAnalisisMexico(analisis)) return <section className="card" role="alert">El resultado mexicano tiene un formato inválido. No se muestra una clasificación inventada.</section>
  const metricas = analisis.metricas_prueba
  const control = analisis.control_uso
  const comparacion = analisis.comparacion_modelos
  return <section className="card resultado-mexico" aria-labelledby="resultado-mexico-titulo">
    <div className="card-heading"><h2 id="resultado-mexico-titulo">Resultado del modelo mexicano</h2><span className="enterprise-panel-tag">Piloto empresarial</span></div>
    <div className="enterprise-risk-body">
      <p className="notice">Prueba en modo sombra: no habilita decisiones automatizadas ni uso con clientes reales. {control ? 'Validación empresarial pendiente.' : 'Registro histórico anterior al control del piloto.'}</p>
      <h3>{analisis.atraso_reportado_estimado ? 'Perfil asociado con atrasos reportados' : 'Perfil sin asociación detectada con atrasos reportados'}</h3>
      <p>La regresión logística aprendió de entrevistas mexicanas de ENIF 2024. Este resultado no usa las reglas de score y margen, ni lo decide Ollama.</p>
      <p className="notice">Modelo experimental de capacidad limitada: AUC {metricas.auc_roc.toFixed(3)} en prueba. Sus resultados no justifican una decisión crediticia.</p>
      <dl className="detail-fields"><div><dt>Salida estadística asociativa</dt><dd>{porcentaje(analisis.estimacion_asociativa)}</dd></div><div><dt>Umbral elegido en validación</dt><dd>{porcentaje(analisis.umbral)}</dd></div></dl>
      <p className="notice">Ese porcentaje NO es su probabilidad de dejar de pagar. La clase describe un patrón de encuesta, no confirma atrasos de esta persona. No equivale a Bajo, Medio o Alto ni a una autorización.</p>
      <details><summary>Calidad medida y procedencia</summary><p>Prueba independiente: {metricas.filas} entrevistas. AUC {metricas.auc_roc.toFixed(3)} · sensibilidad {porcentaje(metricas.sensibilidad)} · precisión positiva {porcentaje(metricas.precision_positiva)} · exactitud {porcentaje(metricas.exactitud)}.</p><p>Capacidad limitada: predecir siempre «sin atraso» logra {porcentaje(analisis.exactitud_siempre_sin_atraso)} de exactitud. No debe usarse para aprobar o rechazar créditos.</p><p>{analisis.limites}</p><a href="https://www.inegi.org.mx/programas/enif/2024/" target="_blank" rel="noreferrer">Fuente: INEGI/CNBV, ENIF 2024</a><p className="model-version">Modelo: {analisis.modelo_id}<br />SHA-256: {analisis.modelo_sha256}</p></details>
      {control && <details><summary>Qué falta para habilitar una prueba con clientes reales</summary><ul>{control.motivos_no_promocion.map(motivo => <li key={motivo}>{motivo}</li>)}</ul><p>Estos controles no se pueden aprobar desde el formulario. Un porcentaje o una comparación mejor no sustituyen la autorización y validación empresarial.</p></details>}
      {comparacion?.estado === 'completado' && <details><summary>Comparación de mejoras del piloto</summary>
        <p>Validación cruzada anidada por grupos sobre {comparacion.filas_desarrollo} casos de desarrollo. No es la prueba final de 783 casos ni validación en la empresa; no comparar sus AUC directamente como una mejora frente al 0.605 del modelo servido.</p>
        <table className="comparacion-piloto"><caption>Modelos comparados con calibración interna</caption><thead><tr><th scope="col">Modelo</th><th scope="col">AUC</th><th scope="col">AP</th><th scope="col">Brier</th></tr></thead><tbody>{Object.entries(modelos).map(([id, nombre]) => <tr key={id}><th scope="row">{nombre}</th><td>{comparacion.resultados[id].auc_roc.toFixed(3)}</td><td>{comparacion.resultados[id].average_precision.toFixed(3)}</td><td>{comparacion.resultados[id].brier.toFixed(3)}</td></tr>)}</tbody></table>
        <p>AUC mide distinción; AP resume precisión y detección; Brier evalúa el error de las estimaciones, donde menos es mejor. Ninguna es por sí sola una aprobación del modelo.</p>
        {!Object.values(comparacion.resultados).some(m => m.mejora_auc_demostrada_respecto_logistica) && <p className="notice">No se demostró una mejora consistente de AUC frente a la regresión logística en esta comparación. No se cambió automáticamente el modelo.</p>}
        <p>{comparacion.limites}</p>
      </details>}
      {comparacion?.estado === 'no_disponible' && <p className="form-footnote">{comparacion.motivo}</p>}
      <p className="form-footnote">Se conserva junto con esta evaluación si PostgreSQL está disponible. No se reescribe el historial. Funciona sin Azure, Ollama o llamadas a INEGI al evaluar.</p>
    </div>
  </section>
}
