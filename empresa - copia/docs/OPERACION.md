# Operación y soporte — demostración local

Actualización documental: 04/10/2026. Refleja código y pruebas existentes; no implica una nueva ejecución ni aceptación empresarial. Ver [evidencias](evidencias/README.md) y [pendientes de entrega](ENTREGA_DEMO.md).

## Manual de usuario del prototipo

Acceso: abrir [localhost:8080](http://localhost:8080/) y pulsar «Iniciar sesión con Microsoft». Introducir la contraseña solo en Microsoft. Se requiere cuenta autorizada del tenant configurado, ámbito access_as_user y rol Analista o Administrador. Ambos roles tienen el mismo acceso funcional actual. La interfaz comprueba la identidad contra FastAPI; mostrar el login no sustituye la validación del servidor. No compartir tokens ni claves. Si la sesión vence, volver a iniciar sesión; 403 indica permisos insuficientes. No desactivar controles para resolver un fallo.

Revisión manual: en el historial pulsar Ver detalle. Consultar los datos, elegir Pendiente, Aprobada o Rechazada, escribir el motivo y pulsar Guardar revisión demo. «Responsable autenticado» es de solo lectura y el servidor lo fija desde Entra. Revisiones antiguas pueden contener nombres declarados. El detalle conserva fechas y versiones; los datos antiguos ausentes aparecen como No capturado. Cambiar estado no cambia el riesgo ni autoriza un crédito real. Usar exclusivamente datos ficticios.

Si el guardado falla, reintentar sin cambiar los campos conserva la clave de solicitud y evita duplicar la revisión. Si aparece conflicto, copiar cualquier observación pendiente, cerrar y abrir el detalle para revisar la versión actual antes de enviar otro cambio. No cerrar el panel con datos sin guardar si se desean conservar.

API de revisión: POST /api/v1/evaluaciones/{id}/revisiones recibe id UUID de reintento, version_anterior, estado, responsable (1–120 caracteres) y observaciones (1–2000). Por compatibilidad el contrato admite responsable, pero el servidor sustituye su valor por la identidad verificada; no permite suplantarlo. Rechaza textos vacíos, estados ajenos y versiones desactualizadas; devuelve 404 si no existe la evaluación y 503 ante indisponibilidad. La migración 002 agrega una tabla sin borrar evaluaciones existentes. El historial no sustituye una auditoría operativa completa de lecturas, accesos y acciones.

Dashboard: debajo del formulario aparecen los indicadores de todas las evaluaciones. Elegir fechas y riesgo, y pulsar Aplicar / actualizar; Limpiar filtros regresa al conjunto completo. Los filtros solo afectan ese panel, no el historial. Las fechas se interpretan en UTC, incluyendo ambos días. Al guardar una evaluación el panel se actualiza respetando los filtros activos. El total cuenta evaluaciones, no personas. La deuda promedio usa únicamente valores capturados (incluye ceros); Sin datos indica ausencia, no deuda cero. Los niveles son reglas demo, no tasas reales de incumplimiento. Si falla la conexión, restablecer los servicios y pulsar Aplicar / actualizar.

1. Iniciar Docker siguiendo [README](../README.md).
2. Abrir localhost:8080, iniciar sesión con Microsoft y usar exclusivamente escenarios ficticios.
3. Capturar identificador ficticio, ingresos mayores a cero, gastos, deuda y pagos no negativos, días de atraso enteros no negativos y score entero entre 0 y 1000. Capturar cero solo cuando corresponda, no para reemplazar un dato desconocido. Los gastos incluyen pagos de créditos.
4. Pulsar Evaluar escenario. Consultar margen y factores. El nivel depende exclusivamente de reglas demo: Bajo si margen > 15,000 y score >= 680; Medio si no cumple Bajo pero margen > 7,000; Alto en otro caso. Tras el guardado se solicita automáticamente la explicación Azure OpenAI con la guía demo de Search. Puede generar consumo; revisar humanamente el texto. Si falla IA, el guardado y riesgo no cambian. La explicación no se conserva después de recargar.
5. Con PostgreSQL configurado, cada evaluación guarda entradas, resultado, fecha y versión; el historial permanece al recargar. Cambiar un dato limpia el resultado del formulario, pero conserva lo guardado. Sin base configurada se indica expresamente que no se guardó.
6. Si PostgreSQL no está disponible, se muestra un error de guardado. Revisar los servicios Docker; no iniciar la base nativa para sustituir el volumen Docker. Reenviar el mismo formulario conserva la clave de reintento durante la sesión para evitar duplicados; editar un campo inicia otra solicitud.

El campo RFC acepta texto libre; no valida estructura, identidad ni registro fiscal. Si aparece un error de validación, revisar campos. Si falla conexión, revisar salud de Docker y API, sin revelar configuración privada. CORS no configura el retorno Entra: cambiar de puerto/origen requiere registros y aplicación acordes, no basta modificar CORS_ORIGINS.

## Otras secciones de la aplicación

- Azure ML: abrir el formulario UCI y cargar el ejemplo ficticio. Son 19 enteros, importes NTD de un experimento de Taiwán, no el formulario MXN. Consultar el modelo usa Azure y puede generar consumo. El aviso distingue configuración, espera, éxito y fallo del último intento de esa sesión; recargar restaura el aviso inicial. La clase no es probabilidad ni decisión de crédito, no se guarda en el historial. La etiqueta local no verifica la versión remota del modelo.
- Documentos: catálogo de 2 guías / 14 secciones recuperadas desde Azure AI Search. Abrir «Leer guía» o buscar palabras clave sin datos personales. Son documentos de demostración, no políticas oficiales. Si Azure falla se informa; no se inventa contenido de respaldo.
- Indicadores financieros: Banxico FIX/tasa y Banco Mundial inflación/PIB, con periodo, unidad, procedencia y hora de consulta diferenciados. «Volver a consultar» no fuerza una llamada externa: la caché dura una hora para datos válidos y un minuto para fallos. No son historial crediticio privado ni datos en tiempo real y no cambian el riesgo. Ambos proveedores estuvieron disponibles el 04/10/2026.
- Power BI: abrir el proyecto PBIP y pulsar Actualizar para obtener nuevas evaluaciones. La prueba Desktop del 30/09/2026 usó 5 evaluaciones; la prueba web del 04/10/2026 terminó con 7. No afirmar que el reporte importado ya tiene 7 sin refrescar y comprobar. Ver [manual Power BI](../analitica/reportes_power_bi/README.md).

## Manual técnico

El formulario incluye deuda_actual, pagos_mensuales_creditos y dias_atraso_actual. Capturar cero cuando no existan deudas/pagos/atrasos; no usar cero como sustituto de datos desconocidos. Los importes permiten hasta 1,000,000,000 MXN y los días deben ser enteros entre 0 y 36,500 (límites técnicos, no políticas crediticias). Incluir pagos de créditos dentro de gastos mensuales; no se restan otra vez. Los nuevos campos se guardan en solicitud JSONB y se consultan mediante el endpoint de detalle o SQL, pero aún no modifican el scoring. Los registros anteriores conservan sus datos y no se rellenan con ceros.

Docker: abrir Docker Desktop y ejecutar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar` desde la carpeta interior. El lanzador abre localhost:8080, origen requerido por Entra. No necesita iniciar Vite ni FastAPI por separado. Las acciones `estado`, `logs` y `pruebas` permiten diagnóstico; no compartir logs sin revisar que no contengan datos privados. `detener` conserva el volumen, pero el volumen no es un respaldo. Ver [operación Docker](../infraestructura/contenedores_docker/README.md).

frontend/src/App.jsx coordina la pantalla; frontend/src/evaluacion_crediticia/componentes contiene formulario y resultado; frontend/src/evaluacion_crediticia/servicios/creditApi.js realiza las peticiones; frontend/src/main.jsx inicia React. backend/app/main.py configura la API; rutas_api/routes.py define rutas, validacion_datos/credito.py valida entradas y evaluacion_crediticia/scoring.py evalúa las reglas. Configuración: frontend/.env.example y variable CORS_ORIGINS. GET / comprueba disponibilidad; POST /api/v1/evaluar ejecuta reglas; /docs permite inspeccionar el contrato. backend/requirements.txt declara dependencias Python; frontend/package-lock.json fija las dependencias JavaScript. Aún falta fijar dependencias Python exactas para despliegue reproducible.

## Plan de mantenimiento propuesto

Herramientas locales implementadas: `Probar programacion.cmd` ejecuta las suites en PostgreSQL efímero aislado; `Respaldar PostgreSQL.cmd` crea un respaldo manual privado bajo `.local/respaldos_postgresql/`; `Probar restauracion PostgreSQL.cmd` utiliza un respaldo local y verifica su restauración en un contenedor temporal protegido, nunca sobre la base original. El ensayo del 04/10/2026 concilió tres tablas, filas, huellas, columnas, restricciones y vistas. Dumps sin cifrado ni roles globales/ACL: mantenerlos privados y no publicarlos. Ver [resultado y límites](evidencias/2026-10-04/cierre-tecnico.md).

Nivel 1: asistencia de captura, conectividad y registro de incidentes sin información sensible. Nivel 2: diagnóstico de API, base de datos e integraciones. Nivel 3: correcciones de código/modelo, seguridad y escalamiento a proveedores. Personas y tiempos de atención pendientes de asignación con PluriOne.

Antes de producción: acordar cifrado, respaldos automáticos, retención, objetivos de recuperación y ejercicios completos; monitorear disponibilidad, errores, latencia y deriva del modelo; documentar rollback; revisar dependencias y permisos periódicamente. El ensayo manual local no acredita estos controles productivos.

Plantilla de incidente: ID, fecha, entorno, impacto, pasos de reproducción con datos ficticios, responsable, diagnóstico, solución, validación y cierre.

## Capacitación propuesta y acta pendiente

Agenda: alcance/limitaciones, captura, interpretación, revisión humana, acceso y reporte de incidentes. Práctica: tres escenarios ficticios y un caso inválido. Evidencia: asistencia, ejercicios y dudas resueltas.

Acta por completar tras la sesión: fecha, instructor, asistentes, versión utilizada, ejercicios, resultados, observaciones y conformidad. Capacitación aún no realizada.

