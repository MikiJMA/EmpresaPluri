# Correcciones de la segunda ronda de ruptura

Fecha de trabajo indicada por el usuario: 11/10/2026, America/Mexico_City. Parte de la comprobación ocurrió el 12/10/2026 UTC. Sustituye el estado pendiente del diagnóstico de la segunda ronda, sin reescribir resultados de pruebas anteriores.

## Cambios implementados

| Hallazgo | Corrección | Resultado reproducido |
|---|---|---|
| NUL en observaciones llegaba a PostgreSQL y provocaba 503; texto invisible/DEL se aceptaba | Validador de contenido visible y controles ocultos antes de persistir; permite texto Unicode ordinario, saltos de línea y tabulación | Los tres ataques originales ahora reciben 422, sin guardar; texto válido sigue admitido |
| Frontend aceptaba fechas inexistentes, importes extremos y respuestas contradictorias | Calendario gregoriano, hora/zona explícitas, importes acotados, RFC coincidente y revisión actual coherente con el historial completo; promedios consistentes con cantidad/cobertura | Las doce respuestas inválidas del diagnóstico se rechazan antes de incorporarse al estado |
| Excepción inesperada revertía la cuota de explicación | Commit del intento antes de llamar al proveedor, locks de sesión en conexión dedicada y error genérico saneado cacheado un minuto | Tres reintentos inmediatos ahora producen una sola llamada simulada y un intento persistido; renovar tras vencer registra tres llamadas y tres intentos en la regresión |
| Certificado de CA inexistente provocaba 500 | Error de configuración/conexión segura controlado, sin desactivar TLS ni mostrar rutas privadas | La misma inicialización real del cliente con CA inexistente recibe 503 antes de una solicitud de red |
| Capturas con pagos superiores a gastos y deuda cero con atraso pendiente se guardaban | Validación de campos cruzados en API y alerta accesible/bloqueo de envío en formulario | Ambas capturas originales ahora reciben 422; el repositorio no se invoca con las entradas rechazadas |

El límite de gasto/ingreso/deuda/pagos conserva 1.000.000.000 MXN; el margen admite valores negativos dentro del rango del servidor. Febrero no se normaliza a marzo. Se admiten años bisiestos válidos, timestamps con microsegundos y zonas explícitas positivas/negativas.

La validación del detalle no impone las reglas nuevas de captura a registros históricos: se conservan ausencia frente a cero y datos anteriores. La API sigue admitiendo solicitudes antiguas que omitan deuda/pagos/atraso. No se exige deuda positiva sólo por haber pagado créditos en el mes cuando el atraso es cero. Las reglas `reglas-demo-v1`, resultados guardados y facultades de revisión no cambian; no autoriza créditos reales.

## Diseño de la reserva de cuota

La conexión PostgreSQL es dedicada, no pooled. Los locks advisory de sesión por evaluación/clave y por cuenta sobreviven al commit de la reserva y se liberan al cerrar la conexión. El límite sigue siendo diez intentos por cuenta/hora y se rechazan carreras con 429; reutilizar una respuesta vigente no consume otro intento.

El proveedor sólo se invoca después de confirmar la reserva. La suite comprueba desde una segunda conexión que el contador ya es visible al entrar al callback. También simula una interrupción `SystemExit` y un fallo posterior de almacenamiento: el intento permanece y los locks se liberan. Diez errores inesperados en evaluaciones distintas agotan el límite; nuevas solicitudes reciben 429 sin llamar al proveedor.

La reserva cuenta intentos, no facturas: puede consumirse incluso si el fallo ocurre antes del envío al proveedor. No evita perder el texto ya generado si el proceso/base falla después. No hay reintento automático, garantía exactly-once ni eliminación automática de textos vencidos. Cambiar a un pool de conexiones exige revisar la liberación de locks de sesión.

## Pruebas y evidencia

`scripts/probar-programacion.ps1` terminó correctamente con:

- **139 pruebas backend/PostgreSQL**, sin fallos ni omisiones; migraciones aplicadas dos veces en una base temporal.
- **96 pruebas frontend**, sin fallos ni omisiones, incluyendo renderizado aislado del formulario y bloqueo de envío.
- Lint y build frontend aprobados; `npm audit` reportó cero vulnerabilidades.
- Cinco archivos de pruebas PowerShell aprobados.

Se añadieron nueve pruebas backend y siete frontend respecto de la suite 130/89. Los dobles de proveedores no usan llaves ni redes reales. El caso TLS utiliza la inicialización real de `httpx.Client` con una ruta ficticia inexistente: falla antes de una llamada externa.

Se repitieron los scripts del diagnóstico original, preservando sus resultados anteriores: **29 registros de casos/grupos backend y 13 frontend**. Revocación de cuenta/sesión, roles desde PostgreSQL y concurrencia idempotente siguieron resistiendo; una generación concurrente rechazó doce cuentas ficticias con 429, sin duplicar proveedor. Los 503/502/504 del diagnóstico posterior son fallos deliberados de base/proveedor/configuración, controlados; no respuestas 500 inesperadas.

La carrera tardía del cliente de autenticación mantiene el token nuevo y la guarda de intento de `Acceso.jsx`; no se había demostrado una suplantación visible y no se modificó ese flujo en esta corrección.

Fuentes/evidencias privadas en la raíz exterior, excluidas de Git:

```text
output/pruebas_ruptura/2026-10-11/ronda-2/
  REPORTE.md                         diagnóstico previo, conservado
  backend.py / frontend.mjs          reproducciones originales
  resultados_backend.json           antes
  resultados_frontend.json          antes
  corregido/resultados_backend.json después
  corregido/resultados_frontend.json después
  corregido/validar_datos_guardados.mjs
```

El script de validación de datos guardados recibe los datos de PostgreSQL por un pipe local, sólo en memoria. No escribe ni imprime RFC, solicitudes, revisiones o credenciales. Comprobó historial, los nueve detalles existentes y dashboard usando los contratos nuevos.

## Aplicación local

Se construyeron y recrearon sólo backend y frontend con Compose `--no-deps`. No se cambió el esquema ni se ejecutó una nueva migración sobre la base de trabajo; PostgreSQL y su volumen no se recrearon. No se cambió la cuenta ni su contraseña, las llaves o la selección de proveedores. Todas las integraciones Azure y alternativas locales se conservaron.

Conteos antes/después: **9 evaluaciones, 2 revisiones, 1 cuenta local**. Backend, frontend y PostgreSQL saludables; `/health` respondió `ok`. Los contenedores temporales de la suite y de esta ronda fueron retirados tras verificar sus etiquetas propias. Sólo se descartaron fixtures ficticios recuperables ejecutando de nuevo los scripts.

La página y su nuevo bundle `/assets/index-Y9544Kvt.js` respondieron HTTP 200. Sin sesión, dashboard, historial y estado de OpenAI respondieron HTTP 401 después de la actualización; esas consultas no iniciaron proveedores.

Para cargar el bundle nuevo, recargar la aplicación en `http://localhost:8080/` e iniciar sesión local de nuevo. Los tokens locales viven en memoria del navegador. No se ejecutó un nuevo flujo manual completo del usuario ni una prueba visual en su sesión real.

## Límites

No se consumió IA ni se consultaron Azure/Banxico/SAT reales en estas pruebas. No se publicó un commit, CI remota o despliegue cloud. Las pruebas aprueban estos casos conocidos, no certifican seguridad absoluta, aptitud crediticia ni producción. No se hizo saturación prolongada ni una nueva restauración de respaldo en esta ronda.
