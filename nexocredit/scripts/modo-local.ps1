param([ValidateSet('preparar','local','azure','editar','usuario')][string]$Accion = 'editar')
$ErrorActionPreference = 'Stop'

function Set-NexoPrivateValues([string]$EnvFile, [hashtable]$Values) {
    if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
        throw 'Primero inicia NexoCredit con Docker para crear su configuracion privada.'
    }
    $content = [IO.File]::ReadAllText($EnvFile)
    foreach ($key in $Values.Keys) {
        if ($key -notmatch '^[A-Z][A-Z0-9_]+$' -or $Values[$key] -match '[\r\n]') { throw 'Configuracion no valida.' }
        $pattern = '(?m)^[ \t]*' + [regex]::Escape($key) + '[ \t]*=.*$'
        $line = $key + '=' + $Values[$key]
        if ([regex]::IsMatch($content, $pattern)) {
            $content = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $line })
        } else { $content = $content.TrimEnd() + "`n" + $line + "`n" }
    }
    [IO.File]::WriteAllText($EnvFile, $content, (New-Object System.Text.UTF8Encoding($false)))
}

function Initialize-NexoLocalConfig([string]$EnvFile) {
    if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) { throw 'Falta el archivo privado .env.' }
    $content = [IO.File]::ReadAllText($EnvFile)
    $values = @{ LOCAL_AUTH_ENABLED = 'true' }
    # Preserva un secreto existente; no invalida cuentas/sesiones al repetir.
    if ($content -notmatch '(?m)^[ \t]*LOCAL_AUTH_SECRET[ \t]*=[ \t]*[a-fA-F0-9]{64,}[ \t]*\r?$') {
        if ($content -match '(?m)^[ \t]*LOCAL_AUTH_SECRET[ \t]*=[ \t]*[^\r\n\s]+') {
            throw 'Ya existe un secreto local. No se reemplaza automaticamente: verifica el archivo privado.'
        }
        $bytes = New-Object byte[] 32
        $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
        try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
        $values.LOCAL_AUTH_SECRET = ([BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
    }
    Set-NexoPrivateValues $EnvFile $values
}

function Get-NexoLocalValues([string]$EnvFile) {
    $values = @{
        EXPLICACIONES_PROVEEDOR = 'ollama'; DOCUMENTOS_PROVEEDOR = 'local'; ML_PROVEEDOR = 'local'
        VALORACION_IA_PROVEEDOR = 'ollama'
        OLLAMA_URL = 'http://host.docker.internal:11434'
    }
    # Solo un valor en la misma linea cuenta como modelo configurado.
    if ([IO.File]::ReadAllText($EnvFile) -notmatch '(?m)^[ \t]*OLLAMA_MODEL[ \t]*=[ \t]*[^\r\n\s]+') {
        $values.OLLAMA_MODEL = 'llama3.1:8b'
    }
    return $values
}

$project = Split-Path -Parent $PSScriptRoot
$composeDir = Join-Path $project 'infraestructura\contenedores_docker'
$privateFile = Join-Path $composeDir '.env'
if ($Accion -eq 'editar') {
    if (-not (Test-Path -LiteralPath $privateFile -PathType Leaf)) { throw 'Primero inicia NexoCredit.' }
    # El usuario abre el archivo localmente; nunca se imprime ni envía al navegador.
    Start-Process notepad.exe -ArgumentList ('"' + $privateFile + '"')
    Write-Host 'Configuracion privada abierta. No compartas este archivo ni sus capturas. Guarda y luego actualiza NexoCredit.'
    exit 0
}
if ($Accion -ne 'usuario') {
    Initialize-NexoLocalConfig $privateFile
    if ($Accion -in @('local', 'preparar')) {
        $localValues = Get-NexoLocalValues $privateFile
        Set-NexoPrivateValues $privateFile $localValues
    } elseif ($Accion -eq 'azure') {
        Set-NexoPrivateValues $privateFile @{ EXPLICACIONES_PROVEEDOR = 'azure'; DOCUMENTOS_PROVEEDOR = 'azure'; ML_PROVEEDOR = 'azure' }
    }
    Write-Host 'Configuracion actualizada sin mostrar secretos ni borrar llaves Azure. Microsoft y las cuentas locales se conservan.'
    if ($Accion -eq 'preparar') { exit 0 }
}
$command = Get-Command docker.exe -ErrorAction SilentlyContinue
$dockerExe = if ($command) { $command.Source } else { Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin\docker.exe' }
if (-not (Test-Path -LiteralPath $dockerExe)) { throw 'No se encontro Docker Desktop.' }
$composeArgs = @('compose', '--project-directory', $composeDir, '--env-file', $privateFile, '-f', (Join-Path $composeDir 'docker-compose.yml'))
if ($Accion -eq 'usuario') {
    $usuarioLocal = Read-Host 'Usuario local nuevo (3 a 64 caracteres; letras, numeros, punto, guion o guion bajo)'
    $nombreLocal = Read-Host 'Nombre que aparecera en NexoCredit'
    # Compose identifica el servicio de ESTA instalacion sin depender del nombre del contenedor.
    & $dockerExe @composeArgs exec backend python scripts/crear_usuario_local.py --usuario $usuarioLocal --nombre $nombreLocal
    if ($LASTEXITCODE -ne 0) { throw 'No se creo la cuenta. Revisa el mensaje anterior.' }
} else {
    & $dockerExe @composeArgs up -d --no-build --pull never --wait --wait-timeout 180 backend
    if ($LASTEXITCODE -ne 0) { throw 'Configuracion guardada; no se pudo iniciar el backend. No se borraron datos.' }
    Write-Host 'Modo aplicado. Recarga http://localhost:8080/. Ollama debe estar abierto para generar explicaciones locales.'
}
