$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$gitRoot = Split-Path -Parent $projectRoot
$launchers = @(
    @{ Path = 'operacion/aplicacion/Abrir NexoCredit.cmd'; Script = 'docker.ps1'; Action = 'abrir' },
    @{ Path = 'operacion/aplicacion/Actualizar NexoCredit.cmd'; Script = 'docker.ps1'; Action = 'iniciar' },
    @{ Path = 'operacion/aplicacion/Detener NexoCredit.cmd'; Script = 'docker.ps1'; Action = 'detener' },
    @{ Path = 'operacion/aplicacion/Crear usuario local.cmd'; Script = 'modo-local.ps1'; Action = 'usuario' },
    @{ Path = 'operacion/integraciones/Editar configuracion privada.cmd'; Script = 'modo-local.ps1'; Action = 'editar' },
    @{ Path = 'operacion/integraciones/Activar modo local.cmd'; Script = 'modo-local.ps1'; Action = 'local' },
    @{ Path = 'operacion/integraciones/Activar modo Azure.cmd'; Script = 'modo-local.ps1'; Action = 'azure' },
    @{ Path = 'operacion/integraciones/Cargar documentos Azure AI Search.cmd'; Script = 'cargar_documentos_search.py' },
    @{ Path = 'operacion/integraciones/Conectar Azure AI Search.cmd'; Script = 'configurar-azure-search.ps1' },
    @{ Path = 'operacion/integraciones/Conectar Azure ML.cmd'; Script = 'configurar-azure-ml.ps1' },
    @{ Path = 'operacion/integraciones/Conectar Azure OpenAI.cmd'; Script = 'configurar-azure-openai.ps1' },
    @{ Path = 'operacion/integraciones/Conectar Banxico.cmd'; Script = 'configurar-banxico.ps1' },
    @{ Path = 'operacion/pruebas/Probar programacion.cmd'; Script = 'probar-programacion.ps1' },
    @{ Path = 'operacion/respaldos/Respaldar PostgreSQL.cmd'; Script = 'respaldo-postgresql.ps1'; Action = 'crear' },
    @{ Path = 'operacion/respaldos/Probar restauracion PostgreSQL.cmd'; Script = 'respaldo-postgresql.ps1'; Action = 'probar' }
)
foreach ($launcher in $launchers) {
    $path = Join-Path $projectRoot $launcher.Path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Falta el lanzador $($launcher.Path)." }
    $content = Get-Content -LiteralPath $path -Raw
    if (-not $content.Contains('cd /d "%~dp0..\.."') -or -not $content.Contains('if errorlevel 1 exit /b 1')) {
        throw "El lanzador no comprueba su raiz: $($launcher.Path)."
    }
    $resolvedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $path) '../..'))
    if ($resolvedRoot -ne $projectRoot) { throw 'La carpeta operativa no resuelve la raiz del proyecto.' }
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot "scripts/$($launcher.Script)") -PathType Leaf)) {
        throw "No existe la implementacion de $($launcher.Path)."
    }
    if (-not $content.Contains('scripts\' + $launcher.Script + '"')) { throw 'Destino de script incorrecto.' }
    if ($launcher.Action -and $content -notmatch ([regex]::Escape($launcher.Script) + '"\s+(?:-Accion\s+)?' + $launcher.Action + '(?:\s|$)')) {
        throw "Accion incorrecta en $($launcher.Path)."
    }
    $oldPath = Join-Path $projectRoot (Split-Path -Leaf $path)
    if (Test-Path -LiteralPath $oldPath) { throw 'Se conservo una copia operativa duplicada en la raiz.' }
}
$actualLaunchers = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'operacion') -Recurse -Filter '*.cmd' -File)
if ($actualLaunchers.Count -ne $launchers.Count) { throw 'El indice de lanzadores no coincide con los archivos.' }

foreach ($doc in @('docs/README.md', 'docs/producto/PRD_NEXOCREDIT.md', 'docs/producto/MVP_NEXOCREDIT.md',
    'docs/archivo/PRD_MVP_NEXOCREDIT.md', 'docs/planificacion/PLAN_PROYECTO.md',
    'docs/manuales/OPERACION.md', 'docs/calidad/QA.md', 'docs/entrega/ENTREGA_DEMO.md',
    'docs/desarrollo/GITHUB_ACTIONS.md')) {
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot $doc) -PathType Leaf)) { throw "Falta $doc." }
}
if (Test-Path -LiteralPath (Join-Path $projectRoot '.github/workflows/README.md')) {
    throw 'La documentacion CI no debe confundirse con otro workflow.'
}
if (-not (Test-Path -LiteralPath (Join-Path $gitRoot '.github/workflows/ci.yml') -PathType Leaf)) {
    throw 'Falta el workflow de la raiz Git.'
}
$workspace = Get-Content -LiteralPath (Join-Path $gitRoot 'NexoCredit.code-workspace') -Raw | ConvertFrom-Json
if ($workspace.folders.Count -ne 2 -or $workspace.folders[0].path -ne 'empresa - copia' -or $workspace.folders[1].path -ne '.github') {
    throw 'El workspace debe apuntar a la aplicacion y al CI originales.'
}
$outerSettings = Get-Content -LiteralPath (Join-Path $gitRoot '.vscode/settings.json') -Raw | ConvertFrom-Json
if ($outerSettings.'python.defaultInterpreterPath' -ne '${workspaceFolder}/empresa - copia/.venv/Scripts/python.exe') {
    throw 'El interprete exterior apunta a una carpeta equivocada.'
}
foreach ($settings in @($workspace.settings, $outerSettings,
    (Get-Content -LiteralPath (Join-Path $projectRoot '.vscode/settings.json') -Raw | ConvertFrom-Json))) {
    foreach ($hidden in @('**/.venv', '**/.venv-roto', '**/.local', '**/.tmp', '**/node_modules', '**/dist')) {
        if (-not $settings.'files.exclude'.$hidden) { throw "La vista no oculta $hidden." }
    }
}
Write-Host 'Correcto: 15 lanzadores, rutas de documentos, CI unico y workspace. Sin ejecutar comandos, leer secretos o modificar datos.'
