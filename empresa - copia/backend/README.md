# Backend

FastAPI y reglas de evaluación. Ejecutar desde la raíz de empresa:

```powershell
.\scripts\iniciar-backend.ps1
```

- app/main.py: crea y configura FastAPI.
- app/rutas_api/routes.py: define los endpoints.
- app/validacion_datos/credito.py: valida las entradas.
- app/evaluacion_crediticia/scoring.py: calcula el resultado demo.
- tests/: pruebas de API y reglas.
- requirements.txt: dependencias de Python.
- app/persistencia_postgresql/: conexión, repositorio y migraciones PostgreSQL.
- app/autenticacion_entra_id/: validación de acceso delegado Microsoft, ámbito y roles; fija identidad de nuevas revisiones.
- app/integraciones/: clientes Azure OpenAI, Azure ML, Azure AI Search y APIs financieras, separados por función.
- .env.postgresql: configuración privada de persistencia cargada automáticamente.
- .env: archivo local conservado de la ubicación anterior; no se carga automáticamente. Las variables actuales se toman del entorno del proceso.

El entorno virtual compartido está en ../.venv. Consultar ../README.md para instalación.

Estado documentado al 04/10/2026: 57 pruebas backend/PostgreSQL aprobadas y consultas externas reales comprobadas en la demo autenticada. Ver [QA](../docs/QA.md). Las respuestas simuladas de los tests no certifican disponibilidad cloud ni aptitud del modelo para crédito real. La configuración Entra actual retorna a localhost:8080; no hay acceso público a rutas de negocio sin token.

Comprobación posterior al cambio de marca, 04/10/2026 (hora de México): 69 pruebas backend aprobadas con PostgreSQL temporal aislado mediante `scripts/probar-programacion.ps1`, sin omisiones. La API y los mensajes de acceso presentan NexoCredit; los identificadores públicos Entra, roles, ámbito y retorno autorizado se conservan. Se reconstruyeron únicamente backend y frontend de la demo; PostgreSQL no se recreó. Publicación posterior autorizada en rama de revisión: [CI remota](../docs/evidencias/2026-10-04/github-actions.md) aprobada para el commit de código 19223ae, 69 pruebas sin omisiones, migraciones repetibles y lanzadores PowerShell.
