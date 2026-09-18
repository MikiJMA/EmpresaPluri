param([ValidateSet('preparar','iniciar','detener','estado')][string]$Accion = 'iniciar')
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
& (Join-Path $project '.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'postgresql_local.py') $Accion
exit $LASTEXITCODE
