# Acceso local y Ollama — 11/10/2026

Registro de desarrollo local de NexoCredit. No acredita producción, vigencia de Azure ni una nueva ejecución de GitHub Actions.

## Verificación automática

`scripts/probar-programacion.ps1` terminó correctamente tras reconstruir las imágenes de verificación. No montó archivos privados ni utilizó la base de trabajo como destino. PostgreSQL temporal sin salida de red, puertos publicados ni carpetas del usuario; el contenedor propio se retiró al terminar.

| Comprobación | Resultado observado |
|---|---|
| Backend y PostgreSQL | 106 pruebas aprobadas, sin omisiones; migraciones aplicadas dos veces |
| Frontend | 64 pruebas aprobadas, sin omisiones; lint y build aprobados |
| Dependencias npm | `npm audit --audit-level=high`: 0 vulnerabilidades reportadas |
| Utilidades PowerShell | Cinco archivos de pruebas aprobados |
| Configuración local | Pruebas adicionales de campos vacíos seguidos de otras variables, secreto preservado y modelo elegido conservado, aprobadas después de la revisión |

Las pruebas cubren hash scrypt, JWT local separado de Entra, revocación, límites persistentes de intentos, omisión de contraseñas en errores y envío de tokens solo a la API propia. La integración de acceso con PostgreSQL se probó en la base aislada, no creando una cuenta predeterminada en la base del usuario. Azure y APIs financieras emplearon respuestas simuladas en esta suite.

Se actualizó mecánicamente `source-map-js` de 1.2.1 a 1.2.2 en el lockfile tras el aviso de auditoría; la [alerta oficial](https://github.com/advisories/GHSA-68fv-2mgg-jv7q) identifica 1.2.2 como versión corregida. La auditoría describe el resultado del registro consultado en esta fecha, no ausencia permanente de riesgos.

## Generación real local

Ollama ya estaba instalado en Windows. Se observaron sus modelos por `/api/tags` desde el equipo y desde Docker. No se descargaron modelos ni se cambió la exposición del servicio.

El adaptador nuevo generó una explicación real con `llama3.1:8b` desde un contenedor de verificación sin credenciales Azure. Escenario ficticio: ingresos 30,000 MXN, gastos 10,000 MXN, score 700, margen 20,000 MXN y riesgo demo Bajo. La respuesta completa llegó en aproximadamente 56.7 segundos, con `proveedor=ollama`, `generada_por_ia=true` y cita de DEM-02. No se guardó una evaluación para esta comprobación ni se envió el RFC al modelo.

Este resultado es una generación puntual, no una prueba de carga, calidad general o latencia garantizada. El límite HTTP es 60 segundos; no hay descargas, reintentos ni cambio automático a Azure ante fallos.

## Aplicación de los cambios

Se preparó el modo local y se reconstruyeron los servicios de trabajo con Docker Compose. Backend, frontend y PostgreSQL quedaron saludables; migraciones terminó correctamente. Se conservaron las líneas de configuración de PostgreSQL, Azure y Banxico sin imprimir sus valores.

- Evaluaciones antes/después: 9 / 9. Revisiones antes/después: 2 / 2.
- Migraciones presentes: 001, 002 y 003. Las dos tablas de autenticación nuevas quedaron vacías.
- Acceso público de configuración: local habilitado, sin cuentas disponibles todavía. Frontend HTTP 200.
- Solicitudes anónimas a identidad, proveedores, evaluaciones y catálogo documental: HTTP 401 a través de Nginx.
- Proveedores efectivos: explicaciones Ollama (`llama3.1:8b`), documentos locales (14 secciones), laboratorio ML deshabilitado explícitamente.
- Revisión visual de la pantalla real: formulario local, aviso de primera cuenta y botones Microsoft visibles; sin contraseñas o llaves mostradas.

La primera cuenta de trabajo queda a cargo del usuario mediante `operacion/aplicacion/Crear usuario local.cmd`, que solicita su contraseña en privado. No se completó una sesión humana local en la aplicación de trabajo ni una nueva sesión Microsoft en esta revisión. No se actualizaron Power BI ni sus evidencias históricas, no se hizo un ensayo nuevo de restauración de las tablas de cuentas y no se publicó ni se creó un commit.

## Ajuste posterior: contraseña desde seis caracteres

Por petición del usuario se redujo el mínimo de 12 a 6 caracteres, sin exigir mayúsculas, números ni símbolos. El máximo de 128 y el rechazo de contraseñas compuestas únicamente por espacios se conservan. La política se comparte entre hash/verificación, esquema de login y aviso del creador de cuentas; el formulario y el manual también indican seis. No se cambió `LOCAL_AUTH_SECRET`, Microsoft ni las credenciales de PostgreSQL.

La suite completa posterior aprobó 109 pruebas backend/PostgreSQL, 64 frontend, lint/build, auditoría npm sin vulnerabilidades reportadas y cinco archivos PowerShell. Los casos nuevos incluyen exactamente seis, rechazo de cinco, 128/129, Unicode, contraseña anterior larga y reset a seis con revocación de la sesión anterior; se probaron en la base aislada.

Se reconstruyó y aplicó Docker: servicios saludables y esquema de login del backend activo con `minLength=6`. Los conteos permanecieron en 9 evaluaciones, 2 revisiones y 0 cuentas locales. No se creó ni cambió una contraseña real; el usuario debe repetirla idéntica en la confirmación al crear su cuenta.

## Límites y operación

La evaluación principal y el historial siguen usando PostgreSQL y reglas demo. El artefacto AutoML no se ejecuta localmente: se conserva el adaptador Azure ML y el modo local muestra su laboratorio deshabilitado, sin predicciones inventadas. Banxico/Banco Mundial siguen necesitando Internet. Seleccionar Ollama no cancela ni elimina recursos de pago Azure.

Ver [manual de acceso, proveedores y llaves](../../manuales/ACCESO_LOCAL_Y_PROVEEDORES.md). El archivo privado `.env` y los respaldos con hashes de cuentas no se deben compartir ni publicar.
