# Evaluación local del candidato UCI

## Resultado verificado

Evaluación terminada el 26 de septiembre de 2026 a las 03:20 UTC (25 de septiembre en México).
Modelo Azure ML: `plurione-uci-voting-candidato:1`, VotingEnsemble, procedente de
`uci-incumplimiento-automl-1_4`. El modelo carga y predice localmente. La carga genérica
MLflow también pasó una prueba de cinco filas y coincidió con la carga scikit-learn.

Se reprodujeron las métricas de validación antes de evaluar el conjunto de prueba.
No se reentrenó, no se ajustaron umbrales y no se usó Azure para esta evaluación.

| Métrica | Validación (6.136 filas) | Prueba (5.955 filas) |
| --- | ---: | ---: |
| ROC AUC, clase incumplimiento | 0,786294 | 0,775274 |
| Exactitud | 81,73 % | 82,55 % |
| Exactitud balanceada | 63,49 % | 64,06 % |
| Sensibilidad a incumplimiento | 31,10 % | 32,01 % |
| Precisión entre positivos predichos | 67,92 % | 68,77 % |
| F1 de incumplimiento | 0,426598 | 0,436856 |
| Average precision | 0,541990 | 0,548352 |
| Brier score (menor es mejor) | 0,134991 | 0,131972 |
| Log loss (menor es mejor) | 0,429792 | 0,423969 |
| Exactitud de predecir siempre no incumplimiento | 78,15 % | 78,86 % |

Matriz de prueba: TN=4.513, FP=183, FN=856, TP=403. Se detectaron 403 de los
1.259 incumplimientos; 856 quedaron sin detectar. La exactitud supera en 3,69 puntos
porcentuales el baseline trivial, pero no demuestra aptitud para decisiones crediticias.
Las predicciones se obtuvieron con el comportamiento nativo del modelo, sin modificar
sus reglas de clasificación. El orden de clases queda documentado en el JSON.

**Estado: candidato académico evaluado, no aprobado para producción.** Datos UCI de
Taiwán de 2005, particiones aleatorias agrupadas, sin validación temporal ni evidencia
de representatividad para clientes de PluriOne. No se evaluó equidad ni calibración
prospectiva. Las 19 entradas UCI no equivalen a las entradas actuales de la aplicación.
No se conectó el modelo al formulario ni se desplegó un servicio.

## Evidencias y origen del fallo

- [Métricas, versiones y huellas](resultados/20260926T032027806Z/evaluacion.json).
- [Registro de ejecución local](resultados/20260926T032027806Z/ejecucion.log).
- Archivo recibido: `plurione-uci-voting-candidato_.zip`.
- SHA256 del ZIP: `649b9c1489bcdb2e826cdf6fa4dd809db5d6a369600c6b4b8a442a25896ee9ee`.
- SHA256 del modelo: `b7d18b9419c7a1184f07a01c7a774f291d795d7d679eaa46e7a4db9325e84f58`.

El registro de Azure de la ejecución original indica `Saved mlflow model successfully`
antes de fallar en `generate_model_code_and_notebook`, al llamar `current_run.set_tags`.
El servicio respondió HTTP 400: etiquetas reservadas no modificables después de crear
el trabajo. Por ello, el trabajo original sigue en estado fallido aunque el artefacto
fue guardado y ahora su carga local está comprobada. No se modificaron etiquetas
reservadas ni se otorgaron permisos adicionales.

La auditoría local verifica CRC y lista exacta del ZIP, huellas de modelo/datos, nombres
de columnas, cantidades de filas y ausencia de intersección de predictores entre
entrenamiento reducido, validación y prueba. Se comprobó que las probabilidades son
finitas, están entre cero y uno y suman uno, y se reconciliaron métricas con la matriz.

## Reproducir sin tocar la aplicación

Requiere Docker Desktop con contenedores Linux. Imagen oficial de Microsoft
`mcr.microsoft.com/azureml/curated/ai-ml-automl:41`, fijada en el lanzador al digest:
`sha256:dfdbb322eee5cd05598e775f670507a69209fb07ca0fe6b011983101181946d5`.
La imagen ocupa aproximadamente 8 GB y permanece en la caché local de Docker.

Desde esta carpeta:

```powershell
.\evaluar_local.ps1 -Zip 'C:\ruta\plurione-uci-voting-candidato_.zip'
```

El lanzador crea una carpeta de resultados nueva por ejecución. Usa dos CPU, 4 GB RAM,
un límite de diez minutos en el proceso, usuario no privilegiado, sistema raíz de solo
lectura, datos de solo lectura y red desactivada. No monta credenciales, el repositorio
completo ni el socket de Docker. El contenedor temporal se elimina al terminar.
Las instalaciones Python de Windows y los contenedores de la aplicación no cambian.

No ejecutar el pickle fuera del aislamiento ni sustituirlo por archivos desconocidos:
la carga pickle puede ejecutar código. Las huellas están fijadas al artefacto cuyo
origen se verificó en Azure. Ver [persistencia de scikit-learn](https://scikit-learn.org/stable/model_persistence.html)
y [carga MLflow sklearn](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html).

Las siguientes mejoras deben utilizar entrenamiento/validación, no optimizar contra
este conjunto de prueba ya consultado. Una selección posterior basada en sus métricas
requeriría otra evaluación final independiente.
