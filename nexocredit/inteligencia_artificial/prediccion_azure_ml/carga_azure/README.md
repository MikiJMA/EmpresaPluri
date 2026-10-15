# Paquete local para Azure ML

## Configuración con validación independiente (24 de septiembre de 2026)

Para el trabajo AutoML actual usar los siguientes recursos distintos:

| Función | Nombre del recurso nuevo/existente | Carpeta local | Filas |
|---|---|---|---:|
| Entrenar | `uci-incumplimiento-entrenamiento-reducido` (nuevo) | `entrenamiento_reducido` | 17.909 |
| Validar y seleccionar modelo | `uci-incumplimiento-validacion` (nuevo) | `validacion` | 6.136 |
| Evaluación final | `uci-incumplimiento-prueba` (existente) | `prueba` | 5.955 |

Cada carpeta contiene solamente `MLTable` y su CSV. Registrar las nuevas carpetas por separado como Tabla (MLTable), en `workspaceblobstore`, sin sobrescribir los recursos previos. La carga y lectura de los nuevos recursos en Azure aún están pendientes.

En **Tipo de tarea y datos**, reemplazar `uci-incumplimiento-entrenamiento` por `uci-incumplimiento-entrenamiento-reducido`. En **Datos de validación de usuario**, seleccionar `uci-incumplimiento-validacion`. No combinar la validación con el entrenamiento completo, que la contiene. No usar prueba para validación ni para elegir modelos o hiperparámetros.

La etiqueta y las otras 19 columnas se conservan. Ambos MLTable usan la misma lectura que los recursos existentes, incluida la inferencia de tipos; en Azure debe comprobarse que la etiqueta siga siendo booleana en los dos nuevos recursos. No se ha ejecutado el motor MLTable localmente.

División reproducible: `python preparacion_datos/preparar_validacion.py` desde la carpeta de Azure ML. Verificación: `python preparacion_datos/verificar_validacion.py`. SHA-256 de los 19 predictores con semilla `plurione-validacion-agrupada-v1`; probabilidad de grupo 25% a validación, resto a entrenamiento reducido. Sin estratificación ni partición temporal. Conserva los grupos de predictores idénticos, todas las filas y etiquetas; sin solapamiento entre las tres particiones. No altera los archivos anteriores. Auditoría por línea del CSV original y conteos/huellas en `datos_uci/auditoria_validacion.csv` y `datos_uci/division_validacion.json`.

Fuente/licencia y límites de uso académico: [documentación UCI](../datos_uci/README.md). Esta separación no demuestra representatividad local, calibración ni ausencia de sesgos.

## Paquetes iniciales conservados

Seleccionar solamente la carpeta `entrenamiento` en el asistente de carga MLTable. Contiene la definición `MLTable` (sin extensión) y una copia exacta de `../datos_uci/entrenamiento.csv` respecto de esta carpeta.

No seleccionar la carpeta padre ni agregar prueba, original o auditoría al recurso de entrenamiento. Para registrar `uci-incumplimiento-prueba`, seleccionar únicamente la carpeta `prueba`, que contiene su propio `MLTable` y una copia exacta de `datos_uci/prueba.csv`. Reservar este recurso para evaluación final, no para entrenamiento ni selección de modelos. La preparación local de estos paquetes no carga datos ni inicia cómputo en Azure.

Fuente, licencia CC BY 4.0, límites de uso y procedimiento reproducible: [documentación de los datos](../datos_uci/README.md). Si se regeneran los datos, actualizar la copia de entrenamiento y comprobar que su SHA-256 coincide con el archivo de origen antes de subir.

La definición sigue el [esquema oficial MLTable](https://learn.microsoft.com/en-us/azure/machine-learning/reference-yaml-mltable?view=azureml-api-2). La lectura en Azure queda pendiente de verificar en el portal.
