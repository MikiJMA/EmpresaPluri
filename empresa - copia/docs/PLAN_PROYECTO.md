# Plan del proyecto — borrador para revisión con asesores

## Identificación

Título: Proyecto de Desarrollo de un Sistema Inteligente de Análisis de Riesgo Crediticio.
Empresa: PluriOne S.A. de C.V. Nombre comercial: Develop Talent & Technology.
Dirección: Puebla 46, Colonia Roma Norte, Alcaldía Cuauhtémoc, C.P. 06700, Ciudad de México.
RFC: PLU060407HC9. Representante legal: Xochicuahuitl Gleason Juárez.
Sector privado, mediana empresa; consultoría, desarrollo de software y capacitación TI.
Contacto: 55 1900 3503; contacto@develop.com.mx. Horario: lunes a viernes, 09:00–18:00.
Responsable de estadías y asesor externo: Juan Méndez Herrera.
Líder de proyecto y evaluaciones: Edgar Loheffelmman.
Alumno: Villegas Rodriguez Jose Julian, Ingeniería en sistemas computacionales, TESOEM. Duración: 500 horas.
Datos proporcionados por el alumno; no verificados externamente.

## Tecnologías obligatorias

Por indicación del alumno, deben utilizarse Python, FastAPI, React.js, Azure OpenAI Service, Azure Machine Learning, Azure AI Search, PostgreSQL, Power BI, Docker, GitHub Actions, Microsoft Entra ID, APIs financieras y Scrum. No son alternativas opcionales. Consultar ../REQUISITOS_TECNOLOGICOS.md para ubicación y estado; reservar una carpeta no acredita implementación.

## Objetivo y alcance

Desarrollar un sistema que analice información financiera y crediticia, presente indicadores explicables y apoye la revisión humana de solicitudes. Diseñar arquitectura, implementar y validar modelos de scoring y predicción, y entregar documentación y soporte.

Se esperan beneficios en consistencia de evaluación y seguimiento del riesgo; la reducción del incumplimiento debe medirse en una implementación real y no se presume demostrada.

El alcance final incluye historial crediticio, pagos, ingresos, endeudamiento y variables económicas. El prototipo actual solo recibe RFC, ingresos, gastos y score capturado. Las reglas existentes son una referencia educativa, no una política aprobada por PluriOne.

## Requerimientos iniciales

| ID | Requerimiento | Criterio de aceptación | Estado |
|---|---|---|---|
| RF01 | Capturar y validar escenario | Rechazar ingresos no positivos, gastos negativos, identificador vacío y score fuera de escala demo | Implementado |
| RF02 | Explicar evaluación | Mostrar margen, regla y versión | Implementado con reglas demo |
| RF03 | Guardar solicitudes y evaluaciones | Consultar historial persistente con fecha y versión, sin duplicar solicitudes por reintento | Implementado localmente en PostgreSQL; reintentos con Idempotency-Key |
| RF04 | Analizar pagos y deuda | Diccionario de variables y validaciones acordadas con asesor | Pendiente |
| RF05 | Predecir incumplimiento | Modelo entrenado, comparación con baseline y reporte de validación | Pendiente |
| RF06 | Dashboard y alertas | Filtros por fecha/riesgo, métricas conciliadas y alertas trazables | Pendiente |
| RF07 | Revisión humana | Registrar dictamen, responsable y motivo sin sustituirlo por salida de IA | Pendiente |
| RF08 | Roles y auditoría | Analista y administrador con permisos comprobados y acceso auditado | Pendiente |
| RF09 | Integraciones | Contratos de API, autorización de datos y manejo de indisponibilidad | Pendiente |

Requerimientos no funcionales propuestos: secretos fuera del código; acceso restringido; cifrado en tránsito en despliegue; no registrar RFC o expedientes completos en logs; restauración comprobada de respaldo; validación de entradas en servidor; pruebas de rendimiento con volumen acordado. Los objetivos numéricos de latencia, concurrencia y recuperación se fijarán con el asesor.

## Propuesta técnica y arquitectura objetivo

React → FastAPI → PostgreSQL. FastAPI consulta un modelo versionado desplegado desde Azure Machine Learning. Microsoft Entra ID autentica usuarios y la API valida token, audiencia, emisor y roles. Azure AI Search recupera documentos autorizados de políticas internas; Azure OpenAI Service puede redactar explicaciones basadas en resultados y políticas citadas. Las explicaciones no alteran el score ni ejecutan decisiones.

Power BI consume vistas de información agregada con permisos. Los adaptadores de APIs financieras normalizan fuentes contratadas. Docker facilita ejecución reproducible; GitHub Actions ejecuta validación y empaquetado sin secretos en el repositorio.

Entidades propuestas: solicitante, solicitud, observación financiera, historial de pagos, evaluación, versión de modelo, alerta, revisión humana y evento de auditoría. Cada evaluación conserva versión, fecha de corte, variables utilizadas y factores explicativos. Definir retención y eliminación antes de almacenar datos reales.

Estado actual: React llama POST /api/v1/evaluar de FastAPI. GET / informa salud. /docs expone OpenAPI. PostgreSQL guarda las entradas y el resultado con fecha, versión e ID; GET /api/v1/evaluaciones consulta el historial y GET /api/v1/evaluaciones/{id} devuelve el detalle. La interfaz conserva el historial al recargar. Sin configuración se permite una evaluación identificada expresamente como no guardada. infraestructura/contenedores_docker/docker-compose.yml ejecuta frontend, backend, PostgreSQL y migraciones; se verificaron guardado e historial mediante navegador y persistencia tras reiniciar la base. El despliegue productivo permanece pendiente.

## Estrategia de modelos

1. Acordar con el asesor la definición de incumplimiento, horizonte y fecha de observación.
2. Obtener un conjunto autorizado con variables disponibles al momento de la solicitud y resultados observados posteriormente. Datos sintéticos sirven para integración, no para demostrar precisión real.
3. Crear diccionario, controles de faltantes, duplicados, calidad, procedencia y acceso. RFC es identificador; excluirlo de las variables predictivas.
4. Separar entrenamiento/validación/prueba por tiempo y evitar que un cliente aparezca indebidamente en distintos conjuntos. Preprocesar usando solo entrenamiento.
5. Comparar baseline interpretable con modelos candidatos. Reportar discriminación, calibración, falsos positivos/negativos y resultados por segmentos, con tamaño de muestra y limitaciones.
6. Seleccionar umbrales con costo de errores y políticas acordadas. No inventar umbrales productivos ni presentar score como probabilidad sin calibración.
7. Registrar versión y monitorear cambios en datos y desempeño. Mantener revisión humana y mecanismo de reversión.

## Cronograma propuesto de 500 horas

Bloques secuenciales orientativos. Fechas pendientes de inicio y disponibilidad del alumno; el horario de la empresa no equivale a horas efectivas de estadía.

| Actividad | Horas | Horas acumuladas | Entregable / condición de salida |
|---|---:|---:|---|
| 1. Detección de necesidades | 40 | 40 | Requerimientos revisados, fuentes identificadas |
| 2. Propuesta y negociación | 25 | 65 | Propuesta técnica y alcance acordado |
| 3. Arquitectura | 45 | 110 | Componentes, datos, APIs y controles documentados |
| 4. Planificación | 25 | 135 | Backlog priorizado, responsables y calendario |
| 5. Desarrollo | 200 | 335 | Backend 50, frontend 45, IA 65 e integraciones 40 |
| 6. QA | 60 | 395 | Evidencias funcionales, modelo, seguridad y carga |
| 7. Documentación | 35 | 430 | Manual técnico y de usuario reproducibles |
| 8. Mantenimiento | 20 | 450 | Plan de soporte, respaldo y recuperación |
| 9. Capacitación | 25 | 475 | Material, práctica y acta con asistentes reales |
| 10. Cierre | 25 | 500 | Resultados, pendientes y aceptación documentada |

Scrum: iteraciones de dos semanas ajustadas al calendario acordado; planificación, seguimiento breve, revisión con demostración y retrospectiva. No se asignan responsabilidades empresariales adicionales sin acuerdo.

## Backlog en orden de implementación

1. Base local operativa y validada: entrada de React, formulario, errores y API demo.
2. PostgreSQL con migraciones, solicitudes, evaluaciones e historial; pruebas de persistencia.
3. Roles con Entra ID y auditoría antes de habilitar datos reales.
4. Dataset autorizado, pipeline reproducible, baseline y evaluación temporal.
5. Endpoint del modelo versionado, dashboard, alertas y registro de revisión.
6. Integración financiera y económica con procedencia y fecha de actualización.
7. Azure AI Search y Azure OpenAI para consultar políticas y explicar resultados citados.
8. Power BI, contenedores y CI; pruebas de restauración, seguridad y carga.
9. Capacitación, piloto y cierre con evidencias.

## Dependencias a resolver

Fecha de inicio y distribución semanal de 500 horas; políticas crediticias; usuarios/roles; disponibilidad y permiso de uso de históricos; definición de incumplimiento; presupuesto y suscripción Azure; tenant Entra; proveedor de APIs; licencias Power BI; entorno de despliegue; objetivos medibles aceptados por los asesores.

## Cierre y evidencias

Cada entrega debe tener versión, fecha, autor, revisión y evidencia. Este plan no constituye aprobación de los asesores. El reporte final debe comparar objetivos con resultados medidos, listar limitaciones y pendientes, adjuntar pruebas y lecciones aprendidas, y registrar aceptación real. No completar actas, firmas, métricas o capacitación que no hayan ocurrido.
