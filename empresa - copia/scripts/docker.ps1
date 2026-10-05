param([ValidateSet('iniciar','abrir','detener','estado','logs','pruebas')][string]$Accion = 'iniciar')
$ErrorActionPreference = 'Stop'

function Get-PluriOneWebUrl([string]$Port = '8080') {
    if ($Port -notmatch '^\d+$' -or [int]$Port -lt 1 -or [int]$Port -gt 65535) {
        throw 'WEB_PORT debe ser un puerto valido.'
    }
    return "http://localhost:$Port/"
}

$project = Split-Path -Parent $PSScriptRoot
$composeDir = Join-Path $project 'infraestructura\contenedores_docker'
$envFile = Join-Path $composeDir '.env'
$command = Get-Command docker.exe -ErrorAction SilentlyContinue
$dockerExe = if ($command) { $command.Source } else { $null }
if (-not $dockerExe) {
    foreach ($candidate in @((Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin\docker.exe'), 'C:\Program Files\Docker\Docker\resources\bin\docker.exe')) {
        if (Test-Path -LiteralPath $candidate) { $dockerExe = $candidate; break }
    }
}
if (-not $dockerExe) { throw 'No se encontro Docker Desktop. Instalarlo y abrirlo antes de continuar.' }
& $dockerExe info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker no responde. Abre Docker Desktop y espera a que el motor inicie.' }
if (-not (Test-Path -LiteralPath $envFile)) {
    if ($Accion -ne 'iniciar') { throw 'Primero ejecuta la accion iniciar.' }
    function New-DatabasePassword {
        $bytes = New-Object byte[] 32
        $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
        return ([BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
    }
    $content = 'POSTGRES_ADMIN_PASSWORD=' + (New-DatabasePassword) + "`nPOSTGRES_APP_PASSWORD=" + (New-DatabasePassword) + "`nWEB_PORT=8080`n"
    $stream = [System.IO.File]::Open($envFile, [System.IO.FileMode]::CreateNew)
    $writer = New-Object System.IO.StreamWriter($stream, (New-Object System.Text.UTF8Encoding($false)))
    try { $writer.Write($content) } finally { $writer.Dispose() }
    Write-Host 'Configuracion privada creada. Conserva el archivo .env junto con el volumen de datos.'
}
$composeArgs = @('compose', '--project-directory', $composeDir, '--env-file', $envFile, '-f', (Join-Path $composeDir 'docker-compose.yml'))
switch ($Accion) {
    'abrir' { & $dockerExe @composeArgs up -d --no-build --pull never --wait --wait-timeout 180 }
    'iniciar' { & $dockerExe @composeArgs up -d --build --wait --wait-timeout 180 }
    'detener' { & $dockerExe @composeArgs down }
    'estado' { & $dockerExe @composeArgs ps -a }
    'logs' { & $dockerExe @composeArgs logs --tail 100 }
    'pruebas' { & (Join-Path $PSScriptRoot 'probar-programacion.ps1') }
}
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose no completo la accion. Consulta los mensajes anteriores.' }
if ($Accion -eq 'iniciar') { Write-Host 'Proyecto iniciado. Acceso Microsoft: http://localhost:8080/ (WEB_PORT en .env).' }
if ($Accion -eq 'abrir') {
    $webPort = '8080'
    foreach ($line in Get-Content -LiteralPath $envFile) {
        if ($line -match '^\s*WEB_PORT\s*=\s*(\d+)\s*$') { $webPort = $Matches[1] }
    }
    if ($env:WEB_PORT) { $webPort = $env:WEB_PORT }
    $url = Get-PluriOneWebUrl $webPort
    if ($webPort -ne '8080') { Write-Warning 'El retorno Entra actual requiere localhost:8080. Otro puerto necesita configuracion de acceso acorde.' }
    $null = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
    Write-Host "Pagina disponible: $url"
    Start-Process $url
}
