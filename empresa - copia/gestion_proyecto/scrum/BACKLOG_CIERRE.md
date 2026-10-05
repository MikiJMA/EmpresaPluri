# Backlog de cierre y trazabilidad

Corte: 04/10/2026. Inventario del estado observado y propuesta de trabajo siguiente; no es un sprint ejecutado, acta de reunión ni aceptación del asesor. Prioridades propuestas, responsables y fechas objetivo por acordar. No se atribuyen horas ni ceremonias retrospectivamente.

## Incrementos con evidencia técnica

| ID | Incremento demostrado | Evidencia | Alcance |
|---|---|---|---|
| D01 | React, FastAPI, PostgreSQL y Docker: captura, persistencia, historial, reintentos y filtros | [Prueba integral](../../docs/evidencias/2026-10-04/prueba-e2e.md) | RF01/RF03 y parte de RF04/RF06; reglas demo |
| D02 | Acceso Entra y responsable autenticado de revisiones | [QA](../../docs/QA.md) y [contrato Entra](../../backend/app/autenticacion_entra_id/README.md) | RF07 y parte de RF08; no auditoría completa |
| D03 | Explicación automática OpenAI con guía Search; catálogo/búsqueda | [Prueba integral](../../docs/evidencias/2026-10-04/prueba-e2e.md) | RF02 y parte de RF09; guías académicas, no políticas oficiales |
| D04 | Candidato UCI evaluado y laboratorio ML remoto con aviso corregido | [Evaluación local](../../inteligencia_artificial/prediccion_azure_ml/evaluacion/README.md) y [seguimiento técnico](../../docs/evidencias/2026-10-04/cierre-tecnico.md) | Parte de RF05; metadatos modelo:1/tráfico 100 % verificados; comparación binaria y aptitud crediticia pendientes |
| D05 | Indicadores públicos Banxico/Banco Mundial | [Prueba integral](../../docs/evidencias/2026-10-04/prueba-e2e.md) | Parte de RF09; no historial crediticio privado |
| D06 | Power BI Desktop, filtros y conciliación SQL–DAX | [Manual Power BI](../../analitica/reportes_power_bi/README.md) | Parte de RF06; sin alertas ni publicación |
| D07 | Workflow CI y nueva ejecución remota aprobada | [CI del cierre](../../docs/evidencias/2026-10-04/github-actions.md) | Commit de código 19223ae; 69 backend/48 frontend, migraciones, lanzadores, audit, lint y build aprobados; sin despliegue |

«Demostrado» significa evidencia técnica local/histórica, no historia aceptada en un sprint ni requisito completo del sistema final.

## Pendientes para cierre de la demostración

| ID / prioridad propuesta | Trabajo | Estado | Condición de cierre |
|---|---|---|---|
| C01 / alta | Actualizar manuales y organizar entrega | Preparado para revisión documental | Enlaces y coherencia comprobados; observaciones del asesor registradas posteriormente |
| C02 / alta | Validar código actual en GitHub Actions e incluir tests unitarios frontend | Cerrado técnicamente para commit de código 19223ae | [Ejecución 37247212787](../../docs/evidencias/2026-10-04/github-actions.md), ambos trabajos aprobados; unitarios frontend ejecutados; no acredita futuros cambios |
| C03 / alta | Verificar identidad del modelo remoto | Parcial: metadatos modelo:1 y tráfico 100 % verificados | [Lectura independiente](../../docs/evidencias/2026-10-04/cierre-tecnico.md) aprobada; comparación binaria con el artefacto local pendiente. No basta modelo_configurado |
| C04 / alta | Respaldo y ensayo de restauración | Cerrado técnicamente en demo local | [Ensayo aislado](../../docs/evidencias/2026-10-04/cierre-tecnico.md): tres tablas conciliadas sin sobrescribir la base de trabajo; no recuperación productiva completa |
| C05 / alta | Planificación, revisión y retrospectiva Scrum reales | Sin ejecución acreditada | Confirmar responsables, calendario y objetivo; registrar tareas y evidencias; documentar eventos después de realizarlos, sin inventar horas ni fechas |
| C06 / alta | Revisión final del alcance demo con asesor | Pendiente | Sesión real, participantes, hallazgos y aceptación o rechazo explícitos; nunca llenar una firma o conformidad por anticipado |
| C07 / media | Capacitación y manual revisado por usuario | Pendiente | Práctica ficticia real y registro de dudas/resultados; asistentes y horas confirmados |

No se asignan responsables empresariales ni presupuesto desde este documento. La preparación inicial no ejecutó estas tareas; el seguimiento técnico posterior registra lo realmente comprobado. No se acredita con ello un sprint aceptado.

## Sistema final: fuera del cierre técnico de la demo

Datos autorizados representativos y definición de incumplimiento; validación temporal, calibración y segmentos del modelo; análisis efectivo de pagos/deuda e historial crediticio privado; políticas oficiales; alertas trazables; permisos diferenciados según alcance, auditoría, cuotas, TLS del despliegue, retención, carga, monitoreo y recuperación. Ver [plan](../../docs/PLAN_PROYECTO.md). No marcar RF04/RF05/RF06/RF08/RF09 como completos por una conexión de demostración.

## Registro mínimo al iniciar un sprint real

Completar después del acuerdo: identificador y fechas, objetivo, responsables confirmados, historias elegidas de este backlog, capacidad real acordada, criterios de aceptación y evidencias. Durante el sprint registrar cambios y bloqueos. En revisión/retrospectiva registrar fecha real, participantes, resultados y acciones. Hasta entonces estos campos permanecen sin completar; las 500 horas del plan son una propuesta.
