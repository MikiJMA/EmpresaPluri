import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { crearRevisionIdentidad, SAT_CURP_URL } from '../src/evaluacion_crediticia/servicios/identidad.mjs'
import { cargarComponente } from './helpers/cargar-componente.mjs'

const Panel = (await cargarComponente(new URL('../src/evaluacion_crediticia/componentes/PanelIdentidad.jsx', import.meta.url))).default
const data = () => ({ estado: 'coherencia_basica', mensaje: 'Formato compatible; no certifica identidad.', verificacion_oficial: false, fuente_url: SAT_CURP_URL,
  comprobaciones: [{ campo: 'Fecha', correcto: true, detalle: 'La fecha coincide.' }] })

test('CURP opcional y consulta SAT sin identificadores en el enlace ni una identidad oficial inventada', () => {
  const html = renderToStaticMarkup(createElement(Panel, { curp: '', busy: false, change() {}, revisar() {}, data: data() }))
  assert.match(html, /CURP para comparar/)
  assert.match(html, /Comprobación básica · No oficial/)
  assert.match(html, /no se guarda ni se envía a la IA/)
  assert.ok(html.includes(`href="${SAT_CURP_URL}"`))
  assert.match(html, /rel="noopener noreferrer"/)
  assert.doesNotMatch(html, /required=""|SAT verificado|Identidad confirmada/)
})

test('revisión separada envía solo RFC y CURP a API propia y no los conserva en el resultado', async () => {
  const calls = []
  const servicio = crearRevisionIdentidad(async (url, options) => { calls.push({ url, options }); return { ok: true, json: async () => data() } }, 'http://localhost:8080/')
  const respuesta = await servicio('AACD900101A01', 'AACD900101HDFBCD01', new AbortController().signal)
  assert.equal(calls[0].url, 'http://localhost:8080/api/v1/identidad/revisar')
  assert.deepEqual(JSON.parse(calls[0].options.body), { rfc: 'AACD900101A01', curp: 'AACD900101HDFBCD01' })
  assert.equal(respuesta.verificacion_oficial, false)
  assert.ok(!JSON.stringify(respuesta).includes('AACD900101'))
})

test('se rechaza verificación oficial inventada o enlace ajeno y no se reflejan errores externos', async () => {
  for (const changes of [{ verificacion_oficial: true }, { fuente_url: 'https://otro.test/' }, { estado: 'verificado' }, { comprobaciones: [null] }, { comprobaciones: [] }]) {
    const servicio = crearRevisionIdentidad(async () => ({ ok: true, json: async () => ({ ...data(), ...changes }) }), '')
    await assert.rejects(servicio('ficticio', ''), /formato esperado/)
  }
  const servicio = crearRevisionIdentidad(async () => ({ ok: false, json: async () => ({ detail: 'datos privados' }) }), '')
  await assert.rejects(servicio('ficticio', ''), /No se pudo revisar/)
})

test('CURP vive fuera del formulario evaluado y una revisión de otros valores no se muestra', async () => {
  const source = await readFile(new URL('../src/evaluacion_crediticia/componentes/RevisarIdentidad.jsx', import.meta.url), 'utf8')
  assert.ok(source.includes("const [curp, setCurp] = useState('')"))
  assert.ok(source.includes('consulta?.rfc === rfc && consulta?.curp === curp'))
  assert.ok(source.includes('solicitud.signal.aborted'))
  const app = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8')
  assert.ok(app.includes('identidad={<RevisarIdentidad rfc={form.rfc} bloqueado={busy} />}'))
  assert.ok(!app.includes('curp:'))
})
