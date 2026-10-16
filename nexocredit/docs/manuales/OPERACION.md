# Operación y soporte — demostración local

Actualización documental: 15/10/2026. Los recorridos antiguos conservan sus fechas; no equivalen a una ejecución nueva ni aceptación empresarial. Ver [evidencias](../evidencias/README.md) y [pendientes de entrega](../entrega/ENTREGA_DEMO.md).

## Modelo mexicano en la evaluación — 15/10/2026

1. Usar la copia académica actualizada y completar los campos habituales con datos ficticios. El bloque **Modelo mexicano · ENIF 2024** está activado en las nuevas capturas. No necesita Azure, Ollama o conexión a INEGI para evaluar.
2. Ejemplo ficticio: ingreso laboral por periodo 12000; periodicidad Mes; ingreso Fijo; presupuesto Sí; ingreso suficiente para gastos Sí; ahorros Tres meses a menos de seis meses; Tarjeta bancaria. El ingreso laboral del perfil es otra pregunta, no se copia automáticamente del ingreso mensual total. Si el ingreso por periodo supera 98000, declarar 98000 según el tope de captación ENIF; no usar 99888, que es código de rechazo.
3. Pulsar «Evaluar escenario». Primero aparece **Resultado del modelo mexicano**, después **Comparación por reglas demo**. El ejemplo produce salida asociativa `0.111645` frente a umbral `0.18`: clase `perfil_no_asociado_a_atraso`. No significa que la persona no tenga atrasos ni 11 % de probabilidad de impago. Cambiar sólo el score a 200 modifica las reglas, no ENIF.
4. Abrir «Calidad medida y procedencia»: AUC 0.605, precisión positiva 27 %, capacidad limitada. En Historial → Ver detalle se muestra el resultado guardado con modelo y SHA-256. No recalcula ni altera lo histórico. No usar ninguna salida para aprobar/rechazar créditos.
5. Si no existe crédito formal, ingreso laboral positivo o respuestas completas, desactivar este análisis. Se anuncia «Sin modelo mexicano» y se conserva la evaluación por reglas; nunca se rellenan respuestas por cero. Si el artefacto está ausente/alterado, se informa 503 y no se guarda sólo reglas fingiendo éxito del modelo. Para corregir, restaurar la versión íntegra del código y artefacto, no editar su SHA para saltar el control.

Las explicaciones anteriores siguen tratando las reglas. Ollama puede estar deshabilitado (`VALORACION_IA_PROVEEDOR=deshabilitado`) sin afectar ENIF. Azure, sus campos de keys y el laboratorio UCI se conservan. [Reproducción, población y fuentes](../../inteligencia_artificial/prediccion_mexico/README.md). La instalación existente recibió una actualización verificada el 15/10/2026, conservando datos y configuración; clonar el repositorio no actualiza otros equipos ni publicaciones de GitHub. [Evidencia](../evidencias/2026-10-15/actualizacion-local.md).

## Evaluación con IA del mismo escenario - 15/10/2026

1. Mantener Ollama abierto con el modelo instalado `llama3.1:8b`. El modo local configura `VALORACION_IA_PROVEEDOR=ollama`; Docker usa `OLLAMA_URL=http://host.docker.internal:11434`. Nunca descarga un modelo automáticamente ni necesita llave.
2. Completar los seis datos financieros ficticios habituales y guardar con «Evaluar escenario». La tarjeta **Evaluación con IA de tu escenario** comienza automáticamente; no requiere las entradas UCI ni otro botón. La primera carga puede tardar hasta tres minutos según el equipo.
3. Comparar **Resultado por reglas** con **Valoración de Ollama**. La IA analiza esa misma captura de ingresos/gastos/deuda/pagos/atraso/score, no recibe el riesgo por reglas y puede discrepar. La discrepancia exige revisión; nunca se promedian o sobrescriben los resultados.
4. Consultar factores seleccionados, valores calculados por el servidor y revisiones de un catálogo. El servidor agrega siempre revisión humana, aunque el LLM no la seleccione. No se muestran narraciones libres, cifras inventadas, porcentajes de impago, aprobaciones o rechazos.
5. Si falla, lo guardado permanece; no hay reintento automático. «Volver a intentar valoración IA» es una acción explícita; los errores del proveedor se cachean un minuto. La valoración correcta se cachea 24 horas. Hay diez valoraciones nuevas/hora/cuenta, separadas de las explicaciones anteriores, y un máximo compartido de dos generaciones Ollama simultáneas.

El navegador envía sólo UUID por `POST /api/v1/evaluaciones/{identificador}/valoracion-ia`; FastAPI recupera los datos guardados. `GET /api/v1/valoracion-ia/estado` indica configuración, no prueba conectividad. Ambas rutas exigen sesión. Sin datos financieros completos en un registro antiguo se devuelve 409: ausencia no se sustituye por cero. Sin modelo/configuración, 503; respuesta fuera de contrato, 502; espera agotada, 504; límite, 429. No hay cambio automático a Azure o plantilla fingiendo IA.

**La valoración es generativa, no un modelo estadístico de impago entrenado/validado para México.** No consulta Buró ni valida identidad. No se envían RFC, CURP, nombre, comentarios o motivos. No crea aprobaciones/pagos, no modifica evaluaciones/revisiones ni añade una migración: utiliza la caché existente con clave y cuota separadas. Para desactivarla: `VALORACION_IA_PROVEEDOR=deshabilitado` en el archivo privado y actualizar el backend, sin borrar llaves Azure. No compartir ese archivo.

El experimento UCI permanece bajo **Experimento UCI independiente (opcional)** y en Laboratorio; no es la nueva valoración de los datos MXN. El recorrido siguiente describe ese experimento adicional.

## Recorrido UCI independiente — 15/10/2026

Instalación: seguir el [README de la raíz pública](../../../README.md), con código activo en `nexocredit/`. Puede usarse cuenta local propia, documentos locales y modelo scikit-learn sin consumir Azure; Azure/Entra y sus campos de configuración siguen disponibles. No hay contraseña predeterminada ni comprobación nueva de suscripción Azure por publicar este manual.

1. Abrir `http://localhost:8080/`, iniciar sesión y usar exclusivamente datos ficticios. Para el ejemplo principal: identificador `AAAA010101AA1`, ingresos 30000, gastos 10000, deuda/pagos/atraso 0 y score 700. No usar cero para sustituir datos desconocidos; aquí son ceros intencionales del ejemplo.
2. Pulsar «Evaluar escenario» y comprobar **guardado**, margen 20000 y riesgo **Bajo** bajo `reglas-demo-v2`. La regla actual elige el mayor riesgo de score y margen, conforme al [manual de reglas](REGLAS_RIESGO_DEMO.md). Los registros históricos v1 conservan su resultado.
3. En el mismo resultado, abrir **«Segunda opinión IA (académica)»**. Su bloque «Reglas demo» corresponde al registro guardado; «Modelo académico» corresponde a otro escenario, UCI/Taiwán 2005 con importes NTD. **No evalúa la identidad ni los importes MXN del solicitante.**
4. Expandir «Capturar las 19 variables UCI del escenario ficticio» y pulsar «Cargar ejemplo UCI ficticio», o completar las 19 entradas independientes. Ese botón sólo llena el formulario: no consulta ni guarda. Revisar unidades/códigos y pulsar «Consultar segunda opinión» para ejecutar el proveedor disponible.
5. Revisar clase («Incumplimiento» o «No incumplimiento»), origen/modelo y advertencias. No son Bajo/Medio/Alto ni una probabilidad calibrada. La comparación lleva `guardada: false`; no queda en el expediente, no cambia revisiones, reglas, dashboard o Power BI y se pierde al cambiar de evaluación o recargar.

`LIMIT_BAL` es límite de crédito; `PAY_0` y `PAY_2…6` son códigos de estado de pago −2…9, no días de atraso; `BILL_AMT1…6` son saldos (admiten negativos); `PAY_AMT1…6` son pagos no negativos. Se exigen exactamente 19 enteros int32, con límite positivo. No copiar o convertir ingresos, deudas o atrasos MXN de la solicitud para completar estas variables.

El estado del modelo distingue configuración de consulta real. «Volver a comprobar proveedor» revisa el estado, no genera inferencia. Con `ML_PROVEEDOR=local`, el artefacto scikit-learn incluido no necesita Ollama, keys ni red; con `azure`, la consulta explícita puede generar consumo y requiere recursos/credenciales vigentes. `deshabilitado` o fallo no se sustituyen automáticamente por otro proveedor. Un error deja intacta la evaluación guardada; no pulsar repetidamente para intentar forzar un resultado.

Contrato técnico: `POST /api/v1/evaluaciones/{identificador}/segunda-opinion` exige sesión autorizada, UUID existente y cuerpo `{"valores": {…19 variables UCI…}}`, sin campos adicionales. Devuelve el riesgo/versión guardados y `modelo`, no persiste sus entradas/salida. 401 indica falta de sesión; 422, entrada/UUID inválidos; 404, evaluación ausente; 503, base o modelo no disponibles; 502/504, respuesta o espera del proveedor remoto. [Arquitectura y contrato](../desarrollo/ARQUITECTURA_Y_DATOS.md).

## Base operativa del 11/10/2026 — complementada por el recorrido anterior

Se conserva abajo el recorrido histórico de octubre 4. Para la versión actual, esta sección y los manuales enlazados prevalecen sobre las menciones de acceso sólo Microsoft, texto sólo en memoria, datos siempre libres o ausencia total de alertas.

- Acceso Microsoft o cuenta local habilitada, sin contraseñas en código. Al recargar se pierde la sesión local en memoria y debe iniciarse de nuevo. [Acceso, Ollama y llaves](ACCESO_LOCAL_Y_PROVEEDORES.md).
- Formulario: números válidos/acotados, pagos incluidos en gastos, sin atraso pendiente con deuda cero. La guía de score describe margen y score demo, no Buró. El RFC admite identificadores ficticios en API; la interfaz añade revisión opcional de formato/fecha contra CURP y consulta SAT manual, no identidad oficial. [RFC/CURP](REVISION_RFC_CURP.md).
- Explicación automática: Azure, Ollama o plantilla según selección explícita. Caché privada PostgreSQL 24 h y reserva durable de diez intentos/hora; error un minuto. No envío de RFC, CURP o comentarios; no reintento automático. La plantilla no es IA generativa.
- Nueva sección **Créditos y pagos**: planes ficticios ligados a evaluaciones, abonos parciales, saldos/atraso/puntualidad, alertas versionadas y eventos. Actualizar vencimientos por acción explícita; no importa Buró o depósitos ni modifica el score. [Manual completo](SEGUIMIENTO_CREDITICIO.md).
- Analista mantiene seguimiento operativo. Administrador añade consulta de la auditoría global del nuevo módulo. No se modificaron cuentas existentes; las facultades históricas fuera de seguimiento permanecen iguales.
- [Arquitectura y doce tablas](../desarrollo/ARQUITECTURA_Y_DATOS.md), [plan de mantenimiento](MANTENIMIENTO_Y_SOPORTE.md), [guía de práctica preparada](../entrega/CAPACITACION_DEMO.md). No hay acta de capacitación ni firmas generadas.

Datos de trabajo y backups siguen privados. No borrar volúmenes para resolver fallos y no copiar `.env`, dumps o cachés de Power BI al entregar. Las integraciones/evidencias históricas Azure no garantizan disponibilidad actual.

## Manual de usuario histórico — recorrido del 04/10/2026

Acceso: abrir [localhost:8080](http://localhost:8080/) y pulsar «Iniciar sesión con Microsoft». Introducir la contraseña solo en Microsoft. Se requiere cuenta autorizada del tenant configurado, ámbito access_as_user y rol Analista o Administrador. Ambos roles tienen el mismo acceso funcional actual. La interfaz comprueba la identidad contra FastAPI; mostrar el login no sustituye la validación del servidor. No compartir tokens ni claves. Si la sesión vence, volver a iniciar sesión; 403 indica permisos insuficientes. No desactivar controles para resolver un fallo.

Revisión manual: en el historial pulsar Ver detalle. Consultar los datos, elegir Pendiente, Aprobada o Rechazada, escribir el motivo y pulsar Guardar revisión demo. «Responsable autenticado» es de solo lectura y el servidor lo fija desde Entra. Revisiones antiguas pueden contener nombres declarados. El detalle conserva fechas y versiones; los datos antiguos ausentes aparecen como No capturado. Cambiar estado no cambia el riesgo ni autoriza un crédito real. Usar exclusivamente datos ficticios.

Si el guardado falla, reintentar sin cambiar los campos conserva la clave de solicitud y evita duplicar la revisión. Si aparece conflicto, copiar cualquier observación pendiente, cerrar y abrir el detalle para revisar la versión actual antes de enviar otro cambio. No cerrar el panel con datos sin guardar si se desean conservar.

API de revisión: POST /api/v1/evaluaciones/{id}/revisiones recibe id UUID de reintento, version_anterior, estado, responsable (1–120 caracteres) y observaciones (1–2000). Por compatibilidad el contrato admite responsable, pero el servidor sustituye su valor por la identidad verificada; no permite suplantarlo. Rechaza textos vacíos, estados ajenos y versiones desactualizadas; devuelve 404 si no existe la evaluación y 503 ante indisponibilidad. La migración 002 agrega una tabla sin borrar evaluaciones existentes. El historial no sustituye una auditoría operativa completa de lecturas, accesos y acciones.

Dashboard: debajo del formulario aparecen los indicadores de todas las evaluaciones. Elegir fechas y riesgo, y pulsar Aplicar / actualizar; Limpiar filtros regresa al conjunto completo. Los filtros solo afectan ese panel, no el historial. Las fechas se interpretan en UTC, incluyendo ambos días. Al guardar una evaluación el panel se actualiza respetando los filtros activos. El total cuenta evaluaciones, no personas. La deuda promedio usa únicamente valores capturados (incluye ceros); Sin datos indica ausencia, no deuda cero. Los niveles son reglas demo, no tasas reales de incumplimiento. Si falla la conexión, restablecer los servicios y pulsar Aplicar / actualizar.

1. Iniciar Docker siguiendo [README](../../README.md).
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
- Power BI: abrir el proyecto PBIP y pulsar Actualizar para obtener nuevas evaluaciones. La prueba Desktop del 30/09/2026 usó 5 evaluaciones; la prueba web del 04/10/2026 terminó con 7. No afirmar que el reporte importado ya tiene 7 sin refrescar y comprobar. Ver [manual Power BI](../../analitica/reportes_power_bi/README.md).

## Manual técnico

El formulario incluye deuda_actual, pagos_mensuales_creditos y dias_atraso_actual. Capturar cero cuando no existan deudas/pagos/atrasos; no usar cero como sustituto de datos desconocidos. Los importes permiten hasta 1,000,000,000 MXN y los días deben ser enteros entre 0 y 36,500 (límites técnicos, no políticas crediticias). Incluir pagos de créditos dentro de gastos mensuales; no se restan otra vez. Los nuevos campos se guardan en solicitud JSONB y se consultan mediante el endpoint de detalle o SQL, pero aún no modifican el scoring. Los registros anteriores conservan sus datos y no se rellenan con ceros.

Docker: abrir Docker Desktop y ejecutar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar` desde la carpeta interior. El lanzador abre localhost:8080, origen requerido por Entra. No necesita iniciar Vite ni FastAPI por separado. Las acciones `estado`, `logs` y `pruebas` permiten diagnóstico; no compartir logs sin revisar que no contengan datos privados. `detener` conserva el volumen, pero el volumen no es un respaldo. Ver [operación Docker](../../infraestructura/contenedores_docker/README.md).

frontend/src/App.jsx coordina la pantalla; frontend/src/evaluacion_crediticia/componentes contiene formulario y resultado; frontend/src/evaluacion_crediticia/servicios/creditApi.js realiza las peticiones; frontend/src/main.jsx inicia React. backend/app/main.py configura la API; rutas_api/routes.py define rutas, validacion_datos/credito.py valida entradas y evaluacion_crediticia/scoring.py evalúa las reglas. Configuración: frontend/.env.example y variable CORS_ORIGINS. GET / comprueba disponibilidad; POST /api/v1/evaluar ejecuta reglas; /docs permite inspeccionar el contrato. backend/requirements.txt declara dependencias Python; frontend/package-lock.json fija las dependencias JavaScript. Aún falta fijar dependencias Python exactas para despliegue reproducible.

## Plan de mantenimiento propuesto

Herramientas locales implementadas: `operacion/pruebas/Probar programacion.cmd` ejecuta las suites en PostgreSQL efímero aislado; `operacion/respaldos/Respaldar PostgreSQL.cmd` crea un respaldo manual privado bajo `.local/respaldos_postgresql/`; `operacion/respaldos/Probar restauracion PostgreSQL.cmd` utiliza un respaldo local y verifica su restauración en un contenedor temporal protegido, nunca sobre la base original. El ensayo del 04/10/2026 concilió tres tablas, filas, huellas, columnas, restricciones y vistas. Dumps sin cifrado ni roles globales/ACL: mantenerlos privados y no publicarlos. Ver [resultado y límites](../evidencias/2026-10-04/cierre-tecnico.md).

Nivel 1: asistencia de captura, conectividad y registro de incidentes sin información sensible. Nivel 2: diagnóstico de API, base de datos e integraciones. Nivel 3: correcciones de código/modelo, seguridad y escalamiento a proveedores. Personas y tiempos de atención pendientes de asignación con PluriOne.

Antes de producción: acordar cifrado, respaldos automáticos, retención, objetivos de recuperación y ejercicios completos; monitorear disponibilidad, errores, latencia y deriva del modelo; documentar rollback; revisar dependencias y permisos periódicamente. El ensayo manual local no acredita estos controles productivos.

Plantilla de incidente: ID, fecha, entorno, impacto, pasos de reproducción con datos ficticios, responsable, diagnóstico, solución, validación y cierre.

## Capacitación propuesta y acta pendiente

Agenda: alcance/limitaciones, captura, interpretación, revisión humana, acceso y reporte de incidentes. Práctica: tres escenarios ficticios y un caso inválido. Evidencia: asistencia, ejercicios y dudas resueltas.

Acta por completar tras la sesión: fecha, instructor, asistentes, versión utilizada, ejercicios, resultados, observaciones y conformidad. Capacitación aún no realizada.

