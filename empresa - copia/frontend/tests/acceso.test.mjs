import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
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

  await t.test('adapta el diseño diagonal con marca vigente y controles accesibles en móvil', async () => {
    const html = render({ local: { habilitado: true, cuentas_disponibles: true } })
    assert.match(html, /<aside class="access-panel" aria-hidden="true">/)
    assert.match(html, /class="access-waves"/)
    assert.match(html, /Acceso seguro para analistas y administradores/)
    assert.match(html, /Accede a tu espacio de análisis/)
    assert.match(html, /<label for="local-usuario">/)
    assert.match(html, /<label for="local-password">/)
    assert.doesNotMatch(html, /PluriOne|<script|Inicia sesión con una cuenta local o Microsoft autorizada|Tus evaluaciones permanecen en PostgreSQL/)
    const css = await readFile(new URL('../src/styles/Acceso.css', import.meta.url), 'utf8')
    assert.match(css, /clip-path: polygon\(0 0, 100% 0, 88% 100%, 0 100%\)/)
    assert.match(css, /@media \(max-width: 900px\)\s*\{\s*\.access-screen \.access-panel \{ display: none; \}/)
    assert.doesNotMatch(css, /height: 100vh;\s*overflow: hidden|position: fixed/)
    assert.match(css, /@media \(prefers-reduced-motion: reduce\)/)
  })

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

  await t.test('acceso local habilitado muestra usuario y contraseña sin llaves cloud', () => {
    const html = render({ local: { habilitado: true, cuentas_disponibles: true }, onLocalLogin: () => {} })
    assert.match(html, /Usuario local/)
    assert.match(html, /type="password"/)
    assert.match(html, /autoComplete="current-password"/)
    assert.match(html, /mínimo 6 caracteres/)
    assert.match(html, /id="local-password"[^>]*minLength="6"[^>]*maxLength="128"/)
    assert.match(html, /Entrar con cuenta local/)
    assert.match(html, /Iniciar sesión con Microsoft/)
    assert.doesNotMatch(html, /API_KEY|LOCAL_AUTH_SECRET|Bmx-Token/)
  })

  await t.test('el origen Microsoft no bloquea cuentas locales', () => {
    const html = render({ wrongOrigin: true, local: { habilitado: true, cuentas_disponibles: true } })
    assert.match(html, /Entrar con cuenta local/)
    assert.doesNotMatch(html, /Iniciar sesión con Microsoft/)
    assert.match(html, /localhost:8080/)
  })

  await t.test('sin cuentas informa cómo crear una y bloquea el formulario', () => {
    const html = render({ local: { habilitado: true, cuentas_disponibles: false } })
    assert.match(html, /Todavía no hay cuentas locales/)
    assert.match(html, /Crear usuario local/)
    assert.match(html, /id="local-password"[^>]*disabled=""/)
  })
})
