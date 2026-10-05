param([switch]$SinConstruir)
$ErrorActionPreference = 'Stop'
# Nunca monta configuracion privada ni utiliza la base de trabajo como destino.
$project = Split-Path -Parent $PSScriptRoot
$dockerTestExe = (Get-Command docker.exe -ErrorAction SilentlyContinue).Source
if (-not $dockerTestExe) {
    foreach ($candidate in @("$env:LOCALAPPDATA/Programs/DockerDesktop/resources/bin/docker.exe", 'C:/Program Files/Docker/Docker/resources/bin/docker.exe')) {
        if (Test-Path -LiteralPath $candidate) { $dockerTestExe = $candidate; break }
    }
}

function Get-PostgresTestPlan([string]$Marker, [string]$Image) {
    if ($Marker -notmatch '^[a-f0-9]{32}$' -or $Image -notmatch '^sha256:[a-f0-9]{64}$') {
        throw 'Identidad temporal o imagen de PostgreSQL no valida.'
    }
    return @('run', '--detach', '--pull=never', '--name', "plurione-suite-$Marker",
        '--label', "io.plurione.suite-test=$Marker", '--network', 'none',
        '--memory', '512m', '--cpus', '1', '--security-opt', 'no-new-privileges',
        '--tmpfs', '/var/lib/postgresql/data:rw,nosuid,noexec,size=268435456',
        '--env', 'POSTGRES_USER=ci', '--env', 'POSTGRES_DB=pluri_test',
        '--env', 'POSTGRES_HOST_AUTH_METHOD=trust', $Image)
}

function Remove-PostgresTestContainer([string]$DockerExe, [string]$Container, [string]$Marker) {
    if ($Container -notmatch '^[a-f0-9]{64}$' -or $Marker -notmatch '^[a-f0-9]{32}$') {
        throw 'No se eliminara un contenedor sin identidad temporal valida.'
    }
    # JSON evita que Windows PowerShell 5 quite las comillas de plantillas Go.
    $labelsJson = & $DockerExe inspect --format '{{json .Config.Labels}}' $Container
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo comprobar la identidad del temporal; no se eliminara.' }
    $labels = $labelsJson | ConvertFrom-Json
    if ($labels.'io.plurione.suite-test' -ne $Marker) {
        throw 'El contenedor no pertenece a esta prueba; no se eliminara.'
    }
    & $DockerExe rm --force --volumes $Container
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo retirar el contenedor temporal identificado.' }
}

if (-not $dockerTestExe) { throw 'No se encontro Docker Desktop.' }
& $dockerTestExe info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker no esta disponible. No se reiniciara la aplicacion.' }
$postgresImage = & $dockerTestExe image inspect postgres:17-alpine --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw 'Falta la imagen local de PostgreSQL 17. Inicia primero la aplicacion.' }
if (-not $SinConstruir) {
    & $dockerTestExe build --pull=false --tag plurione-verificacion-backend:local --file (Join-Path $project 'infraestructura/contenedores_docker/backend.Dockerfile') $project
    if ($LASTEXITCODE -ne 0) { throw 'Fallo la construccion backend de verificacion.' }
    & $dockerTestExe build --pull=false --target build --tag plurione-verificacion-frontend-build:local --file (Join-Path $project 'infraestructura/contenedores_docker/frontend.Dockerfile') $project
    if ($LASTEXITCODE -ne 0) { throw 'Fallo test, lint o build frontend.' }
} else {
    Write-Warning 'SinConstruir reutiliza imagenes de verificacion: no acredita cambios de codigo posteriores.'
}
# Solo consulta dependencias publicas al registro npm; no envia escenarios ni secretos.
& $dockerTestExe run --rm --pull=never plurione-verificacion-frontend-build:local npm audit --audit-level=high
if ($LASTEXITCODE -ne 0) { throw 'Auditoria npm no completada o dependencias altas/criticas detectadas.' }

$marker = [guid]::NewGuid().ToString('N')
$testContainer = $null
try {
    $plan = Get-PostgresTestPlan $marker "$postgresImage".Trim()
    $created = & $dockerTestExe @plan
    if ($LASTEXITCODE -ne 0 -or $created -notmatch '^[a-f0-9]{64}$') { throw 'No se pudo identificar PostgreSQL temporal.' }
    $testContainer = "$created".Trim()
    $network = & $dockerTestExe inspect --format '{{.HostConfig.NetworkMode}}' $testContainer
    if ($LASTEXITCODE -ne 0 -or $network -ne 'none') { throw 'El temporal no tiene la red aislada esperada.' }
    $ports = & $dockerTestExe inspect --format '{{json .HostConfig.PortBindings}}' $testContainer
    if ($LASTEXITCODE -ne 0 -or $ports -notin @('{}', 'null')) { throw 'El temporal no debe publicar puertos.' }
    $binds = & $dockerTestExe inspect --format '{{json .HostConfig.Binds}}' $testContainer
    if ($LASTEXITCODE -ne 0 -or $binds -notin @('[]', 'null')) { throw 'El temporal no debe montar carpetas del usuario.' }
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        & $dockerTestExe exec $testContainer pg_isready -U ci -d pluri_test 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ready) { throw 'PostgreSQL temporal no pudo iniciar.' }
    # Los dos contenedores comparten unicamente la red sin salida del temporal.
    $commands = 'python -m backend.app.persistencia_postgresql.migrar && python -m backend.app.persistencia_postgresql.migrar && python -m unittest discover -s backend/tests -v'
    & $dockerTestExe run --rm --pull=never --network "container:$testContainer" --read-only --tmpfs '/tmp:rw,nosuid,noexec,size=67108864' --security-opt no-new-privileges --env DATABASE_URL=postgresql://ci@127.0.0.1:5432/pluri_test --env RUN_POSTGRES_TESTS=1 plurione-verificacion-backend:local sh -c $commands
    if ($LASTEXITCODE -ne 0) { throw 'Fallo una migracion o prueba backend en la base temporal.' }
} finally {
    if ($testContainer) { Remove-PostgresTestContainer $dockerTestExe $testContainer $marker }
}
foreach ($test in @('docker-url.test.ps1', 'banxico-config.test.ps1', 'programacion-aislada.test.ps1')) {
    & (Join-Path $PSScriptRoot "tests/$test")
}
Write-Host 'Verificacion local aprobada. Base temporal retirada; base de trabajo intacta. No se ejecuto CI remota.'
