const importe = value => new Intl.NumberFormat('es-MX', { maximumFractionDigits: 2 }).format(value)

export default function PanelValoracionIA({ evaluacion, vista, reintentar }) {
  const { estado, configuracion, resultado, error } = vista
  const busy = ['comprobando', 'generando'].includes(estado)
  return <section className="card segunda-opinion valoracion-ia" aria-labelledby="valoracion-ia-heading" aria-busy={busy}>
    <h2 id="valoracion-ia-heading">Evaluación con IA de tu escenario</h2>
    <p>Ollama valora los <strong>mismos datos guardados</strong>: ingresos, gastos, deuda, pagos, atraso y score. No necesitas llenar otro formulario. No se envían RFC, CURP o nombre.</p>
    <div className="segunda-opinion-comparacion">
      <div><span>Resultado por reglas</span><strong>{evaluacion.nivel_riesgo_preliminar}</strong><small>{evaluacion.version_modelo} · historial conservado</small></div>
      <div><span>Valoración de Ollama</span><strong>{resultado?.nivel_riesgo_ia || (busy ? 'Analizando…' : 'No disponible')}</strong><small>IA generativa · no predicción estadística</small></div>
    </div>
    {estado === 'comprobando' && <p role="status">Comprobando configuración de Ollama; todavía no se ha solicitado el análisis.</p>}
    {estado === 'generando' && <p role="status">La IA está valorando tu escenario guardado. La primera carga puede tardar hasta tres minutos según el equipo; no necesitas pulsar otro botón.</p>}
    {estado === 'no_disponible' && <p role="status">{configuracion?.motivo || 'El evaluador IA no está disponible.'} La clasificación por reglas permanece guardada.</p>}
    {error && <p role="alert" className="error">{error}</p>}
    {!busy && !resultado && <button type="button" className="segunda-opinion-secundario" onClick={reintentar}>Volver a intentar valoración IA</button>}
    {resultado && <div className="segunda-opinion-resultado" role="status">
      <h3>Valoración IA: {resultado.nivel_riesgo_ia}</h3>
      <p>Modelo: {resultado.modelo} · {new Date(resultado.fecha_generacion).toLocaleString('es-MX')}.</p>
      {resultado.nivel_riesgo_ia !== resultado.riesgo_por_reglas && <p className="notice">La IA y las reglas difieren. Requiere revisión humana: no se promedian ni se sustituye el resultado guardado.</p>}
      <h3>Factores seleccionados por la IA</h3>
      <ul>{resultado.factores.map(f => <li key={f.codigo}>{f.etiqueta}: <strong>{importe(f.valor)} {f.unidad}</strong></li>)}</ul>
      <p>Las cifras se calculan en el servidor; la categoría y la selección de factores/revisiones las genera Ollama.</p>
      <h3>Revisiones sugeridas</h3>
      <ul>{resultado.recomendaciones.map(r => <li key={r.codigo}>{r.texto}</li>)}</ul>
      <p>La IA selecciona revisiones de un catálogo. El servidor exige siempre revisión humana, aunque el modelo la omita.</p>
      <p className="notice">{resultado.aviso}</p>
    </div>}
    <p className="notice">Usa sólo datos ficticios. Esta valoración puede equivocarse: no es consulta de Buró, modelo predictivo validado ni autorización de crédito. El análisis se genera automáticamente al guardar si Ollama está configurado y se conserva en caché durante 24 horas.</p>
  </section>
}
