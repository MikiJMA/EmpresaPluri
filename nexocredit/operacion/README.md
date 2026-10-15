# Operación local — NexoCredit

Los accesos de Windows están agrupados por función. Cada .cmd resuelve la raíz del proyecto antes de llamar al script; se puede abrir con doble clic desde su carpeta o invocar por su ruta desde otra ubicación.

## Aplicación

Con Docker Desktop activo:

- [Abrir NexoCredit](<aplicacion/Abrir NexoCredit.cmd>): utiliza las imágenes existentes y abre localhost:8080; no recompila.
- [Actualizar NexoCredit](<aplicacion/Actualizar NexoCredit.cmd>): construye e inicia para aplicar cambios de código. Puede descargar dependencias públicas.
- [Detener NexoCredit](<aplicacion/Detener NexoCredit.cmd>): detiene servicios conservando el volumen de datos.

Los tres accesos reutilizan scripts/docker.ps1. No instalan Docker ni publican la aplicación. Abrir con imágenes antiguas no demuestra que un cambio reciente ya esté aplicado.

- [Crear usuario local](<aplicacion/Crear usuario local.cmd>): solicita usuario/nombre y contraseña oculta, sin cuentas predeterminadas. Requiere imágenes actualizadas, migración 003 y acceso local habilitado.

## Integraciones

- [Editar configuración privada](<integraciones/Editar configuracion privada.cmd>): abre `.env` en un editor, sin pegar llaves en la terminal ni en el navegador.
- [Activar modo local](<integraciones/Activar modo local.cmd>): Ollama + documentos locales, cuenta local habilitada y laboratorio ML deshabilitado honestamente. Conserva llaves Azure y datos PostgreSQL.
- [Activar modo Azure](<integraciones/Activar modo Azure.cmd>): vuelve a Azure sin quitar el acceso local; requiere suscripción/recursos vigentes.

Consultar [campos de configuración, cuentas y límites](../docs/manuales/ACCESO_LOCAL_Y_PROVEEDORES.md). Ollama no requiere llave. Cambiar de proveedor no cancela recursos ni facturación Azure.

- [Conectar Azure OpenAI](<integraciones/Conectar Azure OpenAI.cmd>).
- [Conectar Azure ML](<integraciones/Conectar Azure ML.cmd>).
- [Conectar Azure AI Search](<integraciones/Conectar Azure AI Search.cmd>).
- [Conectar Banxico](<integraciones/Conectar Banxico.cmd>).
- [Cargar documentos Azure AI Search](<integraciones/Cargar documentos Azure AI Search.cmd>).

Los configuradores solicitan secretos de manera privada y pueden aplicar configuración a servicios locales. No compartir claves ni archivos .env. Cargar documentos escribe en el índice Azure; utilizarlo solo cuando se quiera actualizar el contenido y con permisos adecuados, no como una comprobación inocua.

## Pruebas y recuperación

- [Probar programación](<pruebas/Probar programacion.cmd>): suite con PostgreSQL temporal aislado; no usa la base de trabajo.
- [Respaldar PostgreSQL](<respaldos/Respaldar PostgreSQL.cmd>): respaldo manual privado.
- [Probar restauración PostgreSQL](<respaldos/Probar restauracion PostgreSQL.cmd>): crea un respaldo nuevo por defecto y verifica recuperación en un destino temporal, sin sobrescribir el origen.

Los dumps no están cifrados ni incluyen roles globales/ACL. Los lanzadores conservan los límites existentes; no convierten un ensayo local en recuperación productiva. Para probar un respaldo existente, consultar el [manual](../docs/manuales/OPERACION.md) y la [evidencia técnica](../docs/evidencias/2026-10-04/cierre-tecnico.md).

## Implementación

Los scripts Python/PowerShell siguen en scripts para preservar sus rutas internas, pruebas y CI. Los .cmd de esta carpeta son accesos, no copias del backend o configuradores. No mover .local, .venv, .env ni archivos Power BI privados para “limpiar”: contienen entorno, datos o configuración.
