import { COLUMNAS_UCI, mensajeConexionAzureML } from './estadoConexion.mjs'

export default function PanelLaboratorio({ values, estado, status, consulta, busy, error, result, submit, change, cargarEjemplo }) {
  const proveedor = estado?.proveedor
  const configurado = estado?.configurado === true
  const local = proveedor === 'local'
  return <section className="card" style={{ marginTop: 24 }} aria-labelledby="ml-heading" aria-busy={busy}>
    <h2 id="ml-heading">Laboratorio académico · {local ? 'IA local · scikit-learn' : proveedor === 'azure' ? 'Azure ML' : proveedor ? 'Deshabilitado' : 'Comprobando proveedor'}</h2>
    <p>Separado del formulario principal. Usa exclusivamente escenarios ficticios con las 19 variables UCI. Importes en dólares taiwaneses (NTD), no pesos mexicanos. Datos originales: Taiwán, 2005.</p>
    <p role="status">{mensajeConexionAzureML(configurado, status, consulta, proveedor)}</p>
    {local && configurado && <p>Modelo: {estado.modelo_configurado}. Entrenado con scikit-learn; ejecución local sin llave ni suscripción Azure. El artefacto numérico incluido se comprueba antes de cada consulta.</p>}
    <details open={local && configurado}><summary>Abrir formulario UCI</summary>
      <p>LIMIT_BAL: límite de crédito. PAY_0, PAY_2…6: estados de pago de septiembre a abril; códigos originales de −2 a 9, no días de atraso. BILL_AMT1…6: saldos de septiembre a abril (pueden ser negativos). PAY_AMT1…6: pagos de septiembre a abril (no negativos).</p>
      <form onSubmit={submit}>
        <button type="button" disabled={busy} onClick={cargarEjemplo}>Cargar ejemplo ficticio</button>
        <p>Cargar el ejemplo no consulta ni guarda datos. {local ? 'El modelo se ejecutará en el servidor local.' : 'Azure requiere servicio disponible y puede generar consumo.'}</p>
        <fieldset disabled={busy}><legend>19 valores enteros obligatorios</legend><div className="financial-fields">
          {COLUMNAS_UCI.map(name => <label key={name} htmlFor={`uci-${name}`}>{name}
            <input id={`uci-${name}`} type="number" step="1" required value={values[name]} autoComplete="off"
              min={name === 'LIMIT_BAL' ? 1 : name.startsWith('PAY_AMT') ? 0 : name.startsWith('PAY_') ? -2 : -2147483648}
              max={name.startsWith('PAY_') && !name.startsWith('PAY_AMT') ? 9 : 2147483647}
              onChange={event => change(name, event.target.value)} />
          </label>)}
        </div></fieldset>
        <button type="submit" disabled={!configurado || busy}>{busy ? 'Consultando modelo…' : local ? 'Consultar IA local' : 'Consultar modelo en Azure'}</button>
      </form>
    </details>
    {error && <p className="error" role="alert">{error}</p>}
    {result && <div role="status"><h3>Clase predicha: {result.incumplimiento_predicho ? 'Incumplimiento' : 'No incumplimiento'}</h3>
      <p>Origen: {result.origen}. Modelo: {result.modelo_configurado}.</p><p>{result.advertencia}</p>
      {local && result.variables_fuera_rango_entrenamiento.length > 0 && <p className="notice">Variables fuera de los rangos observados al entrenar: {result.variables_fuera_rango_entrenamiento.join(', ')}. La extrapolación puede ser poco fiable.</p>}
    </div>}
    {local && configurado && <details><summary>Métricas y límites del modelo local</summary>
      <p>Prueba independiente: {estado.metricas_prueba.filas.toLocaleString('es-MX')} filas UCI. AUC: {estado.metricas_prueba.auc.toFixed(3)}. Sensibilidad: {(estado.metricas_prueba.sensibilidad * 100).toFixed(1)}%. Precisión entre positivos: {(estado.metricas_prueba.precision * 100).toFixed(1)}%.</p>
      <p>Exactitud: {(estado.metricas_prueba.exactitud * 100).toFixed(1)}%; predecir siempre «No incumplimiento» obtiene {(estado.metricas_prueba.baseline_exactitud * 100).toFixed(1)}%. La exactitud por sí sola no acredita calidad crediticia.</p>
      <p>Particiones agrupadas aleatorias, no temporales. No se usaron sexo, educación, estado civil ni edad. Esto no demuestra ausencia de sesgo ni representatividad para México.</p>
    </details>}
    <p className="notice">No autoriza ni rechaza créditos. La clase no es una probabilidad de crédito real. Esta consulta no se guarda en PostgreSQL ni cambia el riesgo del formulario principal.</p>
  </section>
}
