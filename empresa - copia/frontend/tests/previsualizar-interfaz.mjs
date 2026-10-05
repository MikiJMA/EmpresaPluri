import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'
import { createElement as h } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { MARCA } from '../src/interfaz/marca.mjs'

// Vista estática y aislada para QA visual. No inicia MSAL ni consulta/guarda datos.
const cargar = async path => (await cargarComponente(new URL(`../src/${path}.jsx`, import.meta.url))).default
const Marco = await cargar('interfaz/MarcoAplicacion')
const Indicadores = await cargar('evaluacion_crediticia/componentes/IndicadoresEscenario')
const Formulario = await cargar('evaluacion_crediticia/componentes/EvaluationForm')
const Resultado = await cargar('evaluacion_crediticia/componentes/EvaluationResult')
const Tabla = await cargar('evaluacion_crediticia/componentes/TablaHistorial')
const Documentos = await cargar('azure_search/PanelDocumentos')
const cssFiles = ['styles/index.css', 'styles/App.css', 'styles/History.css', 'styles/Detail.css', 'dashboard/Dashboard.css', 'styles/Bento.css', 'styles/Enterprise.css', 'styles/Acceso.css', 'azure_search/Documentos.css']
const css = (await Promise.all(cssFiles.map(path => readFile(new URL(`../src/${path}`, import.meta.url), 'utf8')))).join('\n')
const fragmentos = []
for (const file of ['01_alcance_proyecto.md', '02_guia_demostracion.md']) {
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
const form = { rfc: 'AAAA010101AA1', ingresos_mensuales: '30000', gastos_mensuales: '10000', deuda_actual: '0', pagos_mensuales_creditos: '0', dias_atraso_actual: '0', score_buro_actual: '700' }
const result = { rfc: form.rfc, margen_libre: 20000, nivel_riesgo_preliminar: 'Bajo', factores: ['Margen mensual: ingresos menos gastos = 20,000 MXN.', 'Regla demo: margen > 15,000 MXN y score capturado ≥ 680.'], mensaje: 'Resultado de prueba visual. No autoriza créditos ni representa un modelo predictivo.', version_modelo: 'reglas-demo-v1', guardado: false }
const usuario = { nombre: 'Usuario de prueba', roles: ['Analista'] }
const children = [
  h(Indicadores, { result, submitted: form, key: 'kpis' }),
  h('div', { className: 'demo-banner', key: 'demo' }, h('p', null, h('strong', null, 'Vista de prueba'), ' Datos ficticios para QA visual. No envía solicitudes ni guarda evaluaciones.')),
  h('div', { className: 'workspace', id: 'evaluacion', key: 'form' }, h(Formulario, { form, busy: false, error: '', change: () => {}, submit: () => {} }), h(Resultado, { result, submitted: form, busy: false })),
  h('div', { id: 'historial', key: 'history' }, h('section', { className: 'history card' }, h('div', { className: 'history-heading' }, h('div', null, h('h2', null, 'Historial de evaluaciones'), h('p', null, 'Registro ficticio para verificar la tabla.')), h('button', { type: 'button', disabled: true }, 'Actualizar')), h(Tabla, { items: [{ ...result, id: 'prueba-visual', fecha: '2026-09-30T12:00:00Z' }], selected: 'prueba-visual', onSelected: () => {} }))),
  ...[['seguimiento', 'Dashboard de evaluaciones'], ['laboratorio', 'Laboratorio académico · Azure ML']].map(([id, title]) => h('section', { id, className: 'card', style: { marginTop: 24 }, key: id }, h('h2', null, title), h('p', null, 'Sección de la aplicación. Esta vista aislada no consulta servicios ni muestra registros reales.'))),
  documentos,
]
const markup = renderToStaticMarkup(h('div', null,
  h('aside', { className: 'session-bar', 'aria-label': 'Sesión de prueba' }, h('span', null, 'Usuario de prueba · Analista'), h('button', { type: 'button', disabled: true }, 'Cerrar sesión')),
  h(Marco, { user: usuario, seccion: soloDocumentos ? 'documentos' : 'evaluacion', onSeccionChange: () => {} },
    soloDocumentos ? [h('div', { className: 'demo-banner', key: 'aviso' }, h('p', null, h('strong', null, 'Vista de prueba'), ' Guías demo de archivos locales. No consulta Azure ni guarda información.')), documentos] : children),
))
const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${MARCA} · QA visual aislada</title><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&amp;family=IBM+Plex+Mono:wght@500;600;700&amp;display=swap" rel="stylesheet"><style>${css}</style></head><body>${markup}</body></html>`
const server = createServer((request, response) => {
  if (request.url !== '/') { response.writeHead(404).end(); return }
  response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' })
  response.end(html)
})
server.listen(0, '127.0.0.1', () => process.stdout.write(`Vista estática de QA (PID ${process.pid}): http://127.0.0.1:${server.address().port}/\n`))
process.stdin.on('data', text => { if (text.toString().trim() === 'detener') { server.close(); process.stdin.destroy() } })
process.on('SIGINT', () => server.close())
process.on('SIGTERM', () => server.close())
