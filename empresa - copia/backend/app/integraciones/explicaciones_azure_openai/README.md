# Explicaciones — Azure OpenAI Service

Función: explicar resultados guardados de `reglas-demo-v1` usando la guía demo recuperada de Azure AI Search. No son políticas oficiales.
Estado: cliente, ruta autenticada y configurador implementados; respuesta real confirmada por el usuario con `gpt-5-mini-1` y guía DEM-02. La interfaz inicia la explicación automáticamente después de guardar una evaluación.

Comprobación autenticada del 04/10/2026: guardado ficticio, explicación automática y referencia DEM-02 v1.0 observados en la aplicación. Evidencia en [prueba integral](../../../../docs/evidencias/2026-10-04/prueba-e2e.md). No certifica todas las respuestas futuras ni una política empresarial.

Configuración Docker: ejecutar `Conectar Azure OpenAI.cmd` en la carpeta interior, con Docker Desktop abierto. Introducir la clave del recurso `julianvillegas191-9159-resource`, donde existe `gpt-5-mini-1`. Entrada oculta; el archivo privado `.env` queda sin cifrar en disco y excluido de Git. El script conserva PostgreSQL, ML y Search; recrea únicamente backend y reinicia frontend. No realiza una llamada de pago.

Prueba manual: iniciar sesión y pulsar **Evaluar escenario** con datos ficticios. Al confirmar el guardado, aparece **Generando explicación con IA…** y después el texto, sin otro botón. El formulario avisa del envío y del consumo antes de evaluar. Si no se guarda, no se solicita IA; un error de generación no modifica el guardado ni el riesgo. No hay reintentos automáticos. Cada nueva evaluación puede generar consumo.

La pantalla conserva una promesa por UUID mientras está abierta: una evaluación repetida con la misma clave no provoca otra llamada, aunque la respuesta haya fallado. El render, las actualizaciones del dashboard y React StrictMode no disparan generación. Al editar o evaluar otro escenario se oculta la explicación anterior; las respuestas tardías no se muestran en un resultado diferente. La caché es solo en memoria de esa pantalla, no entre pestañas ni después de recargar/cerrar sesión; no constituye deduplicación global del servidor.

POST `/api/v1/evaluaciones/{UUID}/explicacion` carga el registro del servidor; ignora datos o riesgo enviados por el cliente. No envía RFC, identidad, revisiones ni UUID al modelo. No modifica ni persiste una decisión. La explicación solo queda en memoria de la interfaz.

Responses usa el endpoint preview proporcionado por el usuario, `store=false`, límite de 2000 tokens de salida (incluido razonamiento), timeout de 60 segundos y ninguna herramienta ni reintento automático. `store=false` no constituye una garantía de retención cero del proveedor. Se valida respuesta completa, formato JSON y referencia a la guía DEM-02. El texto libre puede contener errores: requiere revisión humana. Dos solicitudes simultáneas por proceso como máximo; no es un sistema de cuotas de producción.

Referencias del contrato: [Azure Responses](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses) y [OpenAI Docs: razonamiento](https://developers.openai.com/api/docs/guides/reasoning). Pruebas simuladas no acreditan acceso real, saldo ni disponibilidad del despliegue. No se ha creado otro recurso cloud.
