# Tecnologías obligatorias del proyecto

Por indicación del alumno, el sistema final debe utilizar todas las tecnologías siguientes. Este requisito sustituye la interpretación anterior de que eran opcionales. Crear una carpeta no significa que su integración esté implementada.

| Tecnología | Función y ubicación | Estado actual |
|---|---|---|
| Python | Lógica del servidor en backend/app | Implementado |
| FastAPI | API HTTP en backend/app/rutas_api | Implementado |
| React.js | Interfaz en frontend/src | Implementado |
| Azure OpenAI Service | Explicaciones en backend/app/integraciones/explicaciones_azure_openai | Pendiente |
| Azure Machine Learning | Entrenamiento y evaluación en inteligencia_artificial/prediccion_azure_ml; consumo en backend/app/integraciones/prediccion_azure_ml | Pendiente |
| Azure AI Search | Recuperación de políticas en backend/app/integraciones/busqueda_azure_ai_search | Pendiente |
| PostgreSQL | Persistencia en backend/app/persistencia_postgresql | Implementado localmente: evaluaciones e historial; pruebas reales aprobadas |
| Power BI | Reportes en analitica/reportes_power_bi | Pendiente |
| Docker | Contenedores en infraestructura/contenedores_docker | Implementado y probado localmente: React/Nginx, FastAPI, PostgreSQL y migraciones con Compose |
| GitHub Actions | Automatización en .github/workflows/ci.yml de la raíz Git (carpeta exterior) | Implementado: backend/PostgreSQL y frontend aprobados en GitHub, ejecución 35911875318 |
| Microsoft Entra ID | Identidad y roles en backend/app/autenticacion_entra_id | Pendiente |
| APIs financieras | Consulta de fuentes en backend/app/integraciones/datos_financieros | Pendiente |
| Scrum | Planificación y seguimiento en gestion_proyecto/scrum | Propuesta; ejecución por documentar |

Las carpetas pendientes contienen instrucciones de responsabilidad y criterios de finalización, no servicios simulados ni conexiones activas.
