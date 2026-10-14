import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'
import { createElement as h } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { MARCA } from '../src/interfaz/marca.mjs'

// Vista estática y aislada para QA visual. No inicia MSAL ni consulta/guarda datos.
const cargar = async path => (await cargarComponente(new URL(`../src/${path}.jsx`, import.meta.url))).default
const Marco = await cargar('interfaz/MarcoAplicacion')
const Inicio = await cargar('interfaz/ResumenInicio')
const Acceso = await cargar('autenticacion/PantallaAcceso')
const Indicadores = await cargar('evaluacion_crediticia/componentes/IndicadoresEscenario')
const Formulario = await cargar('evaluacion_crediticia/componentes/EvaluationForm')
const Resultado = await cargar('evaluacion_crediticia/componentes/EvaluationResult')
const Tabla = await cargar('evaluacion_crediticia/componentes/TablaHistorial')
const Documentos = await cargar('azure_search/PanelDocumentos')
const Finanzas = await cargar('datos_financieros/PanelFinanciero')
const Identidad = await cargar('evaluacion_crediticia/componentes/PanelIdentidad')
const Laboratorio = await cargar('azure_ml/PanelLaboratorio')
const { PanelCredito } = await cargarComponente(new URL('../src/seguimiento_crediticio/PanelCredito.jsx', import.meta.url))
const cssFiles = ['styles/index.css', 'styles/App.css', 'styles/History.css', 'styles/Detail.css', 'dashboard/Dashboard.css', 'azure_search/Documentos.css', 'datos_financieros/Finanzas.css', 'styles/Bento.css', 'styles/Enterprise.css', 'styles/Acceso.css', 'styles/ScoreAyuda.css', 'styles/Identidad.css', 'seguimiento_crediticio/Seguimiento.css', 'styles/EsquinasRectas.css']
const css = (await Promise.all(cssFiles.map(path => readFile(new URL(`../src/${path}`, import.meta.url), 'utf8')))).join('\n')
const fragmentos = []
for (const file of ['01_alcance_proyecto.md', '02_guia_demostracion.md', '03_reglas_demo_v2.md']) {
  const text = await readFile(new URL(`../../backend/app/integraciones/busqueda_azure_ai_search/contenidos_demo/${file}`, import.meta.url), 'utf8')
  const titulo = text.split(/\r?\n/)[0].replace(/^# /, '')
  const fuente = /^Identificador: (.+)$/m.exec(text)[1].trim()
  const version = /^Versión: (.+)$/m.exec(text)[1].trim()
  for (const section of text.split(/^## /m).slice(1)) {
    const [seccion, ...body] = section.split(/\r?\n/)
    fragmentos.push({ id: `${fuente}-${seccion}`, fuente, titulo, version, seccion, contenido: body.join('\n').trim(),
      aviso: 'Material académico de demostración. No es una política oficial ni autoriza créditos.' })
  }
}
const documentos = h(Documentos, { key: 'documentos', consulta: '', busy: false, error: '', resultados: null,
  catalogo: { estado: 'lista', fragmentos }, onConsultaChange: () => {}, submit: () => {}, reintentar: () => {} })
const soloDocumentos = process.argv.includes('--documentos')
const soloSeguimiento = process.argv.includes('--seguimiento')
const fixtureSeguimiento = { resumen: { fecha_corte:'2026-10-12',total_pactado:'100.00',total_pagado:'20.00',saldo_pendiente:'80.00',saldo_vencido:'30.00',dias_atraso_maximo:5,
  cuotas_vencidas:1,cuotas_completas_vencidas:0,puntualidad_cuotas_vencidas_pct:'0.00',cuotas:[{id:'fixture-1',vencimiento:'2026-10-07',importe:'50.00',pagado:'20.00',saldo:'30.00',dias_atraso:5,estado:'Vencida'},
    {id:'fixture-2',vencimiento:'2026-10-17',importe:'50.00',pagado:'0.00',saldo:'50.00',dias_atraso:0,estado:'Pendiente'}],acciones_seguimiento:['Revisar cuotas vencidas y registrar sólo pagos realmente recibidos.'],aviso:'Datos ficticios de QA. No autoriza créditos ni confirma depósitos bancarios.'},
  indicadores:{pagos_sobre_ingresos_pct:'8.33',gastos_sobre_ingresos_pct:'33.33',deuda_sobre_ingreso_mensual_veces:'1.67',aviso:'Datos capturados, no verificados. No cambian el riesgo demo.'},pagos:[{id:'pago-fixture',cuota_id:'fixture-1',fecha_pago:'2026-10-12',importe:'20.00'}] }
const seguimiento = h('section',{className:'card ledger',id:'creditos'},h('h2',null,'Créditos y pagos · DEMO'),h('p',null,'Vista estática aislada de QA. No consulta ni escribe datos.'),h(PanelCredito,{data:fixtureSeguimiento}),
  h('article',{className:'ledger-alert'},h('strong',null,'Pendiente · cuota vencida'),h('p',null,'Saldo de última revisión: $30.00 MXN. Atendida no significa pagada.'),h('label',null,'Motivo de atención',h('textarea',{disabled:true,placeholder:'Ejercicio ficticio de revisión'})),h('button',{disabled:true,type:'button'},'Registrar atención')))
const form = { rfc: 'AAAA010101AA1', ingresos_mensuales: '30000', gastos_mensuales: '11666.67', deuda_actual: '0', pagos_mensuales_creditos: '0', dias_atraso_actual: '0', score_buro_actual: '700' }
const result = { rfc: form.rfc, margen_libre: 18333.33, nivel_riesgo_preliminar: 'Bajo', factores: ['Margen mensual: 18,333.33 MXN; mínimo por margen Bajo.', 'Score 700: Bajo. Se conserva el mayor riesgo de score y margen.'], mensaje: 'Resultado de prueba visual. No autoriza créditos ni representa un modelo predictivo.', version_modelo: 'reglas-demo-v2', guardado: false }
const usuario = { nombre: 'Usuario de prueba', roles: ['Analista'] }
const children = [
  h('div', { id: 'seguimiento', key: 'inicio' }, h(Inicio, { onSeccionChange: () => {} })),
  h(Indicadores, { result, submitted: form, key: 'kpis' }),
  h('div', { className: 'demo-banner', key: 'demo' }, h('p', null, h('strong', null, 'Vista de prueba'), ' Datos ficticios para QA visual. No envía solicitudes ni guarda evaluaciones.')),
  h('div', { className: 'workspace', id: 'evaluacion', key: 'form' }, h(Formulario, { form, busy: false, error: '', change: () => {}, submit: () => {}, identidad: h(Identidad, { curp: '', disabled: false, busy: false, change: () => {}, revisar: () => {} }) }), h(Resultado, { result, submitted: form, busy: false })),
  h('div', { id: 'historial', key: 'history' }, h('section', { className: 'history card' }, h('div', { className: 'history-heading' }, h('div', null, h('h2', null, 'Historial de evaluaciones'), h('p', null, 'Registro ficticio para verificar la tabla.')), h('button', { type: 'button', disabled: true }, 'Actualizar')), h(Tabla, { items: [{ ...result, id: 'prueba-visual', fecha: '2026-09-30T12:00:00Z' }], selected: 'prueba-visual', onSelected: () => {} }))),
  ...[['dashboard', 'Dashboard de evaluaciones'], ['laboratorio', 'Laboratorio académico · Azure ML']].map(([id, title]) => h('section', { id, className: 'card', style: { marginTop: 24 }, key: id }, h('h2', null, title), h('p', null, 'Sección de la aplicación. Esta vista aislada no consulta servicios ni muestra registros reales.'))),
  h(Finanzas, { key: 'finanzas', estado: 'error', error: 'Vista aislada de QA: no consulta fuentes financieras ni muestra datos reales.', reintentar: () => {} }),
  documentos,
]
const markup = renderToStaticMarkup(h('div', null,
  h('aside', { className: 'session-bar', 'aria-label': 'Sesión de prueba' }, h('span', null, 'Usuario de prueba · Analista'), h('button', { type: 'button', disabled: true }, 'Cerrar sesión')),
  h(Marco, { user: usuario, seccion: soloSeguimiento ? 'creditos' : soloDocumentos ? 'documentos' : 'seguimiento', onSeccionChange: () => {} },
    soloSeguimiento ? seguimiento : soloDocumentos ? [h('div', { className: 'demo-banner', key: 'aviso' }, h('p', null, h('strong', null, 'Vista de prueba'), ' Guías demo de archivos locales. No consulta Azure ni guarda información.')), documentos] : children),
))
const paginaPrincipal = content => `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${MARCA} · QA visual aislada</title><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;800&amp;display=swap" rel="stylesheet"><style>${css}</style></head><body>${content}</body></html>`
const html = paginaPrincipal(markup)
const resumenHtml = paginaPrincipal(renderToStaticMarkup(h('div', null,
  h('aside', { className: 'session-bar', 'aria-label': 'Sesión de prueba' }, h('span', null, 'Usuario de prueba · Analista · Cuenta local'), h('button', { type: 'button', disabled: true }, 'Cerrar sesión')),
  h(Marco, { user: { ...usuario, proveedor: 'local' }, seccion: 'seguimiento', onSeccionChange: () => {} },
    h('div', { id: 'seguimiento' }, h(Inicio, { onSeccionChange: () => {} })),
    h('p', null, 'Vista aislada de QA. No inicia sesión, consulta APIs ni guarda datos.')))))
const paginaScoreQA = vacio => paginaPrincipal(renderToStaticMarkup(h(Marco, { user: { ...usuario, proveedor: 'local' }, seccion: 'evaluacion', onSeccionChange: () => {} },
  h('p', null, 'Vista aislada de QA: datos ficticios. No consulta API ni guarda evaluaciones.'),
  h(Indicadores, { result: vacio ? null : result, submitted: vacio ? null : form }),
  h('div', { className: 'workspace', id: 'evaluacion' }, h(Formulario, { form, busy: false, error: '', change: () => {}, submit: () => {} })))))
const modeloLocalQA = JSON.parse(await readFile(new URL('../../backend/app/integraciones/prediccion_local/artefactos/modelo.json', import.meta.url), 'utf8'))
const estadoMLQA = { proveedor: 'local', configurado: true, origen: 'scikit-learn local',
  modelo_configurado: modeloLocalQA.modelo_id, metricas_prueba: modeloLocalQA.metricas.prueba }
const valoresMLQA = Object.fromEntries(modeloLocalQA.columnas.map(n => [n, n === 'LIMIT_BAL' ? '200000' : n.startsWith('PAY_AMT') ? '3000' : '0']))
const laboratorioHtml = paginaPrincipal(renderToStaticMarkup(h(Marco, { user: { ...usuario, proveedor: 'local' }, seccion: 'laboratorio', onSeccionChange: () => {} },
  h('div', { id: 'laboratorio' }, h(Laboratorio, { values: valoresMLQA, estado: estadoMLQA,
    status: 'Vista aislada de QA: artefacto local incluido; no consulta API, inicia sesión ni guarda información.',
    consulta: 'pendiente', busy: false, error: '', result: null, submit: () => {}, change: () => {}, cargarEjemplo: () => {} })))))
const crearAcceso = overrides => renderToStaticMarkup(h(Acceso, { busy: false, ready: true, error: '', wrongOrigin: false,
  local: { habilitado: true, cuentas_disponibles: true }, onLogin: () => {}, onLogout: () => {}, onLocalLogin: () => {}, ...overrides }))
const paginaAcceso = overrides => `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${MARCA} · QA de acceso aislada</title><link href="https://fonts.googleapis.com/css2?family=Newsreader:wght@500;600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;800&amp;display=swap" rel="stylesheet"><style>${css}</style></head><body>${crearAcceso(overrides)}</body></html>`
const fondo = await readFile(new URL('../public/images/nexocredit-background-v1.png', import.meta.url))
// Un iframe de ancho conocido activa las media queries reales, sin alterar el navegador.
const movilHtml = path => `<!doctype html><html lang="es"><head><meta charset="utf-8"><title>${MARCA} · QA móvil 390 px</title></head><body style="margin:0;background:#e2e8f0"><iframe title="Vista móvil de prueba" src="${path}" style="display:block;width:390px;max-width:100%;height:844px;border:0;margin:24px auto"></iframe></body></html>`
const paginas = new Map([['/', html], ['/acceso', paginaAcceso()],
  ['/resumen', resumenHtml], ['/movil-resumen', movilHtml('/resumen')],
  ['/score', paginaScoreQA(false)], ['/score-vacio', paginaScoreQA(true)], ['/movil-score', movilHtml('/score')],
  ['/laboratorio', laboratorioHtml], ['/movil-laboratorio', movilHtml('/laboratorio')],
  ['/acceso-microsoft', paginaAcceso({ local: { habilitado: false } })],
  ['/acceso-error', paginaAcceso({ error: 'No se pudo completar el acceso. Vista aislada de QA: no inicia sesión.' })],
  ['/movil', movilHtml('/')], ['/movil-acceso', movilHtml('/acceso')]])
const server = createServer((request, response) => {
  if (request.url === '/images/nexocredit-background-v1.png') {
    response.writeHead(200, { 'Content-Type': 'image/png', 'Cache-Control': 'no-store' })
    response.end(fondo)
    return
  }
  if (!paginas.has(request.url)) { response.writeHead(404).end(); return }
  response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' })
  response.end(paginas.get(request.url))
})
server.listen(0, '127.0.0.1', () => process.stdout.write(`Vista estática de QA (PID ${process.pid}): http://127.0.0.1:${server.address().port}/\n`))
process.stdin.on('data', text => { if (text.toString().trim() === 'detener') { server.close(); process.stdin.destroy() } })
process.on('SIGINT', () => server.close())
process.on('SIGTERM', () => server.close())
