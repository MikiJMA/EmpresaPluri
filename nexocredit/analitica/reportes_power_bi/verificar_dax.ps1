param([Parameter(Mandatory = $true)][ValidateRange(1, 65535)][int]$Puerto)
$ErrorActionPreference = 'Stop'
$powerBiRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$powerBiPython = Join-Path $powerBiRoot '.venv\Scripts\python.exe'
$powerBiSqlJson = & $powerBiPython (Join-Path $powerBiRoot 'scripts\verificar_powerbi.py')
if ($LASTEXITCODE -ne 0) { throw 'No se obtuvieron las cifras SQL de referencia.' }
$powerBiSql = ($powerBiSqlJson -join "`n") | ConvertFrom-Json
$null = [System.Reflection.Assembly]::LoadFrom('C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll')
$powerBiConnection = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=127.0.0.1:$Puerto;Connect Timeout=10")
$powerBiFields = [ordered]@{
    total_evaluaciones = 'Total evaluaciones'
    margen_promedio = 'Margen promedio'
    ingresos_promedio = 'Ingresos promedio'
    deuda_promedio = 'Deuda promedio'
    evaluaciones_con_deuda = 'Evaluaciones con deuda'
    cobertura_deuda = 'Cobertura de deuda'
}
$powerBiRowParts = foreach ($powerBiField in $powerBiFields.GetEnumerator()) { '"' + $powerBiField.Key + '", [' + $powerBiField.Value + ']' }
$powerBiRow = 'ROW(' + ($powerBiRowParts -join ', ') + ')'
$powerBiCases = @([PSCustomObject]@{ nombre = 'sin_filtros'; esperado = $powerBiSql.sin_filtros; filtros = @() })
foreach ($powerBiRisk in @('Bajo', 'Medio', 'Alto')) {
    $powerBiCases += [PSCustomObject]@{ nombre = "riesgo:$powerBiRisk"; esperado = $powerBiSql.por_riesgo.$powerBiRisk; filtros = @("'Consulta1'[riesgo_demo] = `"$powerBiRisk`"") }
}
foreach ($powerBiStatus in @('Pendiente', 'Aprobada', 'Rechazada')) {
    $powerBiCases += [PSCustomObject]@{ nombre = "revision:$powerBiStatus"; esperado = $powerBiSql.por_revision.$powerBiStatus; filtros = @("'Consulta1'[estado_revision] = `"$powerBiStatus`"") }
}
foreach ($powerBiCombined in $powerBiSql.filtros_combinados) {
    $powerBiCases += [PSCustomObject]@{ nombre = "combinado:$($powerBiCombined.riesgo)/$($powerBiCombined.revision)"; esperado = $powerBiCombined;
        filtros = @("'Consulta1'[riesgo_demo] = `"$($powerBiCombined.riesgo)`"", "'Consulta1'[estado_revision] = `"$($powerBiCombined.revision)`"") }
}
$powerBiDifferences = @()
$powerBiActual = $null
try {
    $powerBiConnection.Open()
    foreach ($powerBiCase in $powerBiCases) {
        $powerBiCommand = $powerBiConnection.CreateCommand()
        $powerBiCommand.CommandTimeout = 15
        $powerBiCommand.CommandText = if ($powerBiCase.filtros.Count) { 'EVALUATE CALCULATETABLE(' + $powerBiRow + ', ' + ($powerBiCase.filtros -join ', ') + ')' } else { 'EVALUATE ' + $powerBiRow }
        $powerBiReader = $powerBiCommand.ExecuteReader()
        try {
            if (-not $powerBiReader.Read()) { throw 'DAX no devolvió los indicadores esperados.' }
            $powerBiValues = [ordered]@{}
            foreach ($powerBiKey in $powerBiFields.Keys) {
                $powerBiOrdinal = $powerBiReader.GetOrdinal("[$powerBiKey]")
                $powerBiValue = if ($powerBiReader.IsDBNull($powerBiOrdinal)) { $null } else { $powerBiReader.GetValue($powerBiOrdinal) }
                # Las medidas de conteo deben devolver cero por COALESCE.
                # No se normaliza BLANK: debe detectarse como diferencia frente a cero.
                $powerBiValues[$powerBiKey] = $powerBiValue
                $powerBiExpected = $powerBiCase.esperado.$powerBiKey
                $powerBiEqual = if ($null -eq $powerBiValue -or $null -eq $powerBiExpected) {
                    $null -eq $powerBiValue -and $null -eq $powerBiExpected
                } else {
                    $powerBiExpectedNumber = [double]::Parse([string]$powerBiExpected, [System.Globalization.CultureInfo]::InvariantCulture)
                    [Math]::Abs([double]$powerBiValue - $powerBiExpectedNumber) -le [Math]::Max(0.000001, [Math]::Abs($powerBiExpectedNumber) * 0.000000001)
                }
                if (-not $powerBiEqual) { $powerBiDifferences += [PSCustomObject]@{ caso = $powerBiCase.nombre; medida = $powerBiKey; sql = $powerBiExpected; dax = $powerBiValue } }
            }
            if ($powerBiCase.nombre -eq 'sin_filtros') { $powerBiActual = $powerBiValues }
        } finally { $powerBiReader.Close(); $powerBiCommand.Dispose() }
    }
} finally { $powerBiConnection.Dispose() }
[PSCustomObject]@{
    Casos = $powerBiCases.Count
    MedidasPorCaso = $powerBiFields.Count
    DAXSinFiltros = $powerBiActual
    Coincide = $powerBiDifferences.Count -eq 0
    Diferencias = $powerBiDifferences
    Nota = 'Consultas de solo lectura al modelo abierto. No refresca, guarda ni publica el reporte. Los controles visuales se deben probar en Desktop.'
} | ConvertTo-Json -Depth 6
if ($powerBiDifferences.Count) { exit 1 }
