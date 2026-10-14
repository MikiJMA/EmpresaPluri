import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const css = name => readFile(new URL(`../src/styles/${name}`, import.meta.url), 'utf8')

test('los ceros de la aplicación y el acceso no usan IBM Plex Mono ni una variante marcada', async () => {
  const [global, enterprise, access, html] = await Promise.all([
    css('index.css'), css('Enterprise.css'), css('Acceso.css'),
    readFile(new URL('../index.html', import.meta.url), 'utf8'),
  ])
  assert.match(global, /--font-numeric:\s*'Segoe UI', Arial, sans-serif/)
  assert.match(global, /:where\(\.enterprise-app, \.access-screen, \.session-bar\)[\s\S]*font-feature-settings:\s*'zero' 0/)
  for (const content of [global, enterprise, access, html]) {
    assert.doesNotMatch(content, /IBM(?:\+| )Plex(?:\+| )Mono|font-feature-settings:\s*['"]zero['"]\s*1|slashed-zero/)
  }
})

test('las cifras mantienen alineación tabular con una fuente de cero convencional', async () => {
  const enterprise = await css('Enterprise.css')
  for (const selector of ['.enterprise-kpi > strong', '.enterprise-score-heading strong',
                         '.enterprise-secondary-metrics strong', '.enterprise-app .dashboard-metrics strong']) {
    const start = enterprise.indexOf(`${selector} {`)
    assert.ok(start >= 0, `Falta el selector ${selector}`)
    const rule = enterprise.slice(start, enterprise.indexOf('}', start))
    assert.ok(rule.includes('var(--font-numeric)'), `Falta fuente numérica en ${selector}`)
    assert.ok(rule.includes('font-variant-numeric: tabular-nums'), `Falta alineación en ${selector}`)
  }
  assert.match(enterprise, /\.enterprise-app \.history td \{[^}]*font-variant-numeric: tabular-nums/)
  assert.match(enterprise, /\.enterprise-app input, \.enterprise-app select, \.enterprise-app textarea \{[^}]*font-family: var\(--font-numeric\)[^}]*tabular-nums/)
  assert.match(await css('Acceso.css'), /\.access-screen \.access-local-form input \{[^}]*font-family: var\(--font-numeric\)[^}]*tabular-nums/)
})
