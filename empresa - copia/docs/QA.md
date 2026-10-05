# Reporte QA — prototipo 0.1

## Cómo leer este reporte

Las secciones posteriores son registros históricos con su fecha: las menciones antiguas de falta de Entra, Power BI, Banxico o conexión ML no describen el estado actual si una comprobación posterior las sustituye. Consultar [estado tecnológico actualizado](../REQUISITOS_TECNOLOGICOS.md), [entrega demo](ENTREGA_DEMO.md) e [índice de evidencias](evidencias/README.md). Esta organización documental no ejecuta de nuevo las pruebas, no acredita Scrum ni publica cambios remotos.

## Revisión documental — 4 de octubre de 2026

Publicación posterior autorizada: rama `codex/cierre-nexocredit-demo`, sin cambiar `main`. [CI real del cierre](evidencias/2026-10-04/github-actions.md) aprobada para el commit de código `19223ae`: 69 backend y 48 frontend, sin omisiones; migraciones, lanzadores, audit, lint y build aprobados. No constituye despliegue productivo.

Seguimiento posterior de programación y marca: [cierre técnico NexoCredit](evidencias/2026-10-04/cierre-tecnico.md). 69 pruebas backend/PostgreSQL y 48 frontend aprobadas, 0 omitidas; lint/build y tres archivos de pruebas PowerShell aprobados. Respaldo/restauración aislada de tres tablas y metadatos remotos ML comprobados por separado, con sus límites. Los apartados siguientes conservan los conteos históricos; no describen nuevas ejecuciones CI.

- README, matriz tecnológica, manual, plan y módulos actualizados según el código y la evidencia registrada. Entrega, índice de evidencias y backlog de cierre preparados; Scrum y aceptación siguen sin acreditarse.
- 21 documentos revisados mediante comprobación de 89 enlaces locales: destinos y anclas presentes, sin fallos. Git diff --check aprobado; sin coincidencias de las afirmaciones obsoletas revisadas en los documentos de estado actual.
- Evidencias originales conservadas, con seguimiento de la corrección ML y separación de muestras Power BI/web. No se ejecutaron nuevas pruebas funcionales ni se modificaron código, contenedores, datos, permisos, secretos o servicios remotos durante esta actualización documental.

## Corrección del aviso Azure ML — 4 de octubre de 2026

- El laboratorio distingue configuración inicial, consulta en curso, respuesta correcta y último intento fallido. Solo una respuesta válida con clase booleana acredita la consulta de esa sesión; no verifica la versión remota del modelo ni acredita producción.
- 42 pruebas frontend aprobadas en la construcción Docker, incluidas 8 nuevas de mensajes y contrato. ESLint y compilación Vite aprobados. El intento de ejecutar Node directamente en el host fue bloqueado por permisos de creación de procesos; la suite completa sí se ejecutó en Docker.
- Se aplicó únicamente la imagen frontend. PostgreSQL y backend conservaron sus contenedores; no se modificaron datos ni secretos.
- Comprobación autenticada en localhost con un ejemplo ficticio: se observó «Consultando Azure ML», seguido de «Conexión con Azure ML comprobada en esta sesión» y la clase «No incumplimiento». El dashboard conservó 7 evaluaciones y la consola no registró errores. Fallos y respuestas inválidas cubiertos por pruebas automáticas, no provocados contra el servicio real.
- Captura local `evidencias/2026-10-04/azure-ml-estado-corregido.jpg`, excluida del repositorio público, y [seguimiento de la prueba integral](evidencias/2026-10-04/prueba-e2e.md#corrección-posterior-del-aviso-azure-ml).

## Prueba integral autenticada — 4 de octubre de 2026

Flujo local comprobado en el navegador de Codex con sesión Entra iniciada por el usuario: validación, evaluación ficticia, explicación automática Azure OpenAI con guía Azure AI Search, historial, revisión manual, reenvío sin duplicados, persistencia tras recargar, filtros, búsqueda documental, indicadores Banxico/Banco Mundial y consulta real Azure ML desde la interfaz. 57 pruebas backend/PostgreSQL y 34 frontend aprobadas; lint y compilación aprobados. Se conserva un registro ficticio adicional, no una solicitud real.

Consultar [evidencia, cifras y límites de la prueba](evidencias/2026-10-04/prueba-e2e.md). Sustituye las menciones históricas de Banxico rechazado y conexión ML sin probar; no verifica la versión remota del modelo ni acredita producción. La observación visual del mensaje «conexión pendiente» se corrigió posteriormente, como consta en el apartado anterior. No se ejecutó una nueva validación remota de GitHub Actions.

## APIs financieras y recuperación de arranque — 03 de octubre de 2026

- Fuente real Banco Mundial consultada desde Docker: México, inflación FP.CPI.TOTL.ZG = 3.80668650726485 % anual y crecimiento NY.GDP.MKTP.KD.ZG = 0.561683456144578 % anual, ambas del año 2025. Son contexto público, no datos en tiempo real ni una predicción de riesgo. Segunda consulta al servicio reutiliza caché por ambas fuentes.
- Banxico: token configurado en el servidor sin exponer su valor. La llamada real SIE respondió HTTP 400 y declaró token no válido; no se acredita conexión operativa ni se incorporan valores simulados. Pendiente sustituir el token mediante el configurador privado y validar la respuesta real.
- Incidente: PostgreSQL detenido con salida 0; API `/` HTTP 200 pero lectura de base fallida y backend unhealthy. Se encendió el contenedor PostgreSQL existente y se comprobó recuperación de lectura/control de salud. PostgreSQL, backend y frontend saludables; volumen y evaluaciones existentes conservados.
- Corrección del configurador: inicia y espera PostgreSQL sin recrearlo, después recrea únicamente la API; modo `-UsarTokenGuardado` no pide ni modifica credenciales. Repetición real aprobada. Mensajes de progreso en stderr de Docker no interrumpen PowerShell 5.1; resultado determinado por código de salida.
- 13 pruebas de APIs financieras aprobadas: sesión requerida, destinos y privacidad, fuentes independientes, país/series/fechas/números inválidos, ausencia vs cero/negativo, cuotas/HTTP/JSON/timeout/TLS, caché/expiración/concurrencia y rechazo HTTP 400 sanitizado. Son pruebas con proveedores simulados; se distinguen de las consultas reales anteriores.
- Pruebas PowerShell sin secretos aprobadas: preservación del .env con muestra ficticia, duplicados/entradas inválidas, orden/protección de la base; simulación de progreso stderr, fallo del primer/segundo paso, interrupción antes de recrear API si falla la base y restauración de preferencias.
- Imagen backend reconstruida y suite completa aprobada dentro de un contenedor temporal: 57 pruebas, incluyendo PostgreSQL real con esquemas de prueba aislados. El script público de validación de documentos se montó en solo lectura para la prueba que lo requiere; no se copiaron credenciales. Se aplicó la nueva imagen con `-UsarTokenGuardado`, sin recrear PostgreSQL.
- No se modificaron reglas de riesgo ni se consultó crédito privado. Revisión visual autenticada continúa pendiente por el bloqueo de control de Windows documentado en el chat; no se reanudó ese control.

## Power BI Desktop local — 30 de septiembre de 2026

Este apartado sustituye las menciones anteriores de Power BI local pendiente; no cambia el estado de las demás tecnologías ni acredita un despliegue de producción.

- Proyecto `analitica/reportes_power_bi/PluriOne_Riesgo_Crediticio.pbix.pbip` abierto en Desktop. La captura enviada por el usuario confirma la actualización de 3 a 5 evaluaciones; los 11 visuales del dashboard se muestran sin errores. Revisión adicional mediante control nativo de la aplicación.
- Validación posterior al guardado: 19 archivos JSON de definición pasan los esquemas oficiales de Microsoft (9 esquemas descargados); referencias de medidas/columnas y posiciones dentro de la página correctas. TMDL deserializado con la biblioteca de Power BI: 3 tablas, 12 columnas de datos y 6 medidas en Consulta1. No se confunde esta validación de archivos con ejecución DAX.
- Comparación de las 6 medidas ejecutadas en el modelo abierto frente a SQL real: 16 contextos (sin filtro, 3 riesgos, 3 estados de revisión y 9 combinaciones), 96 comparaciones sin diferencias. Consultas de lectura local; lector limitado a la vista de reportes, con acceso a tablas originales rechazado.
- Se detectó cobertura en blanco cuando había evaluaciones sin dato de deuda. Corrección limitada a dos medidas de conteo: `COALESCE(COUNTROWS('Consulta1'), 0)` y `COALESCE(COUNT('Consulta1'[deuda_actual]), 0)`. Promedios sin cambios; deuda ausente conserva NULL/BLANK, deuda capturada como cero se incluye. Cobertura sin evaluaciones permanece indefinida/en blanco.
- Controles probados en Desktop: Medio (1 registro, deuda 0.00, cobertura 100 %); Alto (1, deuda ausente, cobertura 0 %); Aprobada (1, deuda ausente, cobertura 0 %); Pendiente (4, margen promedio 16,250.00 MXN, cobertura 75 %); Bajo + Pendiente (2, deuda promedio 25,000.25 MXN, cobertura 100 %). Gráficos y tabla de detalle responden. Al limpiar ambos filtros vuelve el total de 5.
- Muestra sin filtros: 5 evaluaciones; margen promedio 17,000.00 MXN; ingresos promedio 30,000.00 MXN; deuda promedio informada 16,666.83 MXN; 3 registros con dato de deuda; cobertura 60 %. Riesgos: Bajo 3, Medio 1, Alto 1. Revisión: Pendiente 4, Aprobada 1. Importes calculados sin abreviación; las tarjetas muestran miles redondeados.
- Guardado confirmado en Desktop y en archivos PBIP/TMDL/caché. Se conservó la página original, se dejó el resumen sin filtros y no se modificaron evaluaciones ni revisiones PostgreSQL. Sin publicación, cambio de permisos ni gateway. Las cifras corresponden solo a esta muestra ficticia.
- Herramientas repetibles: `verificar_reporte.mjs`, `verificar_modelo.ps1`, `scripts/verificar_powerbi.py` y `verificar_dax.ps1`; comandos y límites en `analitica/reportes_power_bi/README.md`.

## GitHub Actions — 23 de septiembre de 2026

Workflow publicado en la raíz Git. Ejecución https://github.com/MikiJMA/EmpresaPluri/actions/runs/35911875318 del commit d3cd93d finalizada con success en ambos trabajos: backend (PostgreSQL temporal, migraciones repetidas y suite unittest) y frontend (npm ci, ESLint y Vite). La instalación limpia de npm pasó en GitHub; esto no confirma la corrección del certificado de la red local. No hay despliegue automático ni uso de credenciales de producción.

## Detalle y revisión manual

- 15 pruebas backend aprobadas con PostgreSQL real, incluyendo estado inicial pendiente, guardado de revisiones, reintento idempotente, conflicto de versión/clave, historial conservado, validación de campos, 404 y evaluación original sin cambios.
- ESLint y Vite aprobados. Migración aditiva aplicada en Docker.
- Chrome: apertura del detalle, ausencia de datos antiguos, guardado de revisión ficticia, persistencia tras recargar, cierre del panel y vista móvil sin desbordamiento ni errores JavaScript. Se conserva una evaluación PRUEBA-REVISION con sufijo temporal para evidencia.
- Pendientes: identidad verificada, permisos y auditoría de producción. Estados de revisión exclusivamente demostrativos.

## Dashboard local

- 14 pruebas backend aprobadas con PostgreSQL: resumen vacío, totales sobre 12 registros (sin límite de página), tres riesgos, promedio de deuda excluyendo ausencias e incluyendo cero, fechas inclusivas UTC, límite de medianoche y filtros combinados e inválidos.
- ESLint y Vite aprobados. Chrome: concordancia del total con API, filtro por riesgo, vacío, rango inválido, limpiar, fallo 503 y recuperación. Capturas escritorio/móvil revisadas; sin desbordamiento horizontal ni errores JavaScript.
- Dashboard React operativo; Power BI, alertas y predicción permanecen pendientes.

## Campos crediticios — 22 de septiembre de 2026

- 13 pruebas aprobadas dentro de Docker con PostgreSQL real: compatibilidad de solicitudes anteriores, importes no negativos, límites técnicos, días enteros, persistencia de los tres campos y conflicto al cambiar días con la misma clave de reintento.
- ESLint y Vite aprobados con dependencias locales; imágenes reconstruidas usando el frontend precompilado por el bloqueo de certificados npm documentado.
- Prueba Chrome en 8080: rechazo de días fraccionarios, captura y guardado de deuda/pagos/atraso, lectura exacta mediante detalle, historial después de recargar y ausencia de errores JavaScript. Se conserva un escenario ficticio PRUEBA-CAMPOS con sufijo temporal.
- Reglas demo sin modificaciones; estos campos no acreditan un modelo predictivo ni el análisis completo del historial de pagos.

## Verificación Docker del 17 de septiembre de 2026

- Construcción de imágenes completada; ESLint y Vite aprobados durante la construcción.
- PostgreSQL, backend y frontend saludables; migraciones finalizadas con código 0.
- 10 pruebas aprobadas dentro del backend con PostgreSQL real y esquemas temporales aislados. La prueba CORS utiliza el origen configurado para cada entorno.
- Chrome en http://127.0.0.1:8080/: evaluación ficticia PRUEBA-DOCKER guardada, reenvío sin duplicados e historial conservado al recargar, sin errores JavaScript. Capturas de escritorio y móvil revisadas.
- Se reinició PostgreSQL y se consultó nuevamente el historial: el registro ficticio permaneció.
- No hay archivos .env en /app/backend de la imagen. La base y el backend no exponen puertos al host; la web se publica solo en loopback.
- La instalación y los datos locales no se modificaron. Pendientes: respaldos, recuperación completa, autenticación, endurecimiento y despliegue de producción.

## Verificación PostgreSQL del 17 de septiembre de 2026

- 10 pruebas aprobadas con RUN_POSTGRES_TESTS=1 y PostgreSQL real: reglas, validación, CORS con Idempotency-Key, falta de configuración, fallos de conexión, guardado y lectura desde otra conexión, reintentos idempotentes, conflicto 409, detalle 404, paginación, migraciones repetibles y rollback.
- Las pruebas de persistencia utilizan esquemas temporales aislados y los eliminan al finalizar.
- ESLint y compilación Vite aprobados con el historial incorporado.
- Navegador Chrome: guardado de una evaluación ficticia, reenvío sin duplicarla e historial conservado tras recargar; sin errores JavaScript. Se revisaron vistas de escritorio y móvil.
- Se conserva una evaluación identificada como PRUEBA-POSTGRES-LOCAL para demostrar el historial. No corresponde a una persona real.
- Continúan pendientes respaldos/restauración, seguridad de usuarios, carga y precisión predictiva. Las notas siguientes corresponden a verificaciones anteriores a la persistencia.

## Registros iniciales históricos

Los apartados siguientes conservan las primeras verificaciones y pendientes del prototipo, anteriores a las integraciones actuales. No deben interpretarse como estado vigente; las evidencias fechadas más arriba y REQUISITOS_TECNOLOGICOS.md los sustituyen donde corresponda.

### Verificaciones ejecutadas inicialmente

- npm run build: aprobado; Vite generó dist correctamente.
- npm run lint: aprobado; ESLint no reportó errores.

### Pruebas preparadas inicialmente

En backend/tests/test_api.py: evaluación explicada, límites de reglas (margen 15000 y 7000), score bajo, margen negativo, entradas inválidas y rechazo CORS de origen ajeno.

Backend: dependencias instaladas y 4 pruebas aprobadas mediante unittest (incluyen múltiples escenarios). Starlette emite una advertencia de futura migración de httpx a httpx2 en TestClient; no afecta el resultado actual.

### Pendientes registrados al inicio

Validación visual/interactiva en navegador; persistencia y migraciones; autenticación y permisos; integración con proveedores; pruebas de carga con objetivos acordados; precisión, calibración y sesgos del modelo con datos autorizados; recuperación de respaldos; aceptación por usuarios.

No hay resultados de precisión predictiva: el prototipo ejecuta reglas demo y no un modelo entrenado. Compilar y pasar lint no equivale a validar el sistema completo.


### Verificación histórica tras reorganizar carpetas

- Backend separado en backend/app con rutas, esquemas y servicio: 4 pruebas aprobadas.
- React separado en componentes, servicios y estilos: compilación y lint aprobados.
- Archivo .env trasladado a backend/.env conservando su contenido; no se carga automáticamente.
- Recursos originales sin uso conservados en docs/archivo.
