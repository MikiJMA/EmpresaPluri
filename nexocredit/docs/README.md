# Documentación — NexoCredit

## Lectura recomendada

Corte de preparación del 14/10/2026: [verificación de entrega](evidencias/2026-10-14/entrega-demo.md). Distingue suites aisladas, consultas reales, resultados históricos y pendientes; el ZIP no incluye credenciales ni datos de trabajo.

1. [Entrega demo](entrega/ENTREGA_DEMO.md): alcance comprobado y pendientes.
2. [PRD](producto/PRD_NEXOCREDIT.md): requisitos y arquitectura.
3. [MVP](producto/MVP_NEXOCREDIT.md): MoSCoW y aceptación.
4. [Manual de operación](manuales/OPERACION.md): uso y soporte.
5. [QA](calidad/QA.md) e [índice de evidencias](evidencias/README.md): comprobaciones fechadas.
6. [Acceso local, Ollama y llaves](manuales/ACCESO_LOCAL_Y_PROVEEDORES.md): alternativa a Azure y ubicación de la configuración privada.
7. [Revisión de RFC/CURP](manuales/REVISION_RFC_CURP.md): formato y fecha, consulta SAT manual y límites de identidad.
8. [Correcciones de las pruebas de ruptura](evidencias/2026-10-11/correcciones-ruptura.md): validación, recuperación de interfaz, acceso/proxy, caché/cuotas de IA y pruebas de regresión.
9. [Seguimiento de créditos y pagos](manuales/SEGUIMIENTO_CREDITICIO.md): obligaciones ficticias, abonos, análisis, alertas y límites.
10. [Arquitectura y datos actuales](desarrollo/ARQUITECTURA_Y_DATOS.md): componentes, relaciones, doce tablas y API.
11. [Mantenimiento y soporte](manuales/MANTENIMIENTO_Y_SOPORTE.md), [material de práctica](entrega/CAPACITACION_DEMO.md) e [informe técnico actual](entrega/INFORME_TECNICO_ACTUAL.md).
12. [Laboratorio IA local](manuales/LABORATORIO_IA_LOCAL.md): alternativa scikit-learn adicional a Azure ML, operación, métricas y límites académicos.
13. [Azure implementado y configuración de keys](manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md): evidencias de integración, campos conservados, archivo privado y selección de proveedor.
14. [Score, margen e importes](manuales/REGLAS_RIESGO_DEMO.md): rangos v2, historial v1 conservado, redondeo visual y guías versionadas.

## Organización

| Carpeta | Contenido |
|---|---|
| producto | PRD y MVP separados |
| planificacion | [Plan del proyecto](planificacion/PLAN_PROYECTO.md) |
| manuales | Uso y mantenimiento local |
| calidad | Pruebas y resultados QA |
| entrega | Guion, alcance y condiciones de entrega |
| desarrollo | [Responsabilidad de GitHub Actions](desarrollo/GITHUB_ACTIONS.md) |
| evidencias | Registros de pruebas por fecha |
| estadia | [Información académica existente](estadia/ALUMNO.md) |
| archivo | PRD/MVP combinado histórico; la plantilla y dependencias obsoletas fueron retiradas |

Las fechas y resultados históricos se conservan. Cambiar la ubicación de un documento no acredita pruebas nuevas, aceptación o ejecución Scrum. El [backlog](../gestion_proyecto/scrum/BACKLOG_CIERRE.md) permanece junto a la gestión del proyecto.

Los accesos .cmd están agrupados en [operacion](../operacion/README.md), no mezclados con estos documentos.
