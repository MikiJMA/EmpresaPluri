param([switch]$SoloValidar)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$composeDir = Join-Path $project 'infraestructura\contenedores_docker'
$envFile = Join-Path $composeDir '.env'
$endpoint = 'https://ml-plurione-riesgo-swgbr.eastus.inference.ml.azure.com/score'
$model = 'plurione-uci-voting-candidato:1'

function Merge-AzureConfiguration([string]$Existing, [string]$Key) {
    # Acepta caracteres de claves base64/base64url, sin interpolacion de dotenv.
    if ($Key -notmatch '^[A-Za-z0-9_+/=-]{16,512}$') {
        throw 'La clave no tiene el formato esperado. Copiala de Azure, sin comillas.'
    }
    $lines = @($Existing -split '\r?\n' | Where-Object {
        $_ -notmatch '^\s*(?:export\s+)?AZURE_ML_(SCORING_URI|API_KEY|MODEL_ID)\s*='
    })
    return (($lines -join "`r`n").TrimEnd("`r", "`n") + "`r`nAZURE_ML_SCORING_URI=$endpoint`r`nAZURE_ML_API_KEY=$Key`r`nAZURE_ML_MODEL_ID=$model`r`n")
}

if ($SoloValidar) {
    $sample = "POSTGRES_ADMIN_PASSWORD=conservar`nPOSTGRES_APP_PASSWORD=conservar2`nWEB_PORT=8080`nAZURE_ML_API_KEY=anterior"
    $merged = Merge-AzureConfiguration $sample 'claveFicticiaDePrueba123=='
    if (-not $merged.Contains('POSTGRES_APP_PASSWORD=conservar2') -or
        -not $merged.Contains('POSTGRES_ADMIN_PASSWORD=conservar') -or
        ([regex]::Matches($merged, '(?m)^AZURE_ML_API_KEY=')).Count -ne 1 -or
        (Merge-AzureConfiguration $merged 'claveFicticiaDePrueba123==') -ne $merged) {
        throw 'Fallo en la comprobacion de conservacion de configuracion.'
    }
    Write-Host 'Validacion correcta. No se leyeron ni modificaron secretos ni contenedores.'
    exit 0
}

if (-not (Test-Path -LiteralPath $envFile)) { throw 'Falta la configuracion de Docker. Inicia primero la aplicacion local.' }
$dockerExe = (Get-Command docker.exe -ErrorAction SilentlyContinue).Source
if (-not $dockerExe) {
    foreach ($candidate in @("$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe", 'C:\Program Files\Docker\Docker\resources\bin\docker.exe')) {
        if (Test-Path -LiteralPath $candidate) { $dockerExe = $candidate; break }
    }
}
if (-not $dockerExe) { throw 'No se encontro Docker Desktop.' }
& $dockerExe info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Abre Docker Desktop antes de continuar.' }
Write-Host "Conectar PluriOne a: $endpoint"
Write-Host 'La clave se guardara en el .env local de Docker, fuera de Git, sin cifrado en disco.'
Write-Host 'No compartas ese archivo. Administradores locales y Docker pueden acceder a el.'
Write-Host 'Se conserva PostgreSQL. Solo se recrea el backend y se reinicia la interfaz.'
$secureKey = Read-Host 'Pega la clave principal de Azure y pulsa Enter (entrada oculta; Ctrl+C cancela)' -AsSecureString
$keyPointer = [IntPtr]::Zero
try {
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer).Trim()
    $existing = [IO.File]::ReadAllText($envFile)
    $updated = Merge-AzureConfiguration $existing $plainKey
    # .env ya existe: se conserva su ACL y todas las variables ajenas a Azure ML.
    [IO.File]::WriteAllText($envFile, $updated, (New-Object Text.UTF8Encoding($false)))
} finally {
    if ($keyPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
    $plainKey = $null; $existing = $null; $updated = $null
    if ($secureKey) { $secureKey.Dispose() }
}
# El archivo privado es la unica fuente para estas variables, no valores heredados.
Remove-Item Env:AZURE_ML_SCORING_URI,Env:AZURE_ML_API_KEY,Env:AZURE_ML_MODEL_ID -ErrorAction SilentlyContinue
$composeArgs = @('compose', '--project-directory', $composeDir, '--env-file', $envFile, '-f', (Join-Path $composeDir 'docker-compose.yml'))
& $dockerExe @composeArgs up -d --no-build --no-deps --wait --wait-timeout 180 backend
if ($LASTEXITCODE -ne 0) { throw 'Configuracion guardada, pero fallo la actualizacion del backend. No compartas el archivo .env.' }
& $dockerExe @composeArgs restart frontend
if ($LASTEXITCODE -ne 0) { throw 'Backend actualizado; falta reiniciar la interfaz.' }
& $dockerExe @composeArgs exec -T backend python -c 'from backend.app.integraciones.prediccion_azure_ml.cliente_ml import configuracion; import sys; sys.exit(0 if configuracion()[3] else 1)'
if ($LASTEXITCODE -ne 0) { throw 'El backend no reconoce la configuracion.' }
Write-Host 'Configuracion local lista. Todavia falta probar una prediccion real desde PluriOne.'
Write-Host 'Recarga la aplicacion y abre Laboratorio academico - Azure ML.'
