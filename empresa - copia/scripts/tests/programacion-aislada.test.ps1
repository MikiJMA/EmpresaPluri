$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'probar-programacion.ps1'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'El verificador no tiene sintaxis valida.' }
foreach ($name in @('Get-PostgresTestPlan', 'Remove-PostgresTestContainer')) {
    $definitions = @($ast.FindAll({ param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name
    }, $false))
    if ($definitions.Count -ne 1) { throw "Falta una definicion unica de $name." }
    . ([scriptblock]::Create($definitions[0].Extent.Text))
}

$marker = 'a' * 32
$image = 'sha256:' + ('b' * 64)
$container = 'c' * 64
$plan = @(Get-PostgresTestPlan $marker $image)
if (($plan -join ' ') -notmatch '--network none' -or ($plan -join ' ') -match '(--publish|--volume|--mount|pluri_admin|pluri_credito)') {
    throw 'El plan de pruebas no esta aislado de la base de trabajo.'
}
if ($plan[-1] -ne $image -or $plan -notcontains '--pull=never' -or $plan -notcontains "io.plurione.suite-test=$marker") {
    throw 'Se pierde la imagen exacta o la identidad temporal.'
}
foreach ($invalid in @('', 'plurione-docker-postgres-1', '../salida', 'a;otra-cosa')) {
    $rejected = $false
    try { $null = Get-PostgresTestPlan $invalid $image } catch { $rejected = $true }
    if (-not $rejected) { throw 'Se acepto un marcador temporal no valido.' }
}
function Invoke-FakeTestDocker {
    $script:calls += ,@($args)
    $global:LASTEXITCODE = 0
    if ($args[0] -eq 'inspect') { return ('{"io.plurione.suite-test":"' + $script:owner + '"}') }
}
$initialExit = $LASTEXITCODE
try {
    foreach ($owner in @($marker, 'otro-propietario')) {
        $script:owner = $owner
        $script:calls = @()
        $failure = $false
        try { Remove-PostgresTestContainer 'Invoke-FakeTestDocker' $container $marker } catch { $failure = $true }
        if ($owner -eq $marker) {
            if ($failure -or $script:calls.Count -ne 2 -or $script:calls[1][0] -ne 'rm' -or $script:calls[1][-1] -ne $container) {
                throw 'La limpieza debe limitarse al contenedor temporal propio.'
            }
        } elseif (-not $failure -or $script:calls.Count -ne 1) { throw 'Se intento eliminar un contenedor ajeno.' }
    }
    $script:calls = @()
    $rejected = $false
    try { Remove-PostgresTestContainer 'Invoke-FakeTestDocker' 'plurione-docker-postgres-1' $marker } catch { $rejected = $true }
    if (-not $rejected -or $script:calls.Count) { throw 'La limpieza no debe aceptar el nombre de la base principal.' }
} finally { $global:LASTEXITCODE = $initialExit }
Write-Host 'Correcto: prueba sin red externa, puertos ni montajes; limpieza propia y rechazo de destinos ajenos. Sin Docker real.'
