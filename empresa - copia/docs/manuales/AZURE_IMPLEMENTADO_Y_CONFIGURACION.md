# Azure implementado y configuración de llaves

Actualización documental: 12/10/2026. NexoCredit **sí implementó las integraciones Azure en la demostración**. Las alternativas locales son adicionales para continuar trabajando cuando no se disponga de suscripción; no eliminan Azure del código, los requisitos ni la documentación.

## Qué se implementó y comprobó

| Tecnología | Implementación en la demo | Evidencia registrada |
|---|---|---|
| Azure OpenAI Service | Cliente backend, generación automática de explicación después del guardado, referencia a la guía DEM-02 y tratamiento de errores; sin enviar RFC ni modificar el riesgo | Consulta real autenticada con `gpt-5-mini-1` el 04/10/2026 |
| Azure AI Search | Catálogo de dos guías / 14 secciones, búsqueda textual y recuperación documental para la explicación | Catálogo y búsqueda real autenticada el 04/10/2026 |
| Azure Machine Learning | Entrenamiento/evaluación académica UCI, registro del candidato, adaptador remoto y formulario separado de 19 entradas NTD | Predicción real autenticada y lectura independiente del modelo registrado servido `plurione-uci-voting-candidato:1` el 04/10/2026 |
| Microsoft Entra ID | Inicio Microsoft con MSAL y validación de identidad/ámbito/roles en FastAPI; rutas de negocio protegidas | Sesión real y rechazo de consultas sin token el 04/10/2026 |

Fuentes del proyecto: [prueba integral autenticada](../evidencias/2026-10-04/prueba-e2e.md), [metadatos y cierre técnico](../evidencias/2026-10-04/cierre-tecnico.md) y [requisitos tecnológicos](../../REQUISITOS_TECNOLOGICOS.md). No se trata únicamente de carpetas preparadas. Estas evidencias tienen fecha: no acreditan que la suscripción siga vigente, disponibilidad cloud actual, validación crediticia o producción.

## Dónde se colocan las keys

Para la aplicación que funciona con Docker, edita **solo el archivo privado**:

```text
infraestructura/contenedores_docker/.env
```

Desde la carpeta interior, el acceso [Editar configuración privada](<../../operacion/integraciones/Editar configuracion privada.cmd>) lo abre en un editor, sin tener que pegar llaves en la terminal. También puede abrirse en VS Code. Los nueve campos Azure ya están presentes; no es necesario crear otro archivo ni borrar valores existentes.

La [plantilla pública Docker](../../infraestructura/contenedores_docker/.env.example) conserva los mismos nombres con valores vacíos. Sirve de referencia, **no para guardar las llaves reales**. No copies toda la plantilla encima del `.env`: perderías configuración y contraseñas de la base existente.

Este bloque muestra los espacios que debes completar en el archivo privado, a la derecha de `=`:

```dotenv
# Azure OpenAI: dirección Responses, implementación y llave de su recurso.
AZURE_OPENAI_RESPONSES_URL=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_KEY=

# Azure AI Search: dirección del servicio, índice y llave de consulta.
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_INDEX_NAME=
AZURE_SEARCH_QUERY_KEY=

# Azure Machine Learning: endpoint de inferencia, modelo y llave del endpoint.
AZURE_ML_SCORING_URI=
AZURE_ML_MODEL_ID=
AZURE_ML_API_KEY=
```

| Campo | Qué poner |
|---|---|
| `AZURE_OPENAI_RESPONSES_URL` | URL completa de Responses del recurso implementado |
| `AZURE_OPENAI_DEPLOYMENT` | Nombre exacto de su implementación, no necesariamente el nombre genérico del modelo |
| `AZURE_OPENAI_API_KEY` | Solo el valor de la llave privada de ese recurso |
| `AZURE_SEARCH_ENDPOINT` | Dirección del servicio Search de las guías demo |
| `AZURE_SEARCH_INDEX_NAME` | Nombre del índice de esas guías |
| `AZURE_SEARCH_QUERY_KEY` | Llave de consulta, no administrativa |
| `AZURE_ML_SCORING_URI` | URL HTTPS del endpoint de inferencia compatible con el adaptador |
| `AZURE_ML_MODEL_ID` | Identificador del modelo que sirve el despliegue; no inventar la versión |
| `AZURE_ML_API_KEY` | Solo el valor de la llave privada del endpoint ML |

No escribas nombres de encabezado como `api-key:` ni prefijos `Bearer` junto a las llaves. Los adaptadores actuales corresponden a los recursos/contratos implementados: OpenAI y Search comprueban la dirección/implementación/índice esperados. Crear otro recurso o cambiar de contrato requiere revisar el adaptador; no se garantiza que cualquier URL funcione por editarla aquí.

Para desarrollo **sin Docker**, la [plantilla backend](../../backend/.env.example) conserva los campos equivalentes; `scripts/iniciar-backend.ps1` utiliza `backend/.env.postgresql`. Docker no lee ese archivo. No dupliques las llaves entre entornos si no los utilizas.

Microsoft Entra ID mantiene su configuración de cliente/tenant/ámbitos existente. Los identificadores públicos de MSAL no son keys de Azure OpenAI, Search o ML. No se añade un `client_secret` al navegador ni a `VITE_*`.

## Activar Azure cuando se necesite

Con recursos/credenciales vigentes y Docker Desktop abierto, el acceso [Activar modo Azure](<../../operacion/integraciones/Activar modo Azure.cmd>) selecciona:

```dotenv
EXPLICACIONES_PROVEEDOR=azure
DOCUMENTOS_PROVEEDOR=azure
ML_PROVEEDOR=azure
```

El lanzador conserva las llaves y cuentas existentes; aplica el cambio al backend sin borrar el volumen PostgreSQL. No verifica por sí solo conectividad ni hace una predicción/generación de pago. Después, recarga la aplicación y entra con tu cuenta. Las nuevas consultas Azure pueden generar consumo; iniciar sesión local no obliga a usar IA local.

Los proveedores también se pueden seleccionar por función. Por ejemplo, `ML_PROVEEDOR=local` mantiene la IA predictiva local sin eliminar los campos `AZURE_ML_*`. El modo local no usa esas llaves para inferencia ni cambia automáticamente a Azure ante un fallo. Seleccionar un modo local no cancela suscripciones o recursos cloud.

**Esta actualización documental no activa Azure**: conserva la configuración local vigente y las credenciales que ya estaban guardadas.

## Protección de las llaves

El `.env` está excluido de Git y de las imágenes; Docker entrega su configuración al backend. No está cifrado en disco y administradores del equipo pueden leerlo. No publiques, adjuntes o fotografíes el archivo, ni pegues llaves en el chat. No las coloques en frontend, `public/`, `VITE_*`, PRD, MVP o evidencias. La plantilla y esta guía permanecen sin secretos.

Si se comparte la documentación, incluir esta guía y `.env.example`, nunca el `.env` privado. Si una llave se expone, rotarla en el proveedor y actualizarla localmente; no basta con borrarla de un texto ya compartido.

Ver también [acceso local, proveedores y llaves](ACCESO_LOCAL_Y_PROVEEDORES.md) y [laboratorio IA local](LABORATORIO_IA_LOCAL.md).
