$ErrorActionPreference = 'Stop'
$frontend = Join-Path (Split-Path -Parent $PSScriptRoot) 'frontend'
Set-Location $frontend

$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if ($npm) {
    & $npm.Source run dev -- --host 127.0.0.1 --port 5173 --strictPort
    exit $LASTEXITCODE
}

$node = Get-Command node.exe -ErrorAction SilentlyContinue
$nodePath = if ($node) { $node.Source } else { $null }
if (-not $nodePath) {
    # VS Code puede tener un PATH diferente al de la terminal de Codex.
    $codexNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
    if (Test-Path -LiteralPath $codexNode) {
        $nodePath = $codexNode
    }
}
$vite = Join-Path $frontend 'node_modules\vite\bin\vite.js'
if (-not $nodePath) {
    throw 'No se encontro Node.js. Instala Node.js (incluyendo npm) y vuelve a ejecutar este script.'
}
if (-not (Test-Path -LiteralPath $vite)) {
    throw 'Faltan las dependencias del frontend. Instala npm y ejecuta "npm ci" dentro de la carpeta frontend.'
}

& $nodePath $vite --host 127.0.0.1 --port 5173 --strictPort
exit $LASTEXITCODE
