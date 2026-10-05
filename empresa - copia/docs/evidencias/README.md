# Índice de evidencias

Organizado el 04/10/2026 sin mover ni reemplazar los archivos originales. Las fechas identifican comprobaciones registradas, no pruebas ejecutadas otra vez al crear este índice. [Entrega y límites](../ENTREGA_DEMO.md).

## Prueba integral local — 04/10/2026

| Evidencia | Qué acredita | Límite |
|---|---|---|
| [Reporte integral](2026-10-04/prueba-e2e.md) | Flujo autenticado, persistencia, reintentos, filtros, OpenAI/Search, ML y proveedores financieros; acceso anónimo rechazado | Muestra ficticia local; no aprobación empresarial ni carga/producción |
| Captura local `2026-10-04/dashboard.jpg` (no publicada) | Vista de la muestra web de 7 evaluaciones | Foto del momento, no actualización Power BI |
| Captura local `2026-10-04/azure-ml.jpg` (no publicada) | Clase remota mostrada en la interfaz | Conserva el aviso visual incorrecto detectado originalmente |
| Captura local `2026-10-04/azure-ml-estado-corregido.jpg` (no publicada) | Éxito del último intento de esa sesión y clase visible tras la corrección | No verifica versión del modelo ni disponibilidad permanente |
| [QA: corrección y suites](../QA.md#corrección-del-aviso-azure-ml--4-de-octubre-de-2026) | 42 pruebas frontend, lint, build, aplicación de la imagen y datos conservados | Pruebas aisladas separadas de la consulta real; no nueva CI remota |

No se guardaron capturas adicionales de cada pantalla. OpenAI, búsqueda documental y proveedores tienen el registro de observación del reporte integral; no se inventan archivos de evidencia inexistentes.

Seguimiento: [cierre técnico y marca NexoCredit](2026-10-04/cierre-tecnico.md), con suites 69/48, respaldo/restauración aislada y lectura independiente de metadatos ML. Las capturas y archivos privados se conservan localmente, no en el repositorio público.

[CI remota del cierre](2026-10-04/github-actions.md): ejecución 37247212787, commit de código 19223ae, ambos trabajos aprobados y conteos 69/48 comprobados en logs.

## Comprobaciones anteriores conservadas

| Fecha | Fuente | Alcance verificado |
|---|---|---|
| 30/09/2026 | [Manual y pruebas Power BI](../../analitica/reportes_power_bi/README.md) y [QA Desktop](../QA.md#power-bi-desktop-local--30-de-septiembre-de-2026) | Dashboard local guardado; 11 visuales; 96 comparaciones SQL–DAX; muestra de 5 evaluaciones |
| 26/09/2026 UTC | [Evaluación UCI](../../inteligencia_artificial/prediccion_azure_ml/evaluacion/README.md) y [métricas JSON](../../inteligencia_artificial/prediccion_azure_ml/evaluacion/resultados/20260926T032027806Z/evaluacion.json) | Artefacto académico y métricas locales, no identidad del endpoint remoto ni aptitud crediticia |
| 23/09/2026 | [QA GitHub Actions](../QA.md#github-actions--23-de-septiembre-de-2026) | Registro de ejecución 35911875318 del commit d3cd93d, no los cambios locales actuales |
| 03/10/2026 | [QA financiero y recuperación](../QA.md#apis-financieras-y-recuperación-de-arranque--03-de-octubre-de-2026) | Incidente de PostgreSQL y token Banxico rechazado entonces; el resultado financiero posterior está en el reporte del 04/10/2026 |

El workflow existente se encuentra en [.github/workflows/ci.yml de la raíz Git exterior](../../../.github/workflows/ci.yml). Su existencia no acredita una nueva ejecución.

## Pendientes sin evidencia de cierre

Comparación binaria del modelo remoto, recuperación productiva completa, pruebas de carga, aceptación, capacitación y ceremonias Scrum. CI del commit de código, lectura de metadatos ML y ensayo aislado de respaldo ya comprobados. Estado y criterios en [BACKLOG_CIERRE.md](../../gestion_proyecto/scrum/BACKLOG_CIERRE.md).

No incluir secretos, expedientes reales ni copias de cachés o sesiones al compartir estas evidencias.
