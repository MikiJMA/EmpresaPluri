import { readFile, readdir } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

// Usa Ajv ya instalado por ESLint, sin instalar dependencias ni modificar reportes.
const require = createRequire(new URL('../../frontend/package.json', import.meta.url))
const Ajv = require('ajv')
const root = new URL('./', import.meta.url)
const report = new URL('PluriOne_Riesgo_Crediticio.pbix.Report/definition/', root)
const official = 'https://developer.microsoft.com/json-schemas/fabric/'
const schemas = new Map()
async function schema(uri) {
  const url = new URL(uri)
  url.hash = ''
  if (!url.href.startsWith(official)) throw new Error('Referencia de esquema fuera del dominio oficial permitido.')
  if (!schemas.has(url.href)) schemas.set(url.href, (async () => {
    const response = await fetch(url, { signal: AbortSignal.timeout(20000), redirect: 'error' })
    if (!response.ok) throw new Error(`Microsoft devolvió HTTP ${response.status} al consultar un esquema.`)
    return response.json()
  })())
  return schemas.get(url.href)
}
async function files(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  const result = []
  for (const entry of entries) {
    const path = new URL(entry.name + (entry.isDirectory() ? '/' : ''), dir)
    if (entry.isDirectory()) result.push(...await files(path))
    else if (entry.name.endsWith('.json')) result.push(path)
  }
  return result
}
const ajv = new Ajv({ allErrors: true, loadSchema: schema, logger: false, unknownFormats: 'ignore' })
const validators = new Map()
let total = 0
const failed = []
for (const file of await files(report)) {
  const data = JSON.parse(await readFile(file, 'utf8'))
  const label = fileURLToPath(file).slice(fileURLToPath(root).length)
  if (typeof data.$schema !== 'string') throw new Error(`Falta $schema: ${label}`)
  if (!validators.has(data.$schema)) validators.set(data.$schema, await ajv.compileAsync(await schema(data.$schema)))
  const validate = validators.get(data.$schema)
  if (!validate(data)) failed.push({ file: label, errors: validate.errors })
  total++
}

const tmdl = await readFile(new URL('PluriOne_Riesgo_Crediticio.pbix.SemanticModel/definition/tables/Consulta1.tmdl', root), 'utf8')
const columns = new Set([...tmdl.matchAll(/^\tcolumn ([^\r\n]+)/gm)].map(match => match[1]))
const measures = new Set([...tmdl.matchAll(/^\tmeasure '([^']+)'/gm)].map(match => match[1]))
const prohibited = new Set(['rfc', 'responsable', 'observaciones', 'solicitud', 'resultado'])
if ([...columns].some(name => prohibited.has(name.toLowerCase()))) throw new Error('El modelo incluye campos no permitidos en el reporte.')
const pageDir = new URL('pages/plurione_dashboard/', report)
const page = JSON.parse(await readFile(new URL('page.json', pageDir), 'utf8'))
let visuals = 0
function references(value) {
  if (!value || typeof value !== 'object') return
  for (const kind of ['Column', 'Measure']) {
    if (value[kind]?.Expression?.SourceRef?.Entity === 'Consulta1' && !(kind === 'Column' ? columns : measures).has(value[kind].Property)) {
      throw new Error(`Referencia inexistente: ${kind} ${value[kind].Property}`)
    }
  }
  for (const child of Object.values(value)) references(child)
}
for (const file of await files(new URL('visuals/', pageDir))) {
  const visual = JSON.parse(await readFile(file, 'utf8'))
  if (!visual.position) continue
  const p = visual.position
  if (p.x < 0 || p.y < 0 || p.x + p.width > page.width || p.y + p.height > page.height) throw new Error(`Visual fuera de la página: ${visual.name}`)
  references(visual)
  visuals++
}
if (failed.length) {
  process.stderr.write(JSON.stringify({ total, failed }, null, 2) + '\n')
  process.exitCode = 1
} else process.stdout.write(JSON.stringify({ archivos_validados: total, visuales_dashboard: visuals, medidas: measures.size,
  esquemas_oficiales: schemas.size, estado: 'Esquemas y referencias correctos; renderizado y ejecución DAX no comprobados por esta herramienta.' }, null, 2) + '\n')
