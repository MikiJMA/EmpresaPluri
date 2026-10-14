# Adaptador de inferencia académica local

`cliente_local.py` sirve el modelo numérico `nexocredit-uci-logistica-v1`, entrenado con scikit-learn. No carga el pickle AutoML histórico, no llama a Azure/Ollama, no almacena consultas ni modifica evaluaciones. El selector `ML_PROVEEDOR=local` es explícito; valores Azure/deshabilitado siguen disponibles.

## Contrato y protección

`GET /api/v1/ml/estado` y `POST /api/v1/ml/predecir`, con cuerpo `{"valores": {…19 enteros UCI…}}`, requieren `usuario_actual`. Los alias `/api/v1/azure-ml/*` comparten manejadores y proveedor. Rutas registradas en `main.py`; selección en `../proveedores.py`; validación HTTP en `../../rutas_api/azure_ml.py`.

El cliente vuelve a comprobar tipo/claves/límites de las entradas para sus llamadas internas. Se rechazan campos adicionales, booleanos, cadenas, fracciones, límites no positivos, pagos negativos o códigos PAY fuera de −2…9. Los saldos sí admiten negativos.

Antes de inferir se comprueban: archivo fijo no symlink, tamaño máximo 65.536 bytes, SHA-256 fijado, esquema numérico de 19 variables, orden/clases, vectores finitos/escalas positivas y métricas coherentes con filas/matriz. No hay carga `pickle`/`joblib` ni rutas de artefactos enviadas por el cliente. La inferencia se ejecuta en el threadpool del servidor; no bloquea el bucle async con una llamada cloud.

Respuesta: booleano `incumplimiento_predicho`, `proveedor=local`, `origen=scikit-learn local`, ID/huella/algoritmo, métricas de prueba, nombres de variables fuera del rango observado y advertencia académica. No devuelve entradas, identidad, score, probabilidad o aprobación. El estado `configurado=true` acredita artefacto verificado, no una consulta realizada ni validez crediticia.

Archivo ausente, sustituido o inválido: estado no configurado / predicción 503 saneada, sin fallback. Entrada inválida: 422. Sin sesión: 401. La comprobación de hash protege de sustituciones accidentales, no de un administrador que pueda alterar artefacto y código simultáneamente.

## Empaquetado y pruebas

Docker incorpora los dos JSON públicos académicos con el código backend; las dependencias scikit-learn ya existían para entrenamiento. La ejecución numérica no requiere el entorno AutoML ni nuevos paquetes/llaves. No hay nueva migración de base de datos.

`backend/tests/test_ml_local.py` cubre artefacto/métricas, ambas clases, ausencia de HTTP/deserialización/guardado, autenticación, alias, entradas inválidas, extrapolación, alteración/ausencia, desactivado y conservación de Azure. Los casos con identidad inyectada prueban el contrato autorizado, no un inicio de sesión humano; las pruebas de autenticación local y Entra se mantienen separadas.

Entrenamiento/procedencia: [README de IA local](../../../../inteligencia_artificial/prediccion_local/README.md). Operación: [manual](../../../../docs/manuales/LABORATORIO_IA_LOCAL.md).
