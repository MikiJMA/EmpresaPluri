$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'configurar-banxico.ps1'
$parseTokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$parseTokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'El configurador no tiene sintaxis valida.' }

# Carga solo funciones concretas: no ejecuta la entrada interactiva ni lee el .env.
foreach ($name in @('Get-BanxicoStartupPlan', 'Invoke-BanxicoStartup')) {
    $definitions = @($ast.FindAll({ param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name
    }, $false))
    if ($definitions.Count -ne 1) { throw "No se encontro una definicion unica de $name." }
    . ([scriptblock]::Create($definitions[0].Extent.Text))
}

function Invoke-FakeDocker {
    $script:testCalls += ,@($args)
    # Docker emite progreso en stderr aun cuando termina correctamente.
    Write-Error 'Mensaje ficticio privado que no debe aparecer en el resultado.'
    $global:LASTEXITCODE = if ($script:testFailAt -eq $script:testCalls.Count) { 1 } else { 0 }
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

$initialExitCode = $LASTEXITCODE
try {
    foreach ($failAt in @(0, 1, 2)) {
        $script:testCalls = @()
        $script:testFailAt = $failAt
        $failure = $null
        $captured = @()
        try {
            $captured = @(Invoke-BanxicoStartup 'Invoke-FakeDocker' @('compose', '--project-name', 'prueba') 6>&1)
        } catch { $failure = $_.Exception.Message }
        Assert-True ($ErrorActionPreference -eq 'Stop') 'No se restauro ErrorActionPreference.'
        Assert-True (-not (($captured | Out-String).Contains('Mensaje ficticio privado'))) 'Se filtro un mensaje privado.'
        Assert-True ($script:testCalls[0][-1] -eq 'postgres') 'PostgreSQL debe ser el primer paso.'
        Assert-True ($script:testCalls[0] -contains '--no-recreate') 'PostgreSQL no debe recrearse.'
        Assert-True ($script:testCalls[0] -contains '--wait') 'Debe esperar la salud de PostgreSQL.'
        if ($failAt -eq 1) {
            Assert-True ($script:testCalls.Count -eq 1) 'No debe recrear el backend si PostgreSQL falla.'
            Assert-True ($failure -like '*PostgreSQL no pudo iniciar*') 'Falta el error sanitizado de PostgreSQL.'
        } else {
            Assert-True ($script:testCalls.Count -eq 2) 'El arranque debe ejecutar exactamente dos pasos.'
            Assert-True ($script:testCalls[1][-1] -eq 'backend') 'La API debe arrancar despues de PostgreSQL.'
            Assert-True ($script:testCalls[1] -contains '--force-recreate') 'Debe aplicar la configuracion a la API.'
            if ($failAt -eq 0) { Assert-True ($null -eq $failure) 'El progreso en stderr no debe provocar un fallo.' }
            else { Assert-True ($failure -like '*backend no paso*') 'Falta el error sanitizado del backend.' }
        }
    }
} finally { $global:LASTEXITCODE = $initialExitCode }

Write-Host 'Correcto: orden, proteccion de PostgreSQL, progreso en stderr, fallos aislados y restauracion de preferencias.'
Write-Host 'Pruebas simuladas: no se leyeron secretos ni se ejecutaron Docker o proveedores.'
