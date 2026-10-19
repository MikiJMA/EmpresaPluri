import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'
import { SECCIONES, rutaDeSeccion, seccionDesdeHash, seccionDesdeRuta } from '../src/interfaz/secciones.mjs'

const { default: Inicio } = await cargarComponente(new URL('../src/interfaz/ResumenInicio.jsx', import.meta.url))
const { default: Marco } = await cargarComponente(new URL('../src/interfaz/MarcoAplicacion.jsx', import.meta.url))

test('el resumen muestra seis accesos reales sin cifras, nombres o servicios inventados', () => {
  const html = renderToStaticMarkup(createElement(Inicio, { onSeccionChange: () => {} }))
  assert.equal((html.match(/class="home-shortcut"/g) || []).length, 6)
  for (const id of ['evaluacion', 'creditos', 'laboratorio', 'indicadores', 'historial', 'documentos']) {
    assert.ok(html.includes(`href="${rutaDeSeccion(id)}"`))
    assert.ok(SECCIONES.some(([key]) => key === id))
  }
  assert.match(html, /Nueva evaluación/)
  assert.match(html, /no autoriza créditos/)
  assert.doesNotMatch(html, /Julian|Villegas|<form|<input|<button|API_KEY|PluriOne/)
})

test('cada acceso activa la sección de su enlace y nueva evaluación respeta el guardado en curso', () => {
  const llamadas = []
  const vista = Inicio({ onSeccionChange: id => llamadas.push(id) })
  for (const enlace of vista.props.children[1].props.children) {
    enlace.props.onClick()
    assert.equal(llamadas.at(-1), SECCIONES.find(([, , , ruta]) => ruta === enlace.props.href)[0])
  }
  vista.props.children[0].props.children[1].props.onClick({ preventDefault: () => assert.fail('No debe bloquearse') })
  assert.equal(llamadas.at(-1), 'evaluacion')
  let reinicios = 0
  let bloqueos = 0
  const pendiente = Inicio({ busy: true, onNuevaEvaluacion: () => reinicios++ })
  const enlace = pendiente.props.children[0].props.children[1]
  assert.equal(enlace.props['aria-disabled'], true)
  enlace.props.onClick({ preventDefault: () => bloqueos++ })
  assert.equal(reinicios, 0)
  assert.equal(bloqueos, 1)
  Inicio({ onNuevaEvaluacion: () => reinicios++ }).props.children[0].props.children[1].props.onClick({})
  assert.equal(reinicios, 1)
})

test('el saludo procede de la cuenta verificada y no atribuye Microsoft a una cuenta local', () => {
  const html = renderToStaticMarkup(createElement(Marco, { user: { nombre: 'Ana López', roles: ['Analista'], proveedor: 'local' }, seccion: 'seguimiento' }))
  assert.match(html, /<h1>Hola, Ana<\/h1>/)
  assert.match(html, /Ana López/)
  assert.match(html, /Acceso con cuenta local/)
  assert.doesNotMatch(html, /Julian|Villegas|Acceso con Microsoft Entra ID/)
  const seguro = renderToStaticMarkup(createElement(Marco, { user: { nombre: '<script>alert(1)</script>', roles: [] }, seccion: 'seguimiento' }))
  assert.doesNotMatch(seguro, /<script>/)
  assert.match(seguro, /&lt;script&gt;/)
})

test('la aplicación conserva dashboard, formularios y avisos inferiores al añadir el inicio', async () => {
  const app = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8')
  assert.match(app, /seccionDesdeHash\(window.location.hash\) \|\| seccionDesdeRuta\(window.location.pathname\) \|\| 'seguimiento'/)
  assert.equal(app.split('id="seguimiento"').length - 1, 1)
  assert.equal(app.split('<Dashboard revision={revision} />').length - 1, 1)
  assert.ok(app.indexOf('<ResumenInicio ') < app.indexOf('<Dashboard revision={revision} />'))
  assert.ok(app.indexOf('<BuscadorDocumentos />') < app.indexOf('<EstadoProveedores />'))
  assert.match(app, /function nuevaEvaluacion\(\) \{\s*if \(busy\) return\s*intentoVisible\.current \+= 1/)
  assert.match(app, /onNuevaEvaluacion={nuevaEvaluacion} busy={busy}/)
  assert.doesNotMatch(app, /location\.reload|localStorage\.clear|sessionStorage\.clear/)
})

test('los enlaces directos y Atrás mantienen la sección sin interpretar anclas desconocidas', async () => {
  for (const [id] of SECCIONES) assert.equal(seccionDesdeHash(`#${id}`), id)
  for (const hash of ['', '#contenido-principal', '#desconocido', '#<script>']) assert.equal(seccionDesdeHash(hash), null)
  for (const [id, , , ruta] of SECCIONES) {
    assert.equal(seccionDesdeRuta(ruta), id)
    assert.equal(rutaDeSeccion(id), ruta)
  }
  for (const ruta of ['/desconocido', 'evaluaciones']) assert.equal(seccionDesdeRuta(ruta), null)
  assert.equal(seccionDesdeRuta('/evaluaciones//'), 'evaluacion')
  const app = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8')
  assert.match(app, /window.addEventListener\('popstate', sincronizarRuta\)/)
  assert.match(app, /window.history.pushState\(null, '', ruta\)/)
  assert.match(app, /if \(destino\) setSeccion\(destino\)/)
  assert.match(app, /window.addEventListener\('hashchange', sincronizarRuta\)/)
  assert.match(app, /window.removeEventListener\('hashchange', sincronizarRuta\)/)
})

test('los controles de sesión móviles quedan sobre el fondo fijo, sin desplazarse fuera de la pantalla', async () => {
  const css = await readFile(new URL('../src/styles/Enterprise.css', import.meta.url), 'utf8')
  const movil = css.slice(css.indexOf('@media (max-width: 1000px)'))
  assert.match(movil, /body \.session-bar \{ position: relative; top: auto; right: auto;/)
  assert.match(css, /body \.session-bar \{[^}]*z-index: 15/)
  assert.match(css, /\.enterprise-app \.enterprise-sidebar-note p \{[^}]*color: #cfe0ff/)
})
