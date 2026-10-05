# Consulta de predicciones — Azure Machine Learning

Función: consumir desde el backend el modelo versionado publicado en Azure ML.
Estado: cliente remoto y formulario UCI conectados al endpoint Azure existente. Consulta real desde la interfaz autenticada comprobada el 4 de octubre de 2026, además de las pruebas con respuestas simuladas. La etiqueta configurada no acredita la identidad remota. Una lectura independiente en Azure ML Studio comprobó ese día el modelo registrado servido `plurione-uci-voting-candidato:1`, endpoint/despliegue Correcto y tráfico directo 100 %. La comparación binaria con el artefacto local sigue pendiente. No cargar model.pkl en el backend. Evidencias: [prueba integral](../../../../docs/evidencias/2026-10-04/prueba-e2e.md) y [seguimiento técnico](../../../../docs/evidencias/2026-10-04/cierre-tecnico.md).

El entrenamiento pertenece a inteligencia_artificial/prediccion_azure_ml.
## Configuración y contrato

Exportar en el entorno del proceso backend AZURE_ML_SCORING_URI (HTTPS terminado en .inference.ml.azure.com/score), AZURE_ML_API_KEY y AZURE_ML_MODEL_ID (por ejemplo plurione-uci-voting-candidato:1, solo cuando corresponda al despliegue real). El archivo .env.example es una plantilla: no se carga automáticamente. Nunca usar variables VITE_* para claves. Docker recibe estas variables desde su entorno o archivo --env-file privado. Reiniciar/recrear el backend tras configurar.

GET /api/v1/azure-ml/estado solo comprueba configuración, no conectividad. POST /api/v1/azure-ml/predecir acepta {"valores": { ...19 columnas... }}. Todas son enteros obligatorios; no acepta campos adicionales. Envía input_data con columns, index y data, en el orden del artefacto. Acepta únicamente una clase booleana, como [true] o {"predictions":[true]}; cualquier otro contrato falla explícitamente. No calcula probabilidades a partir de clases.

Referencia de contrato: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models?view=azureml-api-2

No hay reintentos automáticos ni persistencia de escenarios. Timeout de Azure: 30 segundos. Errores/configuración: 503, respuesta inválida/fallo remoto: 502, timeout: 504. Las claves y respuestas de error remotas no se devuelven al navegador. modelo_configurado es una etiqueta administrativa, no una identidad verificada por el servicio; antes de activar comprobar qué versión sirve el despliegue.

## Estado de conexión en la interfaz

El aviso inicial solo refleja configuración. Mientras se consulta muestra espera; tras una respuesta válida informa que la conexión fue comprobada en esa sesión. Un intento fallido posterior sustituye el éxito y elimina la predicción anterior. No es una comprobación continua: editar campos limpia el resultado, pero conserva el estado histórico del último intento; recargar restaura el aviso inicial. El endpoint GET de estado sigue sin efectuar una llamada externa ni afirmar conectividad verificada.

## Pendiente para producción

Comparar el binario remoto con el artefacto original y conciliar predicciones de entradas ficticias; la lectura puntual de metadatos no sustituye esa prueba ni una verificación continua. El proxy exige sesión Microsoft Entra ID y rol Analista o Administrador; aún faltan límites de consumo por usuario y controles operativos de producción. Mantener acceso local y no publicar este proxy sin completar esos controles. El modelo UCI es académico, no está validado para decisiones de crédito real. El formulario UCI no convierte MXN a NTD ni reutiliza las entradas del formulario crediticio. Las reglas demo se conservan separadas.
