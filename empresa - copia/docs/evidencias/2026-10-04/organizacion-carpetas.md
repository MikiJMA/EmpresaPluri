# Reorganización de carpetas — NexoCredit

Seguimiento local de organización. No modifica el alcance del MVP, no acredita aceptación/Scrum y no publica o despliega la aplicación.

## Cambios

- Ocho documentos reubicados por propósito: producto, planificación, manuales, calidad, entrega y desarrollo. El PRD/MVP combinado se conserva en archivo.
- Ocho accesos .cmd reubicados en operación: integraciones, pruebas y respaldos.
- Tres accesos agregados para abrir, actualizar y detener la instalación Docker existente.
- Índices de documentación y operación con las nuevas rutas; enlaces y mensajes de configuración actualizados.
- Documentación CI retirada de la carpeta interior .github; el workflow real permanece en la raíz Git exterior.
- Workspace NexoCredit.code-workspace y preferencias VS Code para una vista sin temporales/entornos generados. Esos archivos siguen en disco.

Se conservaron datos PostgreSQL, configuración privada, entornos virtuales y proyectos Power BI. No se renombraron las carpetas de código ni se modificaron sus imports.

## Verificación ejecutada

Comando desde la raíz interior: powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\probar-programacion.ps1.

La primera ejecución quedó bloqueada por acceso al pipe Docker del sandbox; no inició ni reinició la aplicación. La ejecución autorizada posterior terminó con código 0:

| Comprobación | Resultado |
|---|---|
| Backend con PostgreSQL temporal real | 69 pruebas, OK, sin omisiones |
| Frontend | 48 pruebas, 48 aprobadas, cero fallos/omitidas |
| ESLint y Vite build | Aprobados |
| npm audit | Cero vulnerabilidades reportadas en esta ejecución |
| Migraciones consecutivas | Ambas completadas |
| Pruebas PowerShell | Cuatro archivos aprobados |
| Nuevas rutas operativas | Once lanzadores y sus scripts validados |

Los proveedores externos de negocio usan mocks en las suites; no se realizaron llamadas Azure, Banxico o Banco Mundial. El PostgreSQL temporal no publicó puertos ni montó datos/configuración privados, y fue retirado al terminar. La base de trabajo no se utilizó como destino.

La prueba de organización valida rutas y contenido sin ejecutar los configuradores .cmd ni leer sus secretos. También se comprobó por separado con Windows PowerShell 5.1.

La construcción actualizó imágenes de verificación, no los servicios de la aplicación. La advertencia de deprecación Starlette/httpx no bloqueó la suite; no se considera una corrección de dependencias realizada.

## Límites

El workflow incluye ahora la prueba de organización, pero no se disparó GitHub Actions ni se hizo commit, push, merge o despliegue. Los resultados CI históricos mantienen sus fechas y conteos.

Los archivos estaban pendientes de revisión/staging antes de esta tarea. Su índice Git no se reescribió automáticamente; las reubicaciones forman parte de los cambios locales.

Consultar [documentación](../../README.md), [operación](../../../operacion/README.md) y [mapa del workspace](../../../../README.md).
