# Modelos predictivos — Python y Azure Machine Learning

Función: preparar datos, entrenar, evaluar y versionar modelos de riesgo.
Estado: candidato académico UCI entrenado en Azure, recuperado y registrado como `plurione-uci-voting-candidato:1`; carga y evaluación local verificadas. No hay despliegue ni integración predictiva con la aplicación. Ver [evaluación, métricas y límites](evaluacion/README.md).

## Experimento académico UCI

Configuración utilizada: entrenamiento reducido (17.909), validación independiente (6.136), prueba independiente (5.955), ahora evaluada. Paquetes y selección correcta para AutoML en [carga de datos](carga_azure/README.md). Las particiones fueron registradas en Azure. No usar el entrenamiento completo con la nueva validación ni optimizar el candidato contra la prueba ya consultada.

Ver [datos y límites de uso](datos_uci/README.md). Se generaron `entrenamiento.csv` y `prueba.csv` desde UCI, con un script reproducible en `preparacion_datos/preparar_uci.py`. No se han subido desde este script a Azure ni creado recursos de cómputo.
El trabajo `uci-incumplimiento-automl-1` entrenó sobre `cpu-plurione` y guardó el modelo, pero quedó fallido por un error de etiquetas reservadas durante la generación de código. El artefacto se recuperó sin reentrenar. La evaluación aislada reprodujo la validación y obtuvo AUC 0,775274 en prueba; detectó 403 de 1.259 incumplimientos (32,01 %). No está aprobado para uso real.

Organización prevista: preparacion_datos/, entrenamiento/, evaluacion/ y despliegue/.
Antes de integrar un modelo real: acordar definición de incumplimiento y horizonte para la población objetivo; obtener datos autorizados y representativos. UCI solo sirve para este experimento separado.
Evidencias necesarias: particiones temporales, comparación con baseline, métricas de discriminación y calibración, versión reproducible y despliegue verificado.
Las reglas de backend/app/evaluacion_crediticia son solamente la demostración actual.
