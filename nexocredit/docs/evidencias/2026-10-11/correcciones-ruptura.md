# Correcciones tras pruebas de ruptura — 11/10/2026

Fecha del usuario: 11/10/2026, America/Mexico_City. Los nombres de respaldo usan UTC y por eso empiezan con `20261012`.

## Qué se corrigió

| Hallazgo | Corrección | Comprobación |
|---|---|---|
| Números no finitos/Unicode provocaban HTTP 500 | Manejo global de validación sin reflejar input/ctx y validación de identificador | NaN, ±Infinity, 1e309 y Unicode aislado ahora 422, incluso con sesión de prueba real |
| `true` se guardaba como importe 1 | Los cuatro importes exigen números JSON, no booleanos ni cadenas | 422 sin persistir; enteros y decimales válidos siguen admitidos |
| RFC solo de espacios, controles o 8192 caracteres | Identificador nuevo de 1–120 caracteres, no blanco ni categorías Unicode de control | 422 para entradas inválidas; identificadores demo libres previos no se reescriben ni se convierten en certificaciones SAT |
| Offset excesivo llegaba a PostgreSQL y producía 503 | Offset máximo 1.000.000 | Valores excesivos rechazados con 422 antes de consultar la base |
| HTTP 200 inesperado fallaba al renderizar React | Contratos de evaluación/historial/detalle/revisión/dashboard/explicación, defensas de presentación y Error Boundary | Objetos vacíos, factores nulos, filas nulas, fechas inválidas y riesgos ajenos se rechazan con mensaje recuperable; no se inventan cifras |
| Logins correctos agotaban cuota de fallos | Separar fallos de ráfagas en PostgreSQL | 25 logins correctos funcionan; los fallos previos no se borran; 60 peticiones/minuto siguen limitadas |
| Clientes del proxy podían compartir el origen del frontal | Nginx sobrescribe X-Forwarded-For; backend acepta solo al servicio frontend resuelto y explícito; Uvicorn no interpreta encabezados arbitrarios | Pruebas de origen confiable/no confiable, rechazo de listas/IP inválido y resolución real de frontend |
| Repetir la API de explicación iniciaba otra generación | Caché privada PostgreSQL de 24 h, bloqueos transaccionales y cuota de 10 nuevas generaciones por cuenta/hora | Tres peticiones generan una sola llamada al proveedor simulado; concurrencia/cuota/expiración probadas con PostgreSQL real |

La revisión RFC/CURP sigue siendo básica y opcional, con consulta SAT manual. No se implementó una API oficial de identidad ni se cambió el scoring, el acceso Microsoft o el mínimo local de seis caracteres.

## Verificación

`scripts/probar-programacion.ps1` aprobó **130 pruebas backend/PostgreSQL y 88 frontend**, sin omisiones, además de lint/build, auditoría npm sin vulnerabilidades reportadas y cinco archivos PowerShell. Las migraciones se aplicaron dos veces en PostgreSQL temporal. Los contratos de proveedores se prueban sin caché con dobles de prueba; la caché/cuotas tienen una suite propia contra PostgreSQL aislado real. Después se añadió el aviso visible de retención de la caché y su prueba: la reconstrucción final frontend aprobó **89 pruebas**, lint y build. No cambió el backend después de su suite de 130.

También se repitió el diagnóstico adversarial original: 119 registros backend (incluidos 128 envíos de fuzz y grupos de concurrencia/autenticación) y 11 casos frontend. No hubo respuestas 5xx en esa ejecución. Los ocho casos de respuestas inválidas se rechazaron antes del render, no apareció el riesgo inventado ni `Invalid Date`. Los 21 accesos correctos de la prueba extra ya no producen 429. El bloqueo tras veinte fallos desde el mismo origen permanece intencionalmente.

Los resultados originales y posteriores se conservan por separado en la carpeta privada, excluida de Git: `output/pruebas_ruptura/2026-10-11/` y su subcarpeta `corregido/`, en la raíz exterior. No son sprints Scrum ni CI remota.

## Aplicación local y datos conservados

Se creó un respaldo privado antes de la migración. Se reconstruyeron/recrearon backend, migraciones y frontend; PostgreSQL y su volumen se conservaron. La migración 004 amplía contadores y crea `cache_explicaciones` / `cuotas_explicaciones`; no transforma evaluaciones, revisiones, usuarios ni contraseñas.

Al terminar: frontend/backend/PostgreSQL saludables y endpoint health correcto. Conteos conservados: **9 evaluaciones, 2 revisiones y 1 cuenta local**. La migración 004 figura aplicada y el servicio frontend se resuelve para la política de proxy. Los nueve detalles, el historial y el dashboard existentes fueron leídos y validados con los contratos frontend actuales en memoria local, sin imprimir ni conservar los datos.

Se creó un segundo respaldo del esquema actualizado y se restauró en un contenedor aislado: **7 tablas**, con filas, huellas, columnas, restricciones y vistas coincidentes. El origen se conservó y el temporal se retiró. Los dumps siguen siendo privados, sin cifrado ni roles globales/ACL; no compartirlos ni tratarlos como recuperación productiva completa.

No se generaron nuevas evaluaciones/revisiones/cuentas en la base de trabajo, no se gastó IA real, no se rotaron secretos ni se publicó un commit/despliegue cloud. Para cargar el bundle nuevo se debe recargar la pestaña e iniciar sesión otra vez. La comprobación de los contratos sobre datos guardados no acredita un nuevo flujo manual completo del usuario en el navegador.

## Límites relevantes

- Los usuarios detrás de la misma IP/NAT comparten los límites por origen. Se mantiene protección de cinco fallos por cuenta y veinte fallos por origen/15 minutos; el máximo adicional es sesenta peticiones de login por origen/minuto. Los antiguos contadores conservan su valor hasta vencer, no se borraron para facilitar la prueba.
- La caché persiste texto/referencias privados, relacionados internamente con el UUID de evaluación. No se envía RFC, CURP, UUID ni identidad al modelo. La cuota usa una huella de la cuenta. Vencer en 24 horas deja de reutilizar el texto, pero no lo borra automáticamente. Los errores saneados se conservan un minuto.
- Un proceso interrumpido o una base fallando durante una generación puede perder una respuesta ya cobrada; tras recuperarse, una nueva petición podría consumir otra vez. No hay reintento automático ni garantía exactly-once ante fallos externos. No se garantizan saldo, disponibilidad o calidad de Azure/Ollama por pasar estas pruebas.
- No se hizo saturación prolongada, evaluación crediticia real, auditoría completa de seguridad ni una nueva ejecución de GitHub Actions. El Error Boundary recupera errores de render, no todos los errores asíncronos/eventos; los clientes tratan por separado los errores HTTP.

Operación/retención: [manual de acceso y proveedores](../../manuales/ACCESO_LOCAL_Y_PROVEEDORES.md). Las integraciones Azure obligatorias se conservaron.
