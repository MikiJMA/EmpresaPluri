$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'No se encontro el entorno .venv. Sigue los pasos de instalacion indicados en README.md.'
}

if (Test-Path -LiteralPath '.\.local\postgresql\datos\PG_VERSION') {
    & $python .\scripts\postgresql_local.py iniciar
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar PostgreSQL.' }
}
& $python -m uvicorn backend.app.main:app --reload --reload-dir backend/app --host 127.0.0.1 --port 8000
