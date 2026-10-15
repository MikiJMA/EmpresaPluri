# Modelo predictivo local — experimento UCI

Entrenado y contrastado el 12/10/2026. Baseline de aprendizaje automático independiente del candidato Azure AutoML: **StandardScaler + LogisticRegression**. Es IA predictiva, no una plantilla de explicación ni un modelo de Ollama. Azure ML se conserva como proveedor opcional; el scoring principal de NexoCredit sigue siendo demostrativo.

## Datos y separación

Fuente: [Default of Credit Card Clients, UCI](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients), I-Cheng Yeh, 2009; población de Taiwán, observaciones 2005, licencia CC BY 4.0. Los importes son NTD. Se reutilizan las particiones académicas locales ya preparadas en `../prediccion_azure_ml`, sin descargar ni enviar datos de usuarios:

| Partición | Archivo en prediccion_azure_ml | Filas | SHA-256 |
|---|---|---:|---|
| Entrenamiento | `carga_azure/entrenamiento_reducido/entrenamiento_reducido.csv` | 17.909 | `d3f2caae94533112d2c0a58241fdb9e1641d6d2ad9cef10635c727ccde6f5b79` |
| Validación | `carga_azure/validacion/validacion.csv` | 6.136 | `212b599be2da5989d2762d2b7bc7516bfbb8f56990d988b6f80a7afd49684891` |
| Prueba | `datos_uci/prueba.csv` | 5.955 | `d7cf431db3eb63400d72a5cfca20d679396013ccc18ff5c902ff71215b01fb72` |

Se verifican huellas, orden exacto de columnas, tamaños, ausencia de faltantes/no finitos, ambas clases y cero solapamiento de grupos de predictores entre particiones. Son divisiones agrupadas aleatorias, no una validación temporal, prospectiva o mexicana. No se usa la base PostgreSQL del proyecto.

Predictores: `LIMIT_BAL`, `PAY_0`, `PAY_2`…`PAY_6`, `BILL_AMT1`…`BILL_AMT6`, `PAY_AMT1`…`PAY_AMT6`. Objetivo: `incumplimiento_mes_siguiente`. Se excluyen sexo, educación, estado civil, edad e identificadores. Eso no constituye una auditoría de equidad.

## Entrenamiento

Los parámetros se fijaron antes de evaluar: C=1, class_weight=balanced, solver=lbfgs, max_iter=1500, tol=1e-7, random_state=20261012. StandardScaler y regresión logística se ajustan solo con entrenamiento. No se seleccionaron parámetros/umbral con validación o prueba. Umbral binario 0,5; un empate corresponde a clase 0.

Entorno observado: Python 3.12.15, scikit-learn 1.9.1, numpy 2.5.4 y pandas 3.0.6. Se usó la imagen backend ya instalada, con red deshabilitada, raíz de solo lectura y límites de 1 GB / dos CPU. No se montaron secretos, sesiones o volúmenes PostgreSQL.

Reproducción desde la carpeta interior en un entorno con las dependencias del backend instaladas:

```powershell
python .\inteligencia_artificial\prediccion_local\entrenar.py --datos '.\inteligencia_artificial\prediccion_azure_ml' --salida '.\.tmp\ml-local-reproduccion-01'
```

La salida debe ser una carpeta nueva: el script rechaza sobrescribir `modelo.json` o `entrenamiento.json`. No copia ni activa automáticamente un modelo. Otras versiones de bibliotecas/plataforma pueden alterar números de punto flotante y la huella; requieren comparación y revisión explícitas.

## Artefactos

Modelo servido: `nexocredit-uci-logistica-v1`. Archivos incluidos en `../../backend/app/integraciones/prediccion_local/artefactos`:

- `modelo.json`: medias, escalas, coeficientes, intercepto, clases, rangos observados y métricas; solo números/listas/metadatos.
- `entrenamiento.json`: procedencia, parámetros, versiones, huellas y resultados del contraste.

SHA-256 del modelo: `259b997587543c3466f665a8b62577465014c2c867ebdbfba61544b2d364b8a4`.

La inferencia suma el logit estandarizado y devuelve clase 1 cuando es mayor que cero. Sus clases coinciden con `pipeline.predict` de scikit-learn en las **30.000 filas**, sin discrepancias. No se deserializan objetos Python ni se carga `model.pkl`. El contrato/huella están fijados en el adaptador para detectar sustituciones accidentales; no es una firma criptográfica que proteja contra un atacante con control del código.

## Evaluación realmente obtenida

| Métrica | Validación (6.136) | Prueba (5.955) |
|---|---:|---:|
| AUC ROC | 0,71860 | 0,71505 |
| Exactitud | 69,92 % | 70,28 % |
| Sensibilidad positiva | 64,06 % | 60,92 % |
| Precisión positiva | 38,64 % | 37,51 % |
| F1 positivo | 48,20 % | 46,43 % |
| Exactitud siempre negativo | 78,15 % | 78,86 % |

Matriz de prueba: filas reales [0,1], columnas predichas [0,1]: `[[3418,1278],[492,767]]`.

La exactitud no supera al clasificador siempre negativo. El balance de clases permite detectar más positivos a costa de falsos positivos. No afirmar que este modelo es superior en todas las métricas al candidato AutoML; tampoco que la salida es una probabilidad calibrada de crédito real. No se validaron calibración, deriva, equidad, costos de error, reglas oficiales, representatividad de México o un piloto real. No autoriza ni rechaza créditos y no usa las entradas MXN del formulario principal.

Referencias técnicas: [Pipeline y prevención de fuga](https://scikit-learn.org/stable/common_pitfalls.html), [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [evaluación de modelos](https://scikit-learn.org/stable/modules/model_evaluation.html). Operación: [manual del laboratorio](../../docs/manuales/LABORATORIO_IA_LOCAL.md).
