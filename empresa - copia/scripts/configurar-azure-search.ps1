param([switch]$SoloValidar)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $project 'infraestructura\contenedores_docker\.env'
$endpoint = 'https://search-plurione-demo-julian.search.windows.net'
$indexName = 'plurione-documentos-demo'

function Merge-SearchConfiguration([string]$Existing, [string]$Key) {
    # Valida sintaxis, no autenticidad ni permisos de la clave.
    if ($Key -notmatch '^[A-Za-z0-9_+/=-]{16,512}$') {
        throw 'Formato no valido. Copia una clave de consulta de Azure sin comillas.'
    }
    $lines = @($Existing -split '\r?\n' | Where-Object {
        $_ -notmatch '^\s*(?:export\s+)?AZURE_SEARCH_(ENDPOINT|QUERY_KEY|INDEX_NAME)\s*='
    })
    return (($lines -join "`r`n").TrimEnd("`r", "`n") + "`r`nAZURE_SEARCH_ENDPOINT=$endpoint`r`nAZURE_SEARCH_QUERY_KEY=$Key`r`nAZURE_SEARCH_INDEX_NAME=$indexName`r`n")
}

if ($SoloValidar) {
    $sample = "POSTGRES_APP_PASSWORD=conservar`nAZURE_ML_API_KEY=conservar_ml`nWEB_PORT=8080`nAZURE_SEARCH_QUERY_KEY=anterior`nexport AZURE_SEARCH_QUERY_KEY=duplicada"
    $merged = Merge-SearchConfiguration $sample 'claveFicticiaDePrueba123=='
    if (-not $merged.Contains('POSTGRES_APP_PASSWORD=conservar') -or
        -not $merged.Contains('AZURE_ML_API_KEY=conservar_ml') -or
        -not $merged.Contains('WEB_PORT=8080') -or
        ([regex]::Matches($merged, '(?m)^AZURE_SEARCH_QUERY_KEY=')).Count -ne 1 -or
        (Merge-SearchConfiguration $merged 'claveFicticiaDePrueba123==') -ne $merged) {
        throw 'Fallo al preservar la configuracion o eliminar duplicados.'
    }
    foreach ($invalid in @('', 'corta', 'clave con espacios', 'clave$conInterpolacion', "clave`nconSaltosDeLinea")) {
        $rejected = $false
        try { $null = Merge-SearchConfiguration $sample $invalid } catch { $rejected = $true }
        if (-not $rejected) { throw 'Una clave mal formada fue aceptada.' }
    }
    Write-Host 'Pruebas correctas: preservacion, duplicados, repeticion y entradas invalidas.'
    Write-Host 'No se leyeron secretos ni se modificaron archivos, Docker o Azure.'
    exit 0
}

if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) {
    throw 'Falta el .env local de Docker. Inicia primero la aplicacion local.'
}
Write-Host "Servicio: $endpoint"
Write-Host 'En Azure, copia la clave de Administrar claves de consulta (seccion inferior).'
Write-Host 'NO copies una clave de administrador. Este configurador no necesita permisos de escritura en Azure.'
Write-Host 'Se guardara en el .env local de Docker, sin cifrado en disco y excluido de Git.'
Write-Host 'Administradores locales pueden leerlo. No compartas ese archivo.'
Write-Host 'No se cargan documentos ni se reinician contenedores en este paso.'
$secureKey = Read-Host 'Pega la clave de consulta y pulsa Enter (entrada oculta; Ctrl+C cancela)' -AsSecureString
$keyPointer = [IntPtr]::Zero
try {
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer).Trim()
    $existing = [IO.File]::ReadAllText($envFile)
    $updated = Merge-SearchConfiguration $existing $plainKey
    # Mantiene las ACL del archivo existente y las variables ajenas a Search.
    [IO.File]::WriteAllText($envFile, $updated, (New-Object Text.UTF8Encoding($false)))
} catch {
    # No imprimir excepciones que pudieran contener datos privados.
    Write-Host 'No se pudo completar el guardado. Comprueba la clave y los permisos del archivo local.'
    exit 1
} finally {
    if ($keyPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer) }
    $plainKey = $null; $existing = $null; $updated = $null
    if ($secureKey) { $secureKey.Dispose() }
}
Write-Host 'Configuracion guardada. La clave todavia NO se ha validado contra Azure.'
Write-Host 'Pendiente: crear el indice, cargar los documentos y conectar el buscador de PluriOne.'
