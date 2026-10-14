# Plan de mantenimiento y soporte multinivel

Plan operativo para la demo local, 11/10/2026. Roles de trabajo, no nombramientos de personas externas ni SLA empresarial. No se contactó a asesores/proveedores. Las frecuencias siguientes son una propuesta operativa; no crean automatizaciones ni acreditan tareas pasadas.

## Responsabilidades por nivel

| Nivel | Alcance | Comprobación / escalamiento |
|---|---|---|
| 1 — Operador local | Acceso, captura, interpretación de avisos, estado Docker, abrir reporte | Verificar campos y servicios. Escalar sin contraseña, token, RFC/CURP o dump |
| 2 — Mantenimiento de aplicación | API/DB, proveedores, conflictos de versión, respaldo y restauración temporal | Reproducir con fixture, revisar configuración de nombres sin imprimir valores, identificar última versión sana |
| 3 — Desarrollo/modelo | Corrección, migración, dependencia, análisis ML y cambios de seguridad | Añadir regresión, ensayar en temporal, documentar cambios y límites. No introducir reglas oficiales sin base definida |

Una misma persona puede ejercer los tres niveles en esta demo. Antes de uso empresarial deben asignarse personas/canales y tiempos acordados; aquí no se prometen plazos de respuesta.

## Mantenimiento preventivo propuesto

| Momento | Acción | Evidencia mínima |
|---|---|---|
| Antes de mostrar la demo | Docker abierto, health, login propio, corte de datos y modo de proveedores | Fecha y estado, sin secretos |
| Antes de modificar código/esquema | Respaldo privado y pruebas aisladas; conservar commit/estado previo | Directorio/manifest privado y resultado de suite |
| Después de una actualización | Servicios saludables, conteos conservados, sesión/rechazos, contratos compatibles | Registro técnico fechado; no medir “éxito” sólo por construir imagen |
| Al revisar créditos otro día | Pulsar Actualizar vencimientos y revisar cuotas pendientes | Fecha de alertas y eventos; no asumir vigilancia de fondo |
| Semanal, si hubo trabajo | Respaldo manual y lectura de incidentes/cambios | Copia privada verificada; volumen Docker no es respaldo |
| Al cambiar dependencias | Audit, suites, lint/build y ensayo de integración | Resultado fechado; no garantía permanente |
| Periódicamente | Revisar acceso, caducidad de Azure, modelos instalados y acumulación de caché/dumps | Inventario de nombres/fechas, nunca llaves o contraseñas |

No se elimina texto vencido o respaldo automáticamente. La caché vencida deja de reutilizarse; su limpieza requiere procedimiento/retención definidos. Los dumps contienen hashes y datos privados sin cifrado y sin roles globales/ACL: guardar en `.local/respaldos_postgresql`, no entregar ni publicar. Antes de copiar fuera del equipo, definir protección/cifrado.

## Runbook de incidentes

1. Registrar fecha UTC/local, síntoma, entorno y alcance, sin payloads privados.
2. Ejecutar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 estado` desde la raíz interior. `/health` confirma disponibilidad local, no salud de cada proveedor externo.
3. 401: volver a iniciar sesión; recargar pierde sesión local en memoria. 403: verificar facultad necesaria sin elevar el rol para evitar el error. 422: corregir captura. 409: conservar clave de reintento si hubo timeout; ante cambio de versión, recargar detalle y revisar antes de otra operación.
4. 503 DB: no alternar con la base nativa ni borrar volumen; verificar PostgreSQL/migraciones. 502/504 de proveedor: distinguir contrato/timeout y revisar metadatos sin imprimir secreto. No reintentar IA automáticamente ni deshabilitar TLS.
5. Reproducir el fallo con datos ficticios en las pruebas temporales. Si afecta saldos o integridad, detener nuevas escrituras voluntariamente hasta revisar; no hacer SQL correctivo sin respaldo y estrategia.
6. Corregir o volver a una imagen de código conocida compatible con el esquema. No usar `docker compose down -v` ni `git reset --hard`. Una reversión de código no revierte una migración: valorar compatibilidad antes de arrancar.
7. Confirmar servicios, pruebas y datos; registrar solución, limitaciones y cierre técnico. No marcar capacitación/aceptación por completar un incidente.

## Respaldo y recuperación ensayada

Accesos en `operacion/respaldos/`. `scripts/respaldo-postgresql.ps1 crear` crea snapshot/dump privado. `probar -Respaldo <carpeta>` restaura sólo un contenedor temporal sin red ni puertos y compara tablas, datos, columnas, restricciones y vistas; valida identidad antes de retirar su temporal. No restaura sobre origen. Nunca usar una ruta ajena o compartir el manifiesto sin revisión.

Tras restaurar una base con cuentas en un futuro entorno autorizado, rotar el secreto local de sesión y revisar configuración para invalidar tokens previos. RPO/RTO, automatización de respaldos y recuperación de host completo siguen sin compromisos productivos. [Herramienta y límites](../../backend/app/persistencia_postgresql/README.md).

## Formato de incidente

ID; fecha real; versión/entorno; severidad observada (bloqueo, integridad, visual); pasos ficticios; esperado/observado; nivel técnico; diagnóstico; corrección; prueba de regresión; datos conservados; fecha de cierre; pendiente. No registrar contraseñas, tokens, llaves, CURP o expedientes.
