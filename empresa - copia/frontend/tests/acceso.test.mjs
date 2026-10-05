import test from 'node:test'
import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { cargarComponente } from './helpers/cargar-componente.mjs'

test('la nueva pantalla conserva los estados de acceso de Microsoft', async t => {
  const source = new URL('../src/autenticacion/PantallaAcceso.jsx', import.meta.url)
  const { default: PantallaAcceso } = await cargarComponente(source)
  const render = overrides => renderToStaticMarkup(createElement(PantallaAcceso, {
    busy: false, ready: true, error: '', wrongOrigin: false,
    onLogin: () => {}, onLogout: () => {}, ...overrides,
  }))

  await t.test('lista para iniciar sesión sin campos de contraseñas ni tokens', () => {
    const html = render()
    assert.match(html, /Iniciar sesión con Microsoft/)
    assert.match(html, /Cerrar sesión de Microsoft \/ cambiar cuenta/)
    assert.match(html, /aria-labelledby="access-title"/)
    assert.match(html, /NexoCredit/)
    assert.doesNotMatch(html, /PluriOne|S\.A\. de C\.V\./i)
    assert.doesNotMatch(html, /disabled|<input|role="status"/)
  })

  await t.test('durante la verificación bloquea el botón y anuncia el estado', () => {
    const html = render({ busy: true })
    assert.match(html, /aria-busy="true"/)
    assert.match(html, /disabled=""/)
    assert.match(html, /role="status">Verificando sesión/)
    assert.doesNotMatch(html, /Cerrar sesión de Microsoft/)
  })

  await t.test('no permite iniciar antes de cargar la configuración', () => {
    const html = render({ ready: false })
    assert.match(html, /disabled=""/)
    assert.doesNotMatch(html, /Cerrar sesión de Microsoft/)
  })

  await t.test('un origen incorrecto muestra el enlace autorizado, no botones de acceso', () => {
    const html = render({ wrongOrigin: true })
    assert.match(html, /href="http:\/\/localhost:8080\/"/)
    assert.match(html, /NexoCredit en localhost:8080/)
    assert.doesNotMatch(html, /<button/)
  })

  await t.test('los errores se muestran como texto y no se interpretan como HTML', () => {
    const html = render({ error: '<script>alert("demo")</script>' })
    assert.match(html, /role="alert"/)
    assert.match(html, /&lt;script&gt;/)
    assert.doesNotMatch(html, /<script/)
  })
})
