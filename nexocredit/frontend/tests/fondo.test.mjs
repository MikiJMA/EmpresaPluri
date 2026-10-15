import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const asset = new URL('../public/images/nexocredit-background-v1.png', import.meta.url)

test('el fondo generado es un PNG local apaisado y de tamaño limitado', async () => {
  const image = await readFile(asset)
  assert.equal(image.subarray(0, 8).toString('hex'), '89504e470d0a1a0a')
  assert.equal(image.subarray(12, 16).toString(), 'IHDR')
  const width = image.readUInt32BE(16)
  const height = image.readUInt32BE(20)
  assert.ok(width >= 1280 && height >= 720)
  assert.ok(width / height > 1.6 && width / height < 1.9)
  assert.ok(image.length < 2 * 1024 * 1024, 'El fondo no debe exceder 2 MiB')
})

test('el panel usa una imagen local con capa suave y el login mantiene su diseño diagonal', async () => {
  const access = await readFile(new URL('../src/styles/Acceso.css', import.meta.url), 'utf8')
  assert.match(access, /background: linear-gradient\(160deg, #1b1a63 0%, #4338ca 100%\)/)
  assert.doesNotMatch(access, /url\(/)
  const enterprise = await readFile(new URL('../src/styles/Enterprise.css', import.meta.url), 'utf8')
  assert.ok(enterprise.includes("url('/images/nexocredit-background-v1.png')"))
  assert.match(enterprise, /linear-gradient\(rgba\(234, 241, 255, \.2\)/)
  assert.match(enterprise, /background-color: #eaf1ff/)
  assert.doesNotMatch(enterprise, /url\(['"]?https?:\/\//)
  assert.match(enterprise, /\.enterprise-app \.card, \.enterprise-app \.finance-panel \{[^}]*background: #fff/)
})

test('el fondo continúa detrás de todas las secciones y no termina en una altura fija', async () => {
  const css = await readFile(new URL('../src/styles/Enterprise.css', import.meta.url), 'utf8')
  const backdrop = /\.enterprise-app::before \{([^}]+)\}/.exec(css)?.[1]
  assert.ok(backdrop)
  assert.match(backdrop, /position: fixed/)
  assert.match(backdrop, /inset: 0/)
  assert.match(backdrop, /pointer-events: none/)
  assert.ok(backdrop.includes("url('/images/nexocredit-background-v1.png')"))
  assert.match(backdrop, /background-size: cover/)
  assert.doesNotMatch(css, /auto 1080px|680px, #f5f6f8 1080px/)
  for (const selector of ['.finance-panel', '.documents-guide', '.dashboard-metrics', '#laboratorio details', '.evaluation-detail', '.history-heading']) {
    assert.ok(css.includes(selector), `Falta el estilo común de ${selector}`)
  }
})

test('el acceso, la sesión y las secciones internas comparten esquinas rectas sin alterar controles', async () => {
  const geometry = await readFile(new URL('../src/styles/EsquinasRectas.css', import.meta.url), 'utf8')
  for (const scope of ['.enterprise-app', '.access-screen', '.session-bar']) {
    assert.ok(geometry.includes(`${scope},`))
    assert.ok(geometry.includes(`${scope} *,`))
  }
  assert.match(geometry, /border-radius: 0 !important;/)
  assert.doesNotMatch(geometry, /outline:|pointer-events:|display:|overflow:|opacity:/)
  const main = await readFile(new URL('../src/main.jsx', import.meta.url), 'utf8')
  const preview = await readFile(new URL('./previsualizar-interfaz.mjs', import.meta.url), 'utf8')
  assert.match(main, /import '\.\/styles\/EsquinasRectas\.css'/)
  assert.ok(preview.includes('styles/EsquinasRectas.css'))
})
