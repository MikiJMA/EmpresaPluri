# Entrega de demostración — NexoCredit

Corte documental: 04/10/2026. Preparado a partir del código local y de comprobaciones registradas; no es un acta firmada ni aprobación del asesor. No acredita las 500 horas propuestas, ejecución de sprints ni disponibilidad permanente de Azure. La preparación inicial no publicó código ni creó recursos cloud. Seguimiento posterior: [cierre técnico NexoCredit](evidencias/2026-10-04/cierre-tecnico.md), suites 69 backend/48 frontend, respaldo/restauración aislada y metadatos ML; la CI se registrará por commit cuando termine.

## Qué se puede demostrar

- Acceso Microsoft Entra ID y rechazo de rutas de negocio sin token.
- Captura ficticia, reglas demo, guardado PostgreSQL, historial y revisión manual con identidad verificada, motivo y versiones. Reintentos sin duplicación y recuperación tras recargar.
- Explicación automática Azure OpenAI con guía DEM-02 de Azure AI Search, sin enviar RFC ni modificar el riesgo. Catálogo de 2 guías / 14 secciones y búsqueda textual.
- Laboratorio Azure ML separado: 19 entradas UCI en NTD, respuesta booleana y aviso correcto de la consulta de esa sesión. No persiste escenarios ni sustituye reglas demo.
- Dashboard React con filtros, totales, promedios que distinguen ausencia de cero y distribución de riesgos. Indicadores públicos de Banxico y Banco Mundial con periodo, unidad, fuente y caché.
- Power BI Desktop conectado a una vista de lectura limitada; 11 visuales y 96 comparaciones SQL–DAX comprobados el 30/09/2026. No publicado en cloud.
- Docker local y workflow GitHub Actions existente. La ejecución remota aprobada documentada corresponde al 23/09/2026, no al árbol local actual.

Las 13 tecnologías obligatorias y su estado individual se consultan en [REQUISITOS_TECNOLOGICOS.md](../REQUISITOS_TECNOLOGICOS.md). Scrum sigue sin ejecución acreditada: el backlog organizado no sustituye reuniones, revisión ni retrospectiva.

## Carpeta de revisión

1. [README principal](../README.md): arranque y límites.
2. [Manual de operación](OPERACION.md): acceso, captura, consulta, errores y Power BI.
3. [Plan y requisitos funcionales](PLAN_PROYECTO.md): alcance objetivo frente a implementación parcial/demo.
4. [Índice de evidencias](evidencias/README.md): enlaces a pruebas, capturas y métricas.
5. [QA](QA.md): resultados actuales y comprobaciones históricas con sus fechas.
6. [Backlog de cierre](../gestion_proyecto/scrum/BACKLOG_CIERRE.md): acciones pendientes y condiciones de cierre, sin horas ni responsables inventados.

## Resultados registrados, no una nueva ejecución

El 04/10/2026 se aprobaron 57 pruebas backend, incluyendo 5 con PostgreSQL real y esquemas aislados. Las respuestas de proveedores en los tests son simuladas. Tras corregir el aviso ML se aprobaron 42 pruebas frontend, ESLint y Vite en una construcción Docker. Son suites separadas, no una sola ejecución combinada ni una nueva validación GitHub Actions.

Las consultas reales autenticadas se documentan por separado en [prueba-e2e.md](evidencias/2026-10-04/prueba-e2e.md). La muestra web terminó con 7 evaluaciones: Bajo 5, Medio 1, Alto 1; margen promedio 17,857.14 MXN; deuda promedio informada 10,000.10 MXN sobre 5 capturas. Son resultados históricos de una muestra ficticia, no cifras permanentes. La muestra Power BI comprobada el 30/09/2026 tenía 5 evaluaciones y necesita actualizarse para reflejar nuevas filas.

## Guion propuesto para revisión con el asesor

Este guion aún no acredita una sesión de capacitación ni aceptación.

1. Iniciar Docker y abrir localhost:8080; el usuario autorizado completa el login Microsoft.
2. Mostrar historial y dashboard existentes, incluyendo filtros y su limpieza, sin agregar registros innecesarios.
3. Si se acuerda una nueva captura, usar identificador ficticio, ingresos 30,000, gastos 10,000, deuda 0, pagos 0, atraso 0 y score 700. Avisar que guardará una evaluación y solicitará automáticamente IA con posible consumo. Esperar margen 20,000 y riesgo demo Bajo; revisar texto y cita DEM-02.
4. Abrir únicamente el detalle ficticio y explicar la revisión manual e identidad del responsable. Guardar una revisión solo si forma parte de la práctica acordada; no es aprobación de crédito real.
5. Mostrar guías y fuentes económicas; diferenciar hora de consulta, periodo del dato y caché. No introducir datos personales en la búsqueda.
6. Mostrar la captura ML ya guardada. Una consulta nueva debe usar solo el ejemplo ficticio UCI y puede generar consumo; no afirmar que verifica la versión efectiva del modelo.
7. Abrir Power BI Desktop y, si se requiere una demostración actual, pulsar Actualizar y comparar con la base. No publicar ni compartir credenciales.
8. Revisar limitaciones y pendientes. Registrar fecha, participantes, observaciones y decisión del asesor solo después de que ocurran.

## Qué no está cerrado

- Nueva CI remota del código actual, hasta registrar resultado por commit. Los tests unitarios frontend ya están incluidos en el workflow.
- Comparación binaria del modelo remoto con el artefacto académico; identidad registrada y versión verificadas mediante metadatos independientes el 04/10/2026, no por la etiqueta local.
- Recuperación productiva completa; respaldo manual y restauración de tres tablas en destino aislado ya comprobados, sin sobrescribir la base de trabajo.
- Evidencias reales de Scrum, capacitación y aceptación del alcance demo por el asesor.
- Sistema crediticio final: datos representativos autorizados, políticas oficiales, historial crediticio privado, análisis efectivo de deuda/pagos, validación del modelo, alertas y seguridad/operación de producción.

Una demo funcional no cierra estos requisitos del sistema final. El candidato UCI detectó 32,01 % de los incumplimientos en su conjunto de prueba; no es un modelo validado para clientes de PluriOne. No hay probabilidad calibrada ni autorización automática de crédito.

## Manejo seguro de la entrega

Entregar documentación y evidencias revisadas, no copiar indiscriminadamente toda la carpeta. Excluir archivos .env, claves, tokens, sessionStorage, dumps de base, cachés con información privada y credenciales de Power BI. Los ejemplos deben seguir siendo ficticios. No trasladar secretos al repositorio ni a capturas. Conservar las evidencias históricas y añadir seguimientos; no reemplazar un fallo previo por un éxito sin fecha y explicación.
