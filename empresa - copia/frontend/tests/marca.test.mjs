import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MARCA, EVENTO_SESION_VENCIDA, presentarDocumentoDemo, textoMarca } from '../src/interfaz/marca.mjs'
import { cargarComponente } from './helpers/cargar-componente.mjs'

const Panel = (await cargarComponente(new URL('../src/azure_search/PanelDocumentos.jsx', import.meta.url))).default
const Explicacion = (await cargarComponente(new URL('../src/azure_openai/Explicacion.jsx', import.meta.url))).default

test('título, favicon y evento de sesión usan la identidad nueva sin modificar el acceso', async () => {
  const html = await readFile(new URL('../index.html', import.meta.url), 'utf8')
  const icono = await readFile(new URL('../public/favicon.svg', import.meta.url), 'utf8')
  const [cliente, acceso] = await Promise.all(['cliente.js', 'Acceso.jsx'].map(file => readFile(new URL(`../src/autenticacion/${file}`, import.meta.url), 'utf8')))
  assert.ok(html.includes(`<title>${MARCA} | Riesgo crediticio</title>`))
  assert.ok(icono.includes(`<title>${MARCA}</title>`))
  assert.equal(EVENTO_SESION_VENCIDA, 'sesion-vencida')
  assert.match(cliente, /new Event\(EVENTO_SESION_VENCIDA\)/)
  assert.match(acceso, /addEventListener\(EVENTO_SESION_VENCIDA/)
  assert.match(acceso, /removeEventListener\(EVENTO_SESION_VENCIDA/)
  assert.doesNotMatch(html + icono + cliente + acceso, /PluriOne/i)
})

test('los textos de marca no inventan una razón social ni cambian identificadores técnicos', () => {
  assert.equal(textoMarca('PluriOne S.A. de C.V. / PluriOne / PLURIONE'), `${MARCA} / ${MARCA} / ${MARCA}`)
  assert.equal(textoMarca('plurione-uci-voting-candidato:1'), 'plurione-uci-voting-candidato:1')
})

test('la adaptación de alcance no atribuye la empresa original a la marca ficticia', () => {
  const original = { id: 'alcance-proyecto-v1-ALC-01', fuente: 'alcance-proyecto-v1', version: '1.0',
    titulo: 'Alcance del proyecto', seccion: 'ALC-01. Identificación',
    contenido: 'Se plantea para PluriOne S.A. de C.V., cuyo nombre comercial es Develop Talent & Technology, dedicada a servicios de consultoría, desarrollo de software y capacitación TI. No autoriza créditos.' }
  const copia = presentarDocumentoDemo(original)
  assert.equal(copia.id, original.id)
  assert.equal(copia.version, original.version)
  assert.equal(copia.fuente, original.fuente)
  assert.match(copia.contenido, /marca demostrativa NexoCredit/)
  assert.match(copia.contenido, /no identifica una razón social/)
  assert.doesNotMatch(copia.contenido, /PluriOne|Develop Talent|S\.A\. de C\.V\./i)
  assert.match(original.contenido, /PluriOne/)
})

test('catálogo y búsqueda adaptan solo la marca y conservan reglas, métricas y citas', () => {
  const base = { fuente: 'guia-demostracion-v1', titulo: 'Guía de demostración: reglas y límites de PluriOne', version: '1.0', aviso: 'Material demo.' }
  const fragmentos = [
    { ...base, id: 'demo-02', seccion: 'DEM-02. Reglas', contenido: 'Bajo: margen > 15 000 y score >= 680. Medio: margen > 7 000. No es política de PluriOne.' },
    { ...base, id: 'demo-03', seccion: 'DEM-03. Modelo', contenido: 'El modelo configurado es `plurione-uci-voting-candidato:1`. Sensibilidad: 32,01 %. No autoriza créditos.' },
    { ...base, id: 'alcance-01', fuente: 'alcance-proyecto-v1', seccion: 'ALC-01. Alcance', contenido: 'Alcance propuesto; no aprobado por PluriOne.' },
  ]
  const html = renderToStaticMarkup(createElement(Panel, { consulta: '', busy: false, error: '', resultados: fragmentos,
    catalogo: { estado: 'lista', fragmentos }, onConsultaChange: () => {}, submit: () => {}, reintentar: () => {} }))
  assert.doesNotMatch(html, /PluriOne|Develop Talent|NexoCredit S\.A\./i)
  assert.match(html, /Presentación de las guías demo adaptada a NexoCredit/)
  assert.match(html, /2 guías · 3 secciones/)
  assert.match(html, /15 000/)
  assert.match(html, /7 000/)
  assert.match(html, /32,01/)
  assert.match(html, /versión 1\.0/)
  assert.match(html, /contenido original en Azure AI Search no se modifica/)
})

test('no reescribe fuentes ajenas ni datos de los solicitantes', () => {
  const original = { fuente: 'expediente-ajeno', titulo: 'PluriOne', contenido: 'PluriOne S.A. de C.V.' }
  assert.equal(presentarDocumentoDemo(original), original)
})

test('la explicación presenta la nueva marca sin alterar las referencias o ejecutar HTML', () => {
  const data = { explicacion: 'PluriOne: margen 20000. <script>demo</script>',
    fuentes: [{ id: 'guia-demo-02', titulo: 'Guía de PluriOne', seccion: 'DEM-02', version: '1.0' }],
    implementacion: 'gpt-5-mini-1', aviso: 'No autoriza créditos.' }
  const html = renderToStaticMarkup(createElement(Explicacion, { estado: { estado: 'lista', data } }))
  assert.match(html, /NexoCredit: margen 20000/)
  assert.match(html, /Guía de NexoCredit/)
  assert.match(html, /DEM-02 · versión de fuente 1\.0/)
  assert.match(html, /gpt-5-mini-1/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /PluriOne|<script>/i)
  assert.equal(data.fuentes[0].titulo, 'Guía de PluriOne')
})
