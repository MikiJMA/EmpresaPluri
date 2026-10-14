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
$dockerTestRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$nginxTest = Get-Content -LiteralPath (Join-Path $dockerTestRoot 'infraestructura/contenedores_docker/nginx.conf') -Raw
$backendTest = Get-Content -LiteralPath (Join-Path $dockerTestRoot 'infraestructura/contenedores_docker/backend.Dockerfile') -Raw
if (-not $nginxTest.Contains('proxy_set_header X-Forwarded-For $remote_addr;') -or $nginxTest.Contains('$proxy_add_x_forwarded_for')) { throw 'El proxy no sobrescribe el origen no confiable.' }
if (-not $backendTest.Contains('--no-proxy-headers')) { throw 'Uvicorn no debe confiar automaticamente en encabezados enviados al puerto directo.' }
Write-Host 'Correcto: origen Entra, puerto configurable, encabezado sobrescrito y proxy explicito. Sin Docker ni secretos.'
