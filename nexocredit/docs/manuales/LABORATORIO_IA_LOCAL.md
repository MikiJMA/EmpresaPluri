# Laboratorio de IA predictiva local

Actualizado: 12/10/2026. Alternativa adicional a Azure Machine Learning para continuar la demostración sin una suscripción Azure. No sustituye el requisito tecnológico original ni es un modelo aprobado para crédito real.

## Adenda de uso — segunda opinión principal — 15/10/2026

El mismo modelo puede consultarse opcionalmente en **«Segunda opinión IA (académica)»**, junto al resultado de una evaluación guardada. El [recorrido vigente de operación](OPERACION.md) explica cómo cargar el ejemplo UCI independiente, consultar explícitamente y distinguir la clase del modelo del riesgo por reglas. Son escenarios diferentes: no se convierten los datos MXN del solicitante a NTD ni se valida su riesgo con este experimento.

`POST /api/v1/evaluaciones/{identificador}/segunda-opinion` exige sesión, UUID existente y las mismas 19 entradas UCI estrictas. Devuelve riesgo/versión originales y modelo con `guardada: false`: no persiste la comparación ni recalcula v1/v2. Se mantienen el laboratorio separado, los límites UCI/Taiwán 2005 y Azure como proveedor explícito adicional; esta adenda no acredita una nueva consulta cloud ni modifica las métricas históricas siguientes.

## Cómo usarlo

1. Mantén Docker Desktop abierto y entra en `http://localhost:8080/`. Si la pantalla sigue mostrando el diseño anterior, recarga con `Ctrl+F5` y vuelve a iniciar sesión con tu propia cuenta.
2. Abre **Laboratorio IA**. Debe aparecer **IA local · scikit-learn** y el modelo `nexocredit-uci-logistica-v1`.
3. Pulsa **Cargar ejemplo ficticio**. Solo completa los 19 campos: no ejecuta el modelo ni guarda datos.
4. Pulsa **Consultar IA local**. La respuesta muestra la clase académica Incumplimiento / No incumplimiento, el origen y el modelo utilizado.
5. Abre **Métricas y límites del modelo local** para revisar los resultados de prueba. Al editar una entrada se retira el resultado anterior; hay que consultar de nuevo.

La inferencia se ejecuta en el backend local. No necesita llave ni Ollama, no llama a Azure y no cambia automáticamente a otro proveedor si falla. Ollama continúa ocupándose de las explicaciones: es una función diferente.

## Qué datos recibe

Se utilizan exclusivamente escenarios ficticios compatibles con el conjunto académico UCI de tarjetas de crédito de Taiwán, 2005. Los importes son **dólares taiwaneses (NTD), no MXN**. No se deben copiar ingresos, gastos, score, RFC, CURP o datos personales del formulario principal para completar estas variables.

| Variables | Significado y validación de captura |
|---|---|
| `LIMIT_BAL` | Límite de crédito; entero positivo |
| `PAY_0`, `PAY_2`…`PAY_6` | Estados de pago de septiembre a abril; códigos originales de −2 a 9, no días de atraso |
| `BILL_AMT1`…`BILL_AMT6` | Saldos de septiembre a abril; enteros, pueden ser negativos |
| `PAY_AMT1`…`PAY_AMT6` | Pagos de septiembre a abril; enteros no negativos |

La API exige exactamente esas 19 claves, sin campos adicionales ni valores vacíos, fraccionarios o booleanos. Los importes se acotan a enteros de 32 bits; este límite técnico no significa que cualquier cifra sea representativa. Si un valor supera los mínimos/máximos observados en el entrenamiento, se advierte la posible extrapolación, sin certificar su fiabilidad.

## Resultados y límites

El modelo es **StandardScaler + LogisticRegression**, entrenado con scikit-learn. El escalado y el ajuste usan solo 17.909 filas de entrenamiento; validación y prueba no se usan para ajustar parámetros. La clase positiva corresponde al incumplimiento del mes siguiente definido en UCI, no a un nivel Bajo/Medio/Alto de la aplicación.

En las 5.955 filas independientes de prueba:

| Métrica | Resultado |
|---|---:|
| AUC ROC | 0,7150 |
| Exactitud global | 70,28 % |
| Sensibilidad a incumplimiento | 60,92 % |
| Precisión entre positivos | 37,51 % |
| F1 positivo | 46,43 % |
| Exactitud de predecir siempre No incumplimiento | 78,86 % |

La exactitud del modelo es **menor** que la estrategia trivial, que no detecta ningún incumplimiento. El modelo encuentra 767 de los 1.259 positivos, omite 492 y produce 1.278 falsos positivos. No es evidencia de aptitud crediticia. Sus pesos balanceados, particiones agrupadas aleatorias (no temporales), antigüedad y población de origen impiden presentar la salida como una probabilidad calibrada o trasladarla directamente a México. Excluir sexo, educación, estado civil y edad tampoco demuestra ausencia de sesgo.

La consulta no guarda entradas/resultados en PostgreSQL, no genera planes ni autorizaciones y no modifica las reglas principales, el score capturado o el riesgo de evaluaciones existentes. Desde el 13/10/2026 las nuevas evaluaciones principales usan [reglas-demo-v2](REGLAS_RIESGO_DEMO.md), mientras que las anteriores v1 se conservan. Las métricas de este modelo **no son** las del candidato AutoML anterior; ambos tienen evidencias separadas.

## Configuración privada y alternativa Azure

El archivo privado sigue siendo `infraestructura/contenedores_docker/.env`, excluido de Git. Para este laboratorio basta:

```dotenv
ML_PROVEEDOR=local
```

No se introduce ninguna llave nueva. El lanzador **Activar modo local** ahora selecciona este modelo además de Ollama/documentos locales. Para aplicar cambios de configuración sin modificar PostgreSQL, ejecuta desde la carpeta interior:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\modo-local.ps1 -Accion local
```

Para usar solo el ML local con otros proveedores, edita únicamente `ML_PROVEEDOR` y utiliza **Actualizar NexoCredit**. No copies `.env.example` encima del archivo privado ni cambies contraseñas de la base existente. El lanzador de actualización reconstruye las imágenes; cambiar proveedores no elimina recursos ni cancela facturación Azure.

`ML_PROVEEDOR=azure` conserva el adaptador Azure, que necesita recursos/credenciales vigentes y puede generar consumo. `ML_PROVEEDOR=deshabilitado` bloquea la inferencia explícitamente. No existe un fallback automático a Azure ni una clasificación inventada ante fallos.

## Contrato y diagnóstico

Las rutas `GET /api/v1/ml/estado` y `POST /api/v1/ml/predecir` requieren una sesión autorizada local o Entra. Las rutas anteriores `/api/v1/azure-ml/estado` y `/predecir` son alias y respetan el proveedor seleccionado; su nombre histórico no indica que estén llamando a Azure.

El estado configurado confirma que el artefacto local está presente y su SHA-256 coincide; no afirma que esa sesión ya haya consultado el modelo. Un archivo ausente/alterado provoca estado no disponible y error 503 al consultar, sin filtrar rutas privadas o cambiar proveedor. Una captura inválida devuelve 422; una petición sin sesión, 401. No desactives autenticación para probarlo.

El modelo se incluye como JSON numérico pequeño, no como `pickle`/`joblib`. Para cambiarlo hay que entrenar, evaluar, revisar el nuevo artefacto, actualizar su versión/huella/contratos y volver a probar; no basta con reemplazar el archivo.

Referencias: [entrenamiento reproducible y procedencia](../../inteligencia_artificial/prediccion_local/README.md), [adaptador y contrato](../../backend/app/integraciones/prediccion_local/README.md), [evidencia fechada](../evidencias/2026-10-12/ia-predictiva-local.md), [acceso y llaves](ACCESO_LOCAL_Y_PROVEEDORES.md).
