$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'docker.ps1'
$tokens = $null
$errorsFound = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$errorsFound)
if ($errorsFound.Count) { throw 'El lanzador Docker no tiene sintaxis valida.' }
$definition = @($ast.FindAll({ param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-PluriOneWebUrl'
}, $false))
if ($definition.Count -ne 1) { throw 'Falta la funcion de URL del lanzador.' }
. ([scriptblock]::Create($definition[0].Extent.Text))
if ((Get-PluriOneWebUrl) -ne 'http://localhost:8080/') { throw 'El origen predeterminado no coincide con Entra.' }
if ((Get-PluriOneWebUrl '8081') -ne 'http://localhost:8081/') { throw 'Se ignora el puerto configurado.' }
foreach ($invalid in @('', '0', '65536', '8080/path', 'abc', '-1', '8080;otra-cosa')) {
    $rejected = $false
    try { $null = Get-PluriOneWebUrl $invalid } catch { $rejected = $true }
    if (-not $rejected) { throw 'Se acepto un puerto invalido.' }
}
Write-Host 'Correcto: localhost para Entra, puerto configurable y rechazo de entradas invalidas. Sin Docker ni secretos.'
