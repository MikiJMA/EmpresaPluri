$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$source = Join-Path $root 'scripts/modo-local.ps1'
$tokens = $null
$errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'El configurador tiene errores de sintaxis.' }
foreach ($name in @('Set-NexoPrivateValues', 'Initialize-NexoLocalConfig', 'Get-NexoLocalValues')) {
    $definition = $ast.Find({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name }, $true)
    if (-not $definition) { throw 'Falta una funcion del configurador.' }
    . ([ScriptBlock]::Create($definition.Extent.Text))
}
$testFile = Join-Path ([IO.Path]::GetTempPath()) ('nexocredit-config-test-' + [guid]::NewGuid().ToString('N') + '.env')
try {
    # Valores exclusivamente ficticios: comprueba todas las ubicaciones Azure sin leer .env real.
    $azureFixture = @{
        AZURE_OPENAI_RESPONSES_URL = 'https://ejemplo-no-real.invalid/openai/responses'
        AZURE_OPENAI_DEPLOYMENT = 'modelo-ficticio'
        AZURE_OPENAI_API_KEY = 'ficticio-azure'
        AZURE_SEARCH_ENDPOINT = 'https://search-no-real.invalid'
        AZURE_SEARCH_INDEX_NAME = 'indice-ficticio'
        AZURE_SEARCH_QUERY_KEY = 'ficticio-search'
        AZURE_ML_SCORING_URI = 'https://ml-no-real.invalid/score'
        AZURE_ML_MODEL_ID = 'modelo-ml-ficticio:1'
        AZURE_ML_API_KEY = 'ficticio-ml'
    }
    $azureLines = @($azureFixture.GetEnumerator() | ForEach-Object { $_.Key + '=' + $_.Value })
    [IO.File]::WriteAllText($testFile, ((@('POSTGRES_APP_PASSWORD=ficticio-no-real', 'BANXICO_API_TOKEN=ficticio-banxico', '# comentario conservado') + $azureLines) -join "`n") + "`n")
    Initialize-NexoLocalConfig $testFile
    $first = [IO.File]::ReadAllText($testFile)
    if ($first -notmatch '(?m)^LOCAL_AUTH_SECRET=([a-f0-9]{64})$') { throw 'No se genero un secreto aleatorio apropiado.' }
    $secretTest = $Matches[1]
    Initialize-NexoLocalConfig $testFile
    $second = [IO.File]::ReadAllText($testFile)
    if (-not $second.Contains('LOCAL_AUTH_SECRET=' + $secretTest)) { throw 'Se roto el secreto al repetir.' }
    Set-NexoPrivateValues $testFile @{ EXPLICACIONES_PROVEEDOR = 'ollama'; DOCUMENTOS_PROVEEDOR = 'local'; ML_PROVEEDOR = 'deshabilitado' }
    $actual = [IO.File]::ReadAllText($testFile)
    foreach ($expected in @('POSTGRES_APP_PASSWORD=ficticio-no-real', 'AZURE_OPENAI_API_KEY=ficticio-azure', 'BANXICO_API_TOKEN=ficticio-banxico', '# comentario conservado', 'EXPLICACIONES_PROVEEDOR=ollama', 'DOCUMENTOS_PROVEEDOR=local', 'ML_PROVEEDOR=deshabilitado')) {
        if (-not $actual.Contains($expected)) { throw 'El cambio de modo no conserva los valores esperados.' }
    }
    Set-NexoPrivateValues $testFile (Get-NexoLocalValues $testFile)
    Set-NexoPrivateValues $testFile @{ EXPLICACIONES_PROVEEDOR = 'azure'; DOCUMENTOS_PROVEEDOR = 'azure'; ML_PROVEEDOR = 'azure' }
    $azureActual = [IO.File]::ReadAllText($testFile)
    foreach ($line in $azureLines) {
        if (-not $azureActual.Contains($line)) { throw 'Cambiar entre local y Azure altero una ubicacion o llave Azure.' }
    }
    if (-not $azureActual.Contains('LOCAL_AUTH_SECRET=' + $secretTest) -or -not $azureActual.Contains('ML_PROVEEDOR=azure')) { throw 'El modo Azure no conserva la identidad local o su seleccion.' }
    foreach ($example in @('backend/.env.example', 'infraestructura/contenedores_docker/.env.example')) {
        $template = [IO.File]::ReadAllText((Join-Path $root $example))
        foreach ($key in $azureFixture.Keys) {
            if ($template -notmatch ('(?m)^' + [regex]::Escape($key) + '=\r?$')) { throw 'Falta un campo Azure vacio en una plantilla publica.' }
        }
    }
    $actual = $azureActual
    $beforeInvalid = $actual
    try { Set-NexoPrivateValues $testFile @{ BAD = "valor`nOTRA=inyeccion" }; throw 'Se acepto un salto de linea.' }
    catch { if ($_.Exception.Message -eq 'Se acepto un salto de linea.') { throw } }
    if ([IO.File]::ReadAllText($testFile) -ne $beforeInvalid) { throw 'Una entrada invalida cambio el archivo.' }
    # Un valor vacio no debe tomar la siguiente variable como si fuera su valor.
    [IO.File]::WriteAllText($testFile, "LOCAL_AUTH_SECRET= `r`nLOCAL_AUTH_TOKEN_SECONDS=1800`r`nOLLAMA_MODEL=`r`nAZURE_OPENAI_API_KEY=ficticio-azure`r`n")
    Initialize-NexoLocalConfig $testFile
    Set-NexoPrivateValues $testFile (Get-NexoLocalValues $testFile)
    if (-not [IO.File]::ReadAllText($testFile).Contains('ML_PROVEEDOR=local')) { throw 'El modo local no activo el modelo UCI incluido.' }
    $blank = [IO.File]::ReadAllText($testFile)
    if ($blank -notmatch '(?m)^LOCAL_AUTH_SECRET=[a-f0-9]{64}\r?$' -or -not $blank.Contains('OLLAMA_MODEL=llama3.1:8b')) { throw 'Los valores vacios no se inicializaron.' }
    if (-not $blank.Contains('LOCAL_AUTH_TOKEN_SECONDS=1800') -or -not $blank.Contains('AZURE_OPENAI_API_KEY=ficticio-azure')) { throw 'Se altero una variable vecina a un campo vacio.' }
    Set-NexoPrivateValues $testFile @{ OLLAMA_MODEL = 'qwen2.5-coder:1.5b-base' }
    Set-NexoPrivateValues $testFile (Get-NexoLocalValues $testFile)
    if (-not [IO.File]::ReadAllText($testFile).Contains('OLLAMA_MODEL=qwen2.5-coder:1.5b-base')) { throw 'El modo local reemplazo un modelo elegido.' }
} finally {
    # Solo un archivo temporal concreto generado por esta prueba, nunca un directorio.
    if (Test-Path -LiteralPath $testFile -PathType Leaf) { Remove-Item -LiteralPath $testFile }
}
Write-Host 'Correcto: modo local preserva claves, genera secreto privado y es repetible. Sin Docker ni archivos privados reales.'
