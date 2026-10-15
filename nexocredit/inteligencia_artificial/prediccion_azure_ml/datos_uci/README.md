# Datos de demostración: incumplimiento de tarjetas

Preparado el 23 de septiembre de 2026. Uso académico; no apto para aprobar o denegar créditos reales.

## Fuente y licencia

Yeh, I. (2009). *Default of Credit Card Clients* [Dataset]. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C55S3H

- Ficha: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- CSV oficial: https://archive.ics.uci.edu/static/public/350/data.csv
- Licencia indicada por UCI: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Mantener atribución, enlace a licencia e indicación de cambios al redistribuir.
- Cambios: renombrado de columnas, exclusión de identificador y variables demográficas de los archivos de modelado, separación de filas. No se inventaron observaciones, imputaron valores ni modificaron etiquetas.

La muestra contiene 30.000 clientes de tarjetas de Taiwán con historia de abril a septiembre de 2005. Los importes están en dólares taiwaneses (NTD), no pesos mexicanos. El resultado observado es incumplimiento del mes siguiente, no un puntaje crediticio ni la regla de riesgo actual de PluriOne.

## Archivos

**Actualización 24/09/2026:** para AutoML con validación de usuario, el entrenamiento completo de esta tabla se subdividió sin modificarlo: 17.909 filas en `carga_azure/entrenamiento_reducido` y 6.136 en `carga_azure/validacion`. Usar ambos recursos nuevos, no entrenamiento completo junto con su subconjunto de validación. Prueba sigue intacto (5.955 filas). Véase [configuración vigente](../carga_azure/README.md).

| Archivo | Uso | Filas | Etiqueta 0 / 1 |
|---|---|---:|---:|
| entrenamiento.csv | Desarrollo y validación interna | 24.045 | 18.668 / 5.377 |
| prueba.csv | Evaluación final reservada | 5.955 | 4.696 / 1.259 |
| original_uci.csv | Fuente sin cambios; no subir como entrenamiento | 30.000 | 23.364 / 6.636 |
| auditoria_particiones.csv | Vincula ID original con partición y grupo; no usar como predictor | 30.000 | — |
| validacion.json | Conteos, parámetros y huellas SHA-256 | — | — |

Los dos archivos de modelado son CSV UTF-8 separados por comas, con cabecera única, 19 predictores numéricos y una etiqueta. No contienen valores vacíos. La etiqueta es `incumplimiento_mes_siguiente`: 1 = incumplimiento observado; 0 = no observado.

## Diccionario y correspondencias

| Columnas del CSV preparado | Fuente | Significado |
|---|---|---|
| LIMIT_BAL | X1 | Límite de crédito en NTD |
| PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6 | X6–X11 | Estado mensual de pago, septiembre a abril de 2005, en ese orden |
| BILL_AMT1 a BILL_AMT6 | X12–X17 | Importe mensual del estado de cuenta en NTD, septiembre a abril |
| PAY_AMT1 a PAY_AMT6 | X18–X23 | Pagos mensuales en NTD, septiembre a abril |
| incumplimiento_mes_siguiente | Y | Resultado binario del mes siguiente |

Para PAY, UCI documenta -1 como pago puntual y valores positivos como meses de retraso. La fuente también contiene -2 y 0; se conservan sin adjudicarles un significado que esa documentación no explica. No son días de atraso. Los importes negativos de estados de cuenta se conservan; no se confunden con datos faltantes.

ID se conserva solo para auditoría. Se excluyen X2 (sexo), X3 (educación), X4 (estado civil) y X5 (edad) del experimento inicial. Esta decisión no demuestra ausencia de sesgos: los demás campos pueden funcionar como indicadores indirectos. El original mantiene todos los campos para trazabilidad.

## Separación y comprobaciones

Partición reproducible mediante SHA-256 de los predictores retenidos y semilla `plurione-uci350-v1`, aproximadamente 80/20. No es estratificada ni temporal. Todos los registros con predictores idénticos quedan juntos aunque sus etiquetas difieran: 29.183 grupos, 134 con varias filas y 85 con etiquetas distintas. Se mantienen las 30.000 filas; no hay grupos compartidos entre entrenamiento y prueba. Las proporciones de incumplimiento son 22,36 % y 21,14 %, respectivamente.

No ajustar transformaciones, selección de variables, hiperparámetros, umbrales ni calibración usando `prueba.csv`. Para esas decisiones utilizar validación interna de entrenamiento, manteniendo juntos los mismos grupos mediante el hash de los 19 predictores (o auditoría). Ajustar escaladores e imputadores, si se usan, solo sobre cada pliegue de entrenamiento. La prueba se reserva para una evaluación final; evitar búsquedas repetidas sobre sus resultados.

Una cohorte histórica no permite una prueba temporal independiente. Antes de cualquier aplicación real se necesitan datos locales autorizados, evaluación fuera de tiempo, calibración, revisión de sesgos y definición operacional del incumplimiento. No hay métricas de modelo todavía.

## Reproducir

Desde esta carpeta de Azure ML, con Python 3.10 o posterior, sin dependencias externas:

```powershell
python preparacion_datos/preparar_uci.py
python preparacion_datos/verificar_datos.py
```

El preparador reutiliza el original local; si falta, lo descarga por HTTPS desde UCI. Verifica su SHA-256 fijado antes de procesarlo y regenera los archivos derivados. Si la fuente cambia, se detiene para revisión. El verificador comprueba filas, clases, trazabilidad, ausencia de solapamiento y reproducibilidad.

## Azure y aplicación

No se han cargado estos archivos a Azure ni ejecutado entrenamientos. En Azure ML registrar entrenamiento y prueba por separado; para clasificación tabular seleccionar la etiqueta indicada. Revisar el costo antes de crear cómputo; una alerta de presupuesto no detiene por sí sola el consumo.

Estos predictores **no coinciden con el formulario actual**: no representan sus ingresos, gastos o score. No renombrar BILL_AMT como deuda del formulario ni LIMIT_BAL como ingresos. Entrenar aquí es un experimento separado; integrar un modelo requerirá un contrato de entrada diferente o datos representativos de los campos del sistema. Las reglas existentes siguen siendo una demostración, no este modelo.
