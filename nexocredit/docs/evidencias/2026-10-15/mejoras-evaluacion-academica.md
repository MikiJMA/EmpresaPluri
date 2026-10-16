# Mejoras posteriores a la revisión académica - 15/10/2026

## Alcance y procedencia

Esta comprobación corresponde exclusivamente a la copia académica reorganizada. No modifica la instalación de desarrollo, su base de datos o su navegador. No es una reevaluación de la rúbrica ni una calificación nueva.

Referencias locales reales, sin reconstruir ni retrofechar el proceso:

- Base de la copia pública: `0c07fb9547e8116967257f49f52d88802d93e343`.
- Reorganización, configuración y recorrido: `079d205`.
- Segunda opinión y pruebas: `9de9d8a0106b21a8355dff158038956b8ac34692`.
- Rama local: `codex/mejoras-evaluacion-academica`.

El usuario eligió conservar las mejoras sólo localmente. No se hizo push, cambio de rama predeterminada, PR o ejecución nueva de GitHub Actions. Los resultados CI anteriores conservan su fecha y no acreditan este incremento.

## Respuesta a las cinco observaciones

| Observación | Cambio comprobable | Límite |
|---|---|---|
| Carpeta `empresa - copia/` | Código de entrega movido a `nexocredit/`; CI, workspace, lanzadores y empaquetado ajustados; Compose `nexocredit-demo` | El entorno original no se movió ni se inició otro Compose de trabajo |
| Proceso e historial | Commits locales separados y README con procedencia del repositorio de desarrollo | No se inventó historia anterior ni se otorgó acceso al repositorio original |
| Inteligencia en evaluación | Tarjeta opcional con inferencia real del modelo junto al resultado guardado | Usa un escenario UCI independiente; no calcula el riesgo individual de la solicitud mexicana |
| Ruta de revisión | README principal con instalación y cuatro pasos, ejemplos 200/600/900 y consulta UCI | La explicación por plantilla no se atribuye a IA generativa; Ollama necesita servicio/modelo |
| Transparencia IA | Declaración de asistencia de Codex y sus tareas | No equivale a aceptación humana o certificación académica |

## Suite local final

Comando desde `nexocredit/`: `powershell.exe -NoProfile -File .\scripts\probar-programacion.ps1`, sin `-SinConstruir`.

| Verificación | Resultado observado |
|---|---|
| Backend Python 3.12 / PostgreSQL 17 | **211 pruebas aprobadas**, sin fallos ni omisiones; 24,976 s en la corrida final |
| Frontend Node 24 | **146 pruebas aprobadas**, sin fallos ni omisiones; 17 nuevas de la segunda opinión |
| Migraciones | Cinco migraciones, ejecutadas dos veces sin errores |
| Lanzadores | Cinco archivos de pruebas PowerShell aprobados, sin leer configuración privada |
| ESLint y Vite | Aprobados; construcción frontend final válida |
| `npm audit --audit-level=high` | Cero vulnerabilidades reportadas en esta consulta; no es garantía permanente |
| Empaquetado Windows | 30 pruebas relacionadas: 17 paquete y 13 respaldo; incluidas en el total backend, no se suman otra vez |
| Selección pública real | Escaneo en memoria de 352 archivos antes de añadir este registro; rutas ZIP relativas, sin error de rutas largas TMDL |

La construcción frontend se ejecutó en la primera corrida de este incremento y se reutilizó por caché en la repetición final, sin cambios posteriores en sus fuentes. Backend y empaquetador se reconstruyeron para incorporar la última regresión de rutas largas. No se deshabilitó la comprobación TLS ni se instalaron dependencias en el proyecto original.

La suite usa PostgreSQL efímero con red `none`, sin puertos publicados ni montajes del equipo; backend comparte únicamente esa red temporal. El almacenamiento de PostgreSQL es temporal. La limpieza comprueba la identidad y etiqueta del contenedor antes de retirarlo. La base de trabajo no se usa como destino.

Medición acotada del seguimiento en la última suite: 40 lecturas secuenciales y 40 con cuatro hilos, cero errores HTTP. P95 de 23,10 ms y 96,04 ms respectivamente. Es TestClient/FastAPI/PostgreSQL temporal, no navegador, TLS, producción ni un SLA.

Advertencia no bloqueante observada: Starlette informa una futura migración de su transporte TestClient/httpx. No produjo fallos y no se alteraron las versiones para ocultarla.

## Segunda opinión: contrato y criterios

`POST /api/v1/evaluaciones/{identificador}/segunda-opinion` requiere sesión y una evaluación existente. Acepta exactamente 19 enteros UCI; rechaza identidad, valores implícitos, fracciones, booleanos y campos extra. Devuelve UUID, riesgo/versión originales, contrato del modelo, `guardada: false` y advertencia.

Las nueve pruebas nuevas del endpoint cubren autenticación, validación, existencia, errores de base/proveedor, modelo local real, proveedor Azure simulado y conservación de registros v1. Se comprueba que no haya llamadas de escritura, conversión de monedas, uso del RFC por el proveedor o recálculo del scoring. Las pruebas del cliente/interfaz cubren contrato, cancelación, respuestas tardías, doble clic, errores y consulta explícita; cargar el ejemplo no ejecuta inferencia.

Se conserva `nexocredit-uci-logistica-v1` y su SHA-256 `259b997587543c3466f665a8b62577465014c2c867ebdbfba61544b2d364b8a4`. El refactor divide validadores para legibilidad, sin reentrenar, cambiar coeficientes o alterar el algoritmo. Las métricas existentes siguen perteneciendo al conjunto UCI de Taiwán, 2005, en NTD; no son precisión crediticia validada en México ni probabilidad calibrada.

## Prueba integral real y capturas

Se ejecutó Chrome headless con perfil temporal propio, frontend Nginx de esta versión, FastAPI y PostgreSQL tmpfs aislados. No se controlaron ventanas o sesiones del usuario. Referencia funcional: `9de9d8a0106b21a8355dff158038956b8ac34692`; ejecución final `nexocredit-segunda-20261015-0af1ad4b`.

- Acceso local con cuenta efímera, sin credenciales predeterminadas o compartidas.
- Una evaluación ficticia: score 900, ingresos 30000, gastos 10000, margen 20000 MXN, riesgo Bajo, `reglas-demo-v2`, guardada en la base temporal.
- El panel comprobó el estado sin inferir. Cargar el ejemplo sólo llenó las 19 entradas. Se hizo **una consulta explícita**, HTTP 200 y `Cache-Control: no-store`; proveedor local, modelo/huella esperados y clase booleana `false` (No incumplimiento académico).
- La respuesta indicó `guardada: false`. El detalle recuperado por API antes y después fue idéntico y el dashboard conservó una sola evaluación. Editar el formulario retiró la opinión anterior, sin otra inferencia.
- Cero excepciones JavaScript. Tarjeta móvil contenida entre x=14 y x=376 en viewport de 390 píxeles; ancho interno 360, sin desbordamiento. Capturas revisadas de escritorio y móvil; no se ocultaron elementos o modificaron estilos para producirlas.
- Se bloquearon solicitudes de fuentes externas e indicadores financieros de fondo; esta prueba no acredita conectividad financiera o Azure. La explicación se configuró como plantilla determinista **NO IA generativa**, no como ejecución Ollama.

Cuatro PNG y su manifiesto con SHA-256 se conservaron localmente en `output/evidencias/Segunda_Opinion_NexoCredit_2026-10-15/` de la raíz de desarrollo exterior, fuera del repositorio académico. No se atribuyen a una ejecución de CI ni se mezclan con las capturas históricas del 14/10.

| Archivo local | Evidencia |
|---|---|
| `01_Formulario_UCI_Desktop.png` | Diecinueve entradas y ejemplo, antes de inferencia |
| `02_Segunda_Opinion_Desktop.png` | Reglas y resultado real del modelo con proveedor y advertencias |
| `03_Comparacion_Movil.png` | Comparación en viewport móvil real 390 x 844 |
| `04_Resultado_Modelo_Movil.png` | Resultado y límites tras desplazamiento normal |

Se retiraron únicamente los tres contenedores y las dos redes temporales cuya etiqueta coincidía con esta ejecución; la base tmpfs se descartó. Las identidades y fechas de inicio de los servicios originales fueron iguales antes, después y al terminar la limpieza. No se leyó su base de datos.

## Límites pendientes

No se realizaron llamadas reales a Azure, descarga Ollama, consulta de historial privado, refresco Power BI, aceptación, capacitación o ceremonias Scrum. Se mantienen las trece tecnologías obligatorias y sus adaptadores/configuración, con evidencia histórica distinguida de disponibilidad actual.

El score principal continúa siendo una regla de demostración. Integrar la consulta del modelo en esa pantalla mejora el recorrido, pero **no convierte un escenario UCI independiente en una segunda predicción del mismo solicitante**. Para hacerlo responsablemente se necesitan datos autorizados compatibles, entrenamiento/validación y definición de uso del resultado.

[README y recorrido](../../../../README.md) · [Arquitectura](../../desarrollo/ARQUITECTURA_Y_DATOS.md) · [QA](../../calidad/QA.md) · [Operación](../../manuales/OPERACION.md).
