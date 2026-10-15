param(
    [Parameter(Mandatory=$true)][string]$Zip,
    [string]$Imagen = 'mcr.microsoft.com/azureml/curated/ai-ml-automl@sha256:dfdbb322eee5cd05598e775f670507a69209fb07ca0fe6b011983101181946d5'
)
$ErrorActionPreference = 'Stop'
$evaluationBase = Split-Path -Parent $PSScriptRoot
$evaluationZip = (Resolve-Path -LiteralPath $Zip).Path
$evaluationScript = Join-Path $PSScriptRoot 'evaluar_candidato.py'
$evaluationTrain = Join-Path $evaluationBase 'carga_azure/entrenamiento_reducido/entrenamiento_reducido.csv'
$evaluationValidation = Join-Path $evaluationBase 'carga_azure/validacion/validacion.csv'
$evaluationTest = Join-Path $evaluationBase 'datos_uci/prueba.csv'
$evaluationOutput = Join-Path $PSScriptRoot ('resultados/' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
New-Item -ItemType Directory -Path $evaluationOutput | Out-Null
$evaluationArgs = @(
    'run', '--rm', '--network=none', '--read-only', '--cap-drop=ALL',
    '--security-opt=no-new-privileges', '--user=65534:65534',
    '--cpus=2', '--memory=4g', '--pids-limit=256',
    '--tmpfs=/tmp:rw,nosuid,nodev,size=1073741824', '--workdir=/tmp',
    '--env=PYTHONDONTWRITEBYTECODE=1', '--env=OMP_NUM_THREADS=2',
    '--env=OPENBLAS_NUM_THREADS=2', '--env=XDG_CACHE_HOME=/tmp/cache',
    '--env=MPLCONFIGDIR=/tmp/matplotlib',
    '--mount', "type=bind,source=$evaluationZip,target=/inputs/model.zip,readonly",
    '--mount', "type=bind,source=$evaluationScript,target=/inputs/evaluar.py,readonly",
    '--mount', "type=bind,source=$evaluationTrain,target=/inputs/train.csv,readonly",
    '--mount', "type=bind,source=$evaluationValidation,target=/inputs/validation.csv,readonly",
    '--mount', "type=bind,source=$evaluationTest,target=/inputs/test.csv,readonly",
    '--mount', "type=bind,source=$evaluationOutput,target=/results",
    '--entrypoint=/azureml-envs/azureml-automl/bin/python', $Imagen,
    '/inputs/evaluar.py', '--zip=/inputs/model.zip', '--train=/inputs/train.csv',
    '--validation=/inputs/validation.csv', '--test=/inputs/test.csv',
    '--output=/results/evaluacion.json'
)
& docker @evaluationArgs 2>&1 | Tee-Object -FilePath (Join-Path $evaluationOutput 'ejecucion.log')
$evaluationExit = $LASTEXITCODE
if ($evaluationExit -ne 0) { throw "La evaluacion no finalizo: codigo $evaluationExit. Registro: $evaluationOutput" }
Write-Output "Resultados: $evaluationOutput"
