$ErrorActionPreference = 'Stop'
$powerBiLibrary = 'C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.Tabular.dll'
if (-not (Test-Path -LiteralPath $powerBiLibrary)) { throw 'Falta la biblioteca de Power BI Desktop. No se validó el modelo.' }
$null = [System.Reflection.Assembly]::LoadFrom($powerBiLibrary)
$powerBiDefinition = Join-Path $PSScriptRoot 'PluriOne_Riesgo_Crediticio.pbix.SemanticModel\definition'
$powerBiDatabase = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($powerBiDefinition)
$powerBiTable = $powerBiDatabase.Model.Tables['Consulta1']
if (-not $powerBiTable -or $powerBiTable.Measures.Count -ne 6) { throw 'El modelo no contiene las seis medidas esperadas.' }
[PSCustomObject]@{
    Estado = 'TMDL deserializado con la biblioteca de Power BI; no ejecuta DAX ni verifica gráficos'
    Tablas = $powerBiDatabase.Model.Tables.Count
    Columnas = $powerBiTable.Columns.Count
    Medidas = $powerBiTable.Measures.Count
} | ConvertTo-Json
