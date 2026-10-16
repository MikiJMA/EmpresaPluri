import { COLUMNAS_UCI, mensajeConexionAzureML } from '../../azure_ml/estadoConexion.mjs'

export default function PanelSegundaOpinion({ evaluacion, vista, cambiar, cargarEjemplo, consultar, comprobar }) {
  const { estado, valores, busy, comprobando, error, resultado, status, consulta } = vista
  const local = estado?.proveedor === 'local'
  const disponible = estado?.configurado === true
  return <section className="card segunda-opinion" aria-labelledby="segunda-opinion-heading" aria-busy={busy || comprobando}>
    <h2 id="segunda-opinion-heading">Segunda opinión IA (académica)</h2>
    <p>Consulta opcional del modelo junto al resultado guardado. <strong>No evalúa a este solicitante:</strong> compara un escenario UCI ficticio independiente, sin convertir tus ingresos o deudas MXN a variables del modelo.</p>
    <div className="segunda-opinion-comparacion">
      <div><span>Reglas demo</span><strong>{evaluacion.nivel_riesgo_preliminar}</strong><small>{evaluacion.version_modelo} · resultado guardado</small></div>
      <div><span>Modelo académico</span><strong>{resultado ? (resultado.modelo.incumplimiento_predicho ? 'Incumplimiento' : 'No incumplimiento') : 'Sin consulta'}</strong><small>{resultado ? 'Escenario UCI independiente · no guardado' : 'Sólo se consulta al pulsar el botón'}</small></div>
    </div>
    <p role="status">{mensajeConexionAzureML(disponible, status, consulta, estado?.proveedor)}</p>
    {disponible && <p>Proveedor: {local ? 'scikit-learn local; sin llaves ni suscripción Azure' : 'Azure Machine Learning; puede generar consumo de pago'}. Modelo: {estado.modelo_configurado || 'etiqueta configurada en servidor'}.</p>}
    {!comprobando && !busy && <button className="segunda-opinion-secundario" type="button" onClick={comprobar}>Volver a comprobar proveedor</button>}
    <details>
      <summary>Capturar las 19 variables UCI del escenario ficticio</summary>
      <p>Datos originales de Taiwán, 2005. Importes en dólares taiwaneses (NTD), no MXN. No se usa RFC, CURP, sexo, educación, estado civil ni edad. No hay conversión automática desde la solicitud.</p>
      <p>LIMIT_BAL: límite de crédito. PAY_0 y PAY_2…6: estados de pago de septiembre a abril, códigos de −2 a 9; no son días de atraso. BILL_AMT1…6: saldos (pueden ser negativos). PAY_AMT1…6: pagos (no negativos), de septiembre a abril.</p>
      <form onSubmit={event => { event.preventDefault(); consultar() }}>
        <button type="button" className="segunda-opinion-secundario" disabled={busy} onClick={cargarEjemplo}>Cargar ejemplo UCI ficticio</button>
        <p>Cargar el ejemplo sólo llena este formulario; no consulta, guarda ni modifica la evaluación.</p>
        <fieldset disabled={busy}><legend>19 enteros obligatorios, capturados de forma independiente</legend>
          <div className="segunda-opinion-campos">{COLUMNAS_UCI.map(name => <label key={name} htmlFor={`segunda-opinion-${name}`}>{name}
            <input id={`segunda-opinion-${name}`} type="number" step="1" required autoComplete="off" value={valores[name]}
              min={name === 'LIMIT_BAL' ? 1 : name.startsWith('PAY_AMT') ? 0 : name.startsWith('PAY_') ? -2 : -2147483648}
              max={name.startsWith('PAY_') && !name.startsWith('PAY_AMT') ? 9 : 2147483647}
              onChange={event => cambiar(name, event.target.value)} />
          </label>)}</div>
        </fieldset>
        {estado?.proveedor === 'azure' && <p className="notice">Al consultar se enviarán estas 19 variables ficticias al servicio Azure configurado. Puede haber consumo de pago; no se envían los datos MXN del solicitante.</p>}
        <button type="submit" disabled={!disponible || busy || comprobando}>{busy ? 'Consultando segunda opinión…' : 'Consultar segunda opinión'}</button>
      </form>
    </details>
    {error && <p role="alert" className="error">{error}</p>}
    {resultado && <div className="segunda-opinion-resultado" role="status">
      <h3>Reglas demo: {resultado.riesgo_por_reglas} · Modelo académico: {resultado.modelo.incumplimiento_predicho ? 'Incumplimiento' : 'No incumplimiento'}</h3>
      <p>Origen: {resultado.modelo.origen}. Modelo: {resultado.modelo.modelo_configurado}.</p>
      <p>{resultado.modelo.advertencia}</p><p>{resultado.advertencia}</p>
      {local && resultado.modelo.variables_fuera_rango_entrenamiento.length > 0 && <p className="notice">Fuera de los rangos observados al entrenar: {resultado.modelo.variables_fuera_rango_entrenamiento.join(', ')}. La extrapolación puede ser poco fiable.</p>}
    </div>}
    <p className="notice">No es una validación para México ni una probabilidad calibrada. No autoriza ni rechaza créditos, no cambia las reglas demo y no se guarda en el expediente. Una discrepancia no acredita que un método sea correcto para este solicitante.</p>
  </section>
}
