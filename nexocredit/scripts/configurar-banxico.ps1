param([switch]$SoloValidar, [switch]$UsarTokenGuardado)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$composeDir = Join-Path $project 'infraestructura\contenedores_docker'
$envFile = Join-Path $composeDir '.env'

function Merge-BanxicoConfiguration([string]$Existing, [string]$Key) {
    if ($Key -cnotmatch '^[A-Za-z0-9]{64}$') { throw 'El token debe contener 64 caracteres alfanumericos.' }
    $lines = @($Existing -split '\r?\n' | Where-Object {
        $_ -notmatch '^\s*(?:export\s+)?BANXICO_API_TOKEN\s*='
    })
    return (($lines -join "`r`n").TrimEnd("`r", "`n") + "`r`nBANXICO_API_TOKEN=$Key`r`n")
}

function Get-BanxicoStartupPlan {
    # La salud del backend incluye PostgreSQL: no recrear la API antes de encender la base.
    # No reconstruye/descarga imagenes, no recrea PostgreSQL ni toca su volumen.
    [pscustomobject]@{
        Arguments = @('up', '-d', '--no-build', '--pull', 'never', '--no-recreate', '--wait', '--wait-timeout', '90', 'postgres')
        Message = 'Encendiendo PostgreSQL y esperando su comprobacion de salud (datos conservados)...'
        Failure = 'Token conservado. PostgreSQL no pudo iniciar. Comprueba Docker Desktop; no borres el volumen de datos.'
    }
    [pscustomobject]@{
        Arguments = @('up', '-d', '--no-build', '--pull', 'never', '--no-deps', '--force-recreate', '--wait', '--wait-timeout', '90', 'backend')
        Message = 'Aplicando la configuracion guardada y esperando la salud del backend...'
        Failure = 'Token conservado. PostgreSQL inicio, pero el backend no paso su comprobacion de salud.'
    }
}

function Invoke-BanxicoStartup([string]$DockerPath, [string[]]$ComposeArguments) {
    foreach ($step in Get-BanxicoStartupPlan) {
        Write-Host $step.Message
        $stepArguments = $step.Arguments
        try {
            # No mostrar errores brutos de Compose que pudieran contener configuracion privada.
            # PowerShell 5.1 interpreta los mensajes normales de Docker en stderr como errores.
            # Capturarlos sin detener el comando; decidir el resultado por su codigo de salida.
            $previousPreference = $ErrorActionPreference
            try {
                $ErrorActionPreference = 'Continue'
                & $DockerPath @ComposeArguments @stepArguments 2>&1 | Out-Null
                $stepExitCode = $LASTEXITCODE
            } finally { $ErrorActionPreference = $previousPreference }
            if ($stepExitCode -ne 0) { throw 'Docker no completo el paso.' }
        } catch { throw $step.Failure }
    }
}

if ($SoloValidar -and $UsarTokenGuardado) { throw 'Usa solo una de las opciones de validacion o arranque.' }
if ($SoloValidar) {
    $sample = "POSTGRES_APP_PASSWORD=conservar`nAZURE_OPENAI_API_KEY=conservar`nWEB_PORT=8080`nBANXICO_API_TOKEN=anterior`nexport BANXICO_API_TOKEN=duplicada"
    $fake = 'a' * 64
    $merged = Merge-BanxicoConfiguration $sample $fake
    if (-not $merged.Contains('POSTGRES_APP_PASSWORD=conservar') -or
        -not $merged.Contains('AZURE_OPENAI_API_KEY=conservar') -or
        -not $merged.Contains('WEB_PORT=8080') -or
        ([regex]::Matches($merged, '(?m)^BANXICO_API_TOKEN=')).Count -ne 1 -or
        (Merge-BanxicoConfiguration $merged $fake) -ne $merged) { throw 'Fallo de preservacion o repeticion.' }
    foreach ($invalid in @('', ('a' * 63), ('a' * 65), ('a' * 63 + '$'), ("a`n" + 'a' * 62), (' ' + 'a' * 63))) {
        $rejected = $false
        try { $null = Merge-BanxicoConfiguration $sample $invalid } catch { $rejected = $true }
        if (-not $rejected) { throw 'Una entrada invalida fue aceptada.' }
    }
    $plan = @(Get-BanxicoStartupPlan)
    if ($plan.Count -ne 2 -or $plan[0].Arguments[-1] -ne 'postgres' -or $plan[1].Arguments[-1] -ne 'backend' -or
        $plan[0].Arguments -notcontains '--no-recreate' -or $plan[0].Arguments -contains '--no-deps' -or
        $plan[1].Arguments -notcontains '--force-recreate' -or $plan[1].Arguments -notcontains '--no-deps') {
        throw 'Fallo del orden de arranque o de la proteccion de PostgreSQL.'
    }
    foreach ($step in $plan) {
        if ($step.Arguments -notcontains '--wait' -or $step.Arguments -notcontains '--no-build' -or
            $step.Arguments -contains '--build' -or $step.Arguments -contains 'down' -or
            $step.Arguments -contains '--volumes' -or $step.Arguments -notcontains 'never') {
            throw 'El arranque debe esperar salud y conservar imagenes y volumenes.'
        }
    }
    Write-Host 'Pruebas correctas: preservacion, duplicados, repeticion, entradas invalidas y orden de arranque.'
    Write-Host 'No se leyeron secretos ni se modificaron archivos, Docker o proveedores.'
    exit 0
}

if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) { throw 'Inicia primero la aplicacion Docker local.' }
if ($UsarTokenGuardado) {
    Write-Host 'Se aplicara la configuracion privada existente sin pedir ni modificar el token.'
} else {
Write-Host 'Obtiene tu token en el sitio oficial del SIE API de Banxico (opcion Obtener token).'
Write-Host 'https://www.banxico.org.mx/SieAPIRest/service/v1/'
Write-Host 'No compartas el token en el chat ni lo pegues en el navegador de PluriOne.'
Write-Host 'Se guardara sin cifrado en el .env privado de Docker, excluido de Git.'
Write-Host 'Los administradores locales pueden leerlo. Se encendera PostgreSQL si esta detenido; SOLO se recreara el backend.'
$secureKey = Read-Host 'Pega el token y pulsa Enter (entrada oculta; Ctrl+C cancela)' -AsSecureString
$keyPointer = [IntPtr]::Zero
try {
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer).Trim()
    $existing = [IO.File]::ReadAllText($envFile)
    $updated = Merge-BanxicoConfiguration $existing $plainKey
    [IO.File]::WriteAllText($envFile, $updated, (New-Object Text.UTF8Encoding($false)))
} catch {
    Write-Host 'No se pudo guardar. Revisa el formato del token y los permisos del archivo.'
    exit 1
} finally {
    if ($keyPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
    $plainKey = $null; $existing = $null; $updated = $null
    if ($secureKey) { $secureKey.Dispose() }
}
}
$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
$dockerPath = if ($dockerCommand) { $dockerCommand.Source } else { $null }
if (-not $dockerPath) {
    foreach ($candidate in @((Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin\docker.exe'), 'C:\Program Files\Docker\Docker\resources\bin\docker.exe')) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $dockerPath = $candidate; break }
    }
}
if (-not $dockerPath -or -not (Test-Path -LiteralPath $dockerPath -PathType Leaf)) {
    Write-Host 'Token guardado. Falta Docker: abre Docker Desktop y reinicia el backend para aplicarlo.'
    exit 1
}
$composeArguments = @('compose', '--project-name', 'plurione-docker', '--project-directory', $composeDir, '--env-file', $envFile, '-f', (Join-Path $composeDir 'docker-compose.yml'))
try {
    Invoke-BanxicoStartup $dockerPath $composeArguments
} catch {
    Write-Host $_.Exception.Message
    exit 1
}
Write-Host 'Backend reiniciado. Recarga PluriOne y abre Indicadores financieros para comprobar Banxico.'
Write-Host 'Guardar el token no acredita que Banxico lo acepte: la pantalla mostrara el resultado real.'
