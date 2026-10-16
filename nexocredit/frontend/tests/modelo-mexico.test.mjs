import assert from 'node:assert/strict'
import test from 'node:test'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { esAnalisisMexico, prepararPerfilMexico, perfilMexicoVacio, esControlPiloto, esComparacionPiloto } from '../src/evaluacion_crediticia/servicios/modeloMexico.mjs'
import { control, comparacion } from './helpers/piloto-fixtures.mjs'
import { validarEvaluacion } from '../src/evaluacion_crediticia/servicios/contratos.mjs'

const { default: Perfil } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/PerfilMexico.jsx', import.meta.url))
const { default: Resultado } = await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/ResultadoMexico.jsx', import.meta.url))
const perfil = { ingreso_laboral: '12000', periodicidad: '3', ingreso_variable: '1', presupuesto: '1', gastos_cubiertos: '1', ahorro_emergencia: '4', creditos: ['bancaria'] }
const analisis = { modelo_id: 'nexocredit-enif2024-logistica-v1', modelo_sha256: '1f6238b217583d0f5c00320d9caf3c331e422452104776b9b99b57a75440e621',
  pais: 'México', objetivo: 'algun_atraso_reportado', tipo: 'modelo_estadistico_entrenado', umbral: .18,
  fuente: 'https://www.inegi.org.mx/contenidos/programas/enif/2024/microdatos/enif_2024_bd_csv.zip',
  clase: 'perfil_no_asociado_a_atraso', atraso_reportado_estimado: false, estimacion_asociativa: .12,
  reglas_score_utilizadas: false, probabilidad_impago_futuro: null, requiere_azure: false, requiere_ollama: false,
  metricas_prueba: { filas: 783, auc_roc: .6054963570127504, sensibilidad: .7158469945355191, precision_positiva: .2673469387755102, exactitud: .47509578544061304, f1: .38930163447251115 },
  exactitud_siempre_sin_atraso: .7662835249042146, limites: 'Muestra transversal de encuesta; no autoriza créditos.' }
const render = (Componente, props) => renderToStaticMarkup(React.createElement(Componente, props))

test('no convierte campos vacíos ni ausencia de crédito en un perfil de ceros', () => {
  assert.equal(prepararPerfilMexico(null), null)
  assert.throws(() => prepararPerfilMexico(perfilMexicoVacio()), /Completa/)
  assert.throws(() => prepararPerfilMexico({ ...perfil, creditos: [] }), /crédito formal/)
  for (const cambios of [{ ingreso_laboral: '99888' }, { periodicidad: '0' }, { ahorro_emergencia: '9' }, { creditos: ['buro'] }, { creditos: ['bancaria', 'bancaria'] }]) assert.throws(() => prepararPerfilMexico({ ...perfil, ...cambios }))
  assert.deepEqual(prepararPerfilMexico(perfil), { ...perfil, ingreso_laboral: 12000, periodicidad: 3, ingreso_variable: 1, presupuesto: 1, gastos_cubiertos: 1, ahorro_emergencia: 4 })
})

test('formulario en evaluación captura preguntas ENIF sin pedir el atraso objetivo ni datos sensibles', () => {
  const html = render(Perfil, { perfil, change() {} })
  assert.equal((html.match(/<select /g) || []).length, 5)
  assert.equal((html.match(/type="checkbox"/g) || []).length, 10)
  assert.match(html, /max="98000"/)
  assert.match(html, /No se convierte automáticamente/)
  assert.doesNotMatch(html, /P6_3|sexo|discapacidad|nombre completo|RFC/)
})

test('sin perfil mantiene la opción explícita y no inventa un resultado estadístico', () => {
  assert.doesNotMatch(render(Perfil, { perfil: null, change() {} }), /<select|enif-ingreso/)
  assert.equal(render(Resultado, {}), '')
})

test('contrato rechaza probabilidades falsas, clases contradictorias o ausencia de métricas', () => {
  assert.equal(esAnalisisMexico(analisis), true)
  for (const cambios of [{ estimacion_asociativa: NaN }, { estimacion_asociativa: 2 }, { modelo_sha256: '' }, { probabilidad_impago_futuro: .12 }, { reglas_score_utilizadas: true }, { atraso_reportado_estimado: true }, { metricas_prueba: null }]) assert.equal(esAnalisisMexico({ ...analisis, ...cambios }), false)
})

test('salida muestra la baja capacidad y separa el porcentaje del impago futuro', () => {
  const html = render(Resultado, { analisis })
  assert.match(html, /Resultado del modelo mexicano/)
  assert.match(html, /AUC 0\.605/)
  assert.match(html, /Capacidad limitada/)
  assert.match(html, /NO es su probabilidad de dejar de pagar/)
  assert.match(html, /no usa las reglas de score/)
  assert.match(html, /ni lo decide Ollama/)
  assert.doesNotMatch(html, /Riesgo Bajo|Riesgo Alto|Aprobado/)
})

test('escapa textos y bloquea metadatos malformados en el contrato de la evaluación', () => {
  assert.match(render(Resultado, { analisis: { ...analisis, limites: '<script>NO</script>' } }), /&lt;script&gt;/)
  const evaluacion = { rfc: 'DEMO', margen_libre: 20000, nivel_riesgo_preliminar: 'Bajo', modo: 'demostracion', version_modelo: 'reglas-demo-v2', factores: ['Demo'], mensaje: 'Demo', guardado: false, analisis_mexico: analisis }
  assert.equal(validarEvaluacion(evaluacion), evaluacion)
  assert.throws(() => validarEvaluacion({ ...evaluacion, analisis_mexico: { ...analisis, modelo_id: 'otro' } }))
})

test('piloto empresarial no se presenta aprobado ni habilita decisiones por una métrica', () => {
  assert.equal(esControlPiloto(control), true)
  for (const cambios of [{ decision_automatizada_habilitada: true }, { uso_con_clientes_reales_habilitado: true },
    { validacion_empresarial: 'aprobada' }, { motivos_no_promocion: [] }]) assert.equal(esControlPiloto({ ...control, ...cambios }), false)
  const html = render(Resultado, { analisis: { ...analisis, control_uso: control, comparacion_modelos: comparacion } })
  assert.match(html, /Piloto empresarial/)
  assert.match(html, /modo sombra/)
  assert.match(html, /Validación empresarial pendiente/)
  assert.match(html, /No se demostró una mejora consistente/)
  assert.match(html, /no comparar sus AUC directamente/)
  for (const modelo of ['Random Forest', 'Gradient boosting', 'Regresión logística', 'Selección anidada']) assert.ok(html.includes(modelo))
})

test('no inventa resultados si el informe no está disponible y soporta registros históricos', () => {
  const no = { estado: 'no_disponible', promocion_automatica: false, motivo: 'Informe no disponible.' }
  assert.equal(esComparacionPiloto(no), true)
  const html = render(Resultado, { analisis: { ...analisis, control_uso: control, comparacion_modelos: no } })
  assert.match(html, /Informe no disponible/)
  assert.doesNotMatch(html, /<table/)
  assert.match(render(Resultado, { analisis }), /Registro histórico anterior al control del piloto/)
})

test('comparaciones inválidas o una mejora contradicha por el intervalo fallan cerrado', () => {
  assert.equal(esComparacionPiloto(comparacion), true)
  for (const cambios of [{ promocion_automatica: true }, { filas_desarrollo: 0 }, { modelo_servido_modificado: true }, { resultados: {} }]) assert.equal(esComparacionPiloto({ ...comparacion, ...cambios }), false)
  const falso = structuredClone(comparacion)
  falso.resultados.bosque.mejora_auc_demostrada_respecto_logistica = true
  assert.equal(esComparacionPiloto(falso), false)
  assert.equal(esAnalisisMexico({ ...analisis, comparacion_modelos: falso }), false)
})
