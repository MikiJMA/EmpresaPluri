import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

// Ejecuta el cliente real con HTTP simulado; no conecta Microsoft ni usa llaves.
async function cargarCliente(t, responder) {
  const originals = { fetch: globalThis.fetch, window: globalThis.window }
  const eventos = []
  globalThis.window = { location: { origin: 'http://localhost:8080' }, dispatchEvent: event => eventos.push(event.type) }
  globalThis.fetch = responder
  t.after(() => { globalThis.fetch = originals.fetch; globalThis.window = originals.window })
  const path = new URL('../src/autenticacion/cliente.js', import.meta.url)
  const marca = new URL('../src/interfaz/marca.mjs', import.meta.url).href
  const source = (await readFile(path, 'utf8'))
    .replaceAll('import.meta.env.VITE_API_URL', "'/'")
    .replace("'../interfaz/marca.mjs'", JSON.stringify(marca))
  const module = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}#${crypto.randomUUID()}`)
  return { module, eventos }
}

const respuesta = (data, status = 200) => ({ ok: status >= 200 && status < 300, status, json: async () => data })
const identidad = { id: 'usuario-demo', nombre: 'Analista ficticio', roles: ['Analista'], proveedor: 'local' }
const token = { access_token: 'token-ficticio-de-prueba', token_type: 'bearer', expires_in: 1800, user: identidad }

test('login local verifica identidad, adjunta bearer y no carga configuración Microsoft', async t => {
  const calls = []
  const { module } = await cargarCliente(t, async (url, options) => {
    calls.push({ url, options })
    return respuesta(url.endsWith('/local/login') ? token : identidad)
  })
  assert.deepEqual(await module.iniciarSesionLocal('analista', 'password-ficticio-para-test'), identidad)
  await module.fetchAutenticado('/api/v1/evaluaciones', { headers: { Authorization: 'otro-token' }, redirect: 'follow' })
  assert.equal(calls.length, 3)
  assert.deepEqual(JSON.parse(calls[0].options.body), { usuario: 'analista', password: 'password-ficticio-para-test' })
  assert.equal(calls[1].options.headers.get('Authorization'), `Bearer ${token.access_token}`)
  assert.equal(calls[2].options.headers.get('Authorization'), `Bearer ${token.access_token}`)
  assert.equal(calls[2].options.redirect, 'error')
  assert.ok(calls.every(call => !call.url.includes('/config') && !call.url.includes('microsoft')))
  await module.cerrarSesion()
  assert.equal(calls.length, 3)
})

test('sesión local no envía bearer fuera del origen ni fuera de /api/', async t => {
  let solicitudes = 0
  const { module } = await cargarCliente(t, async url => { solicitudes++; return respuesta(url.endsWith('/local/login') ? token : identidad) })
  await module.iniciarSesionLocal('analista', 'password-ficticio-para-test')
  for (const url of ['https://externo.example/api/v1/evaluaciones', '/otro', 'http://localhost:8000/api/v1/evaluaciones']) {
    await assert.rejects(module.fetchAutenticado(url), /no pertenece a la API/)
  }
  assert.equal(solicitudes, 2)
})

test('un 401 invalida sesión y solicita autenticación nuevamente', async t => {
  const { module, eventos } = await cargarCliente(t, async url => respuesta(url.endsWith('/local/login') ? token : identidad))
  await module.iniciarSesionLocal('analista', 'password-ficticio-para-test')
  globalThis.fetch = async () => respuesta({ detail: 'Sesión vencida' }, 401)
  await assert.rejects(module.fetchAutenticado('/api/v1/evaluaciones'), /sesión no es válida/)
  assert.equal(eventos.length, 1)
})

test('login rechaza credenciales inválidas y respuestas mal formadas', async t => {
  const { module } = await cargarCliente(t, async () => respuesta({ detail: 'Usuario o contraseña incorrectos.' }, 401))
  await assert.rejects(module.iniciarSesionLocal('analista', 'password-ficticio-para-test'), /incorrectos/)
  globalThis.fetch = async () => respuesta({ access_token: 'demo', token_type: 'bearer', expires_in: '1800' })
  await assert.rejects(module.iniciarSesionLocal('analista', 'password-ficticio-para-test'), /formato esperado/)
})

test('una respuesta 401 antigua no borra un acceso local más reciente', async t => {
  let responderAntigua
  const { module, eventos } = await cargarCliente(t, async url => {
    if (url.endsWith('/evaluaciones')) return new Promise(resolve => { responderAntigua = resolve })
    return respuesta(url.endsWith('/local/login') ? token : identidad)
  })
  await module.iniciarSesionLocal('analista', 'password-ficticio-para-test')
  const antigua = module.fetchAutenticado('/api/v1/evaluaciones')
  const antiguoRechazo = assert.rejects(antigua, /sesión no es válida/)
  await module.iniciarSesionLocal('analista', 'password-ficticio-para-test')
  responderAntigua(respuesta({ detail: 'Antiguo token vencido' }, 401))
  await antiguoRechazo
  assert.equal(eventos.length, 0)
  globalThis.fetch = async (url, options) => {
    assert.equal(options.headers.get('Authorization'), `Bearer ${token.access_token}`)
    return respuesta(identidad)
  }
  assert.equal((await module.fetchAutenticado('/api/v1/auth/me')).status, 200)
})

test('un login antiguo no reemplaza la cuenta de un intento posterior', async t => {
  let responderPrimera
  let solicitudesLogin = 0
  const { module } = await cargarCliente(t, async url => {
    if (url.endsWith('/local/login') && ++solicitudesLogin === 1) return new Promise(resolve => { responderPrimera = resolve })
    return respuesta(url.endsWith('/local/login') ? token : identidad)
  })
  const antiguo = module.iniciarSesionLocal('primero', 'password-ficticio-para-test')
  const rechazo = assert.rejects(antiguo, /reemplazado/)
  assert.deepEqual(await module.iniciarSesionLocal('segundo', 'password-ficticio-para-test'), identidad)
  responderPrimera(respuesta({ ...token, access_token: 'token-antiguo-ficticio' }))
  await rechazo
  globalThis.fetch = async (url, options) => {
    assert.equal(options.headers.get('Authorization'), `Bearer ${token.access_token}`)
    return respuesta(identidad)
  }
  await module.fetchAutenticado('/api/v1/auth/me')
})
