param([switch]$SoloValidar)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$composeDir = Join-Path $project 'infraestructura\contenedores_docker'
$envFile = Join-Path $composeDir '.env'
$endpoint = 'https://julianvillegas191-9159-resource.cognitiveservices.azure.com/openai/responses?api-version=2025-04-01-preview'
$deployment = 'gpt-5-mini-1'

function Merge-OpenAIConfiguration([string]$Existing, [string]$Key) {
    if ($Key -notmatch '^[A-Za-z0-9_+/=-]{16,512}$') { throw 'Formato de clave no valido.' }
    $lines = @($Existing -split '\r?\n' | Where-Object {
        $_ -notmatch '^\s*(?:export\s+)?AZURE_OPENAI_(RESPONSES_URL|DEPLOYMENT|API_KEY)\s*='
    })
    return (($lines -join "`r`n").TrimEnd("`r", "`n") + "`r`nAZURE_OPENAI_RESPONSES_URL=$endpoint`r`nAZURE_OPENAI_DEPLOYMENT=$deployment`r`nAZURE_OPENAI_API_KEY=$Key`r`n")
}
if ($SoloValidar) {
    $sample = "POSTGRES_APP_PASSWORD=conservar`nAZURE_ML_API_KEY=conservar_ml`nAZURE_SEARCH_QUERY_KEY=conservar_search`nAZURE_OPENAI_API_KEY=anterior`nexport AZURE_OPENAI_API_KEY=duplicada"
    $merged = Merge-OpenAIConfiguration $sample 'claveFicticiaDePrueba123=='
    if (-not $merged.Contains('POSTGRES_APP_PASSWORD=conservar') -or
        -not $merged.Contains('AZURE_ML_API_KEY=conservar_ml') -or
        -not $merged.Contains('AZURE_SEARCH_QUERY_KEY=conservar_search') -or
        ([regex]::Matches($merged, '(?m)^AZURE_OPENAI_API_KEY=')).Count -ne 1 -or
        (Merge-OpenAIConfiguration $merged 'claveFicticiaDePrueba123==') -ne $merged) { throw 'Fallo de preservacion.' }
    foreach ($invalid in @('', 'corta', 'clave con espacios', 'clave$interpolada', "clave`nmultilinea")) {
        $rejected = $false
        try { $null = Merge-OpenAIConfiguration $sample $invalid } catch { $rejected = $true }
        if (-not $rejected) { throw 'Clave invalida aceptada.' }
    }
    Write-Host 'Pruebas correctas; no se leyeron secretos ni se modificaron archivos o Azure.'
    exit 0
}
if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) { throw 'Inicia primero la aplicacion Docker local.' }
$dockerExe = (Get-Command docker.exe -ErrorAction SilentlyContinue).Source
if (-not $dockerExe) {
    foreach ($candidate in @("$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe", 'C:\Program Files\Docker\Docker\resources\bin\docker.exe')) {
        if (Test-Path -LiteralPath $candidate) { $dockerExe = $candidate; break }
    }
}
if (-not $dockerExe) { throw 'No se encontro Docker Desktop.' }
& $dockerExe info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Abre Docker Desktop.' }
Write-Host 'Recurso: julianvillegas191-9159-resource. Implementacion: gpt-5-mini-1.'
Write-Host 'Copia la clave de ESE recurso, no la de plurione-ai-creditos.'
Write-Host 'La clave se guarda sin cifrado en el .env local, excluido de Git. Administradores locales y Docker pueden acceder a ella.'
Write-Host 'No compartas ese archivo ni capturas de la clave. Se conserva PostgreSQL, ML y Search.'
$secureKey = Read-Host 'Pega la clave y pulsa Enter (entrada oculta; Ctrl+C cancela)' -AsSecureString
$keyPointer = [IntPtr]::Zero
try {
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer).Trim()
    $existing = [IO.File]::ReadAllText($envFile)
    $updated = Merge-OpenAIConfiguration $existing $plainKey
    [IO.File]::WriteAllText($envFile, $updated, (New-Object Text.UTF8Encoding($false)))
} catch {
    Write-Host 'No se pudo guardar la configuracion. Revisa formato y permisos locales.'
    exit 1
} finally {
    if ($keyPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
    $plainKey = $null; $existing = $null; $updated = $null
    if ($secureKey) { $secureKey.Dispose() }
}
Remove-Item Env:AZURE_OPENAI_RESPONSES_URL,Env:AZURE_OPENAI_DEPLOYMENT,Env:AZURE_OPENAI_API_KEY -ErrorAction SilentlyContinue
$composeArgs = @('compose', '--project-directory', $composeDir, '--env-file', $envFile, '-f', (Join-Path $composeDir 'docker-compose.yml'))
& $dockerExe @composeArgs up -d --no-build --no-deps --wait --wait-timeout 180 backend
if ($LASTEXITCODE -ne 0) { throw 'Configuracion guardada; no se pudo actualizar el backend.' }
& $dockerExe @composeArgs restart frontend
if ($LASTEXITCODE -ne 0) { throw 'Falta reiniciar la interfaz.' }
& $dockerExe @composeArgs exec -T backend python -c 'from backend.app.integraciones.explicaciones_azure_openai.cliente import configurado; import sys; sys.exit(0 if configurado() else 1)'
if ($LASTEXITCODE -ne 0) { throw 'El backend no reconoce la configuracion.' }
Write-Host 'Configuracion local lista; la clave todavia NO se ha validado contra Azure.'
Write-Host 'Recarga PluriOne y evalua datos ficticios. La explicacion se generara automaticamente al guardar; puede generar consumo.'
