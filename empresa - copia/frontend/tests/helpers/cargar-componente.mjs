import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { transformWithOxc } from 'vite'

// Renderizado aislado de componentes de presentación; no inicia MSAL ni llama APIs.
const modules = new Map()
export async function cargarComponente(source) {
  if (!modules.has(source.href)) modules.set(source.href, compilar(source))
  return import(await modules.get(source.href))
}

async function compilar(source) {
  const { code } = await transformWithOxc(await readFile(source, 'utf8'), fileURLToPath(source), { jsx: { runtime: 'classic' } })
  let compiled = code
  for (const match of [...code.matchAll(/from\s+(['"])([^'"]+)\1/g)]) {
    const specifier = match[2]
    let target
    if (specifier.startsWith('.')) {
      const relative = /\.(jsx|mjs|js)$/.test(specifier) ? specifier : `${specifier}.jsx`
      const resolved = new URL(relative, source)
      target = relative.endsWith('.jsx') ? await compilar(resolved) : resolved.href
    } else target = import.meta.resolve(specifier)
    compiled = compiled.replace(match[0], `from ${JSON.stringify(target)}`)
  }
  compiled = `import React from ${JSON.stringify(import.meta.resolve('react'))};\n${compiled}`
  return `data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`
}
