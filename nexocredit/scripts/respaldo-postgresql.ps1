param([ValidateSet('crear','probar')][string]$Accion = 'probar', [string]$Respaldo)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $project '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Falta el entorno Python del proyecto. No se instalaran dependencias automaticamente.' }
$arguments = @((Join-Path $PSScriptRoot 'respaldo_postgresql.py'), $Accion)
if ($Respaldo) { $arguments += @('--respaldo', $Respaldo) }
& $pythonExe @arguments
if ($LASTEXITCODE -ne 0) { throw 'Respaldo/prueba no completados. La base principal no se uso como destino.' }
