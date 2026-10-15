# Prueba integral local — 4 de octubre de 2026

Alcance: demostración React/Nginx → FastAPI → PostgreSQL, con Microsoft Entra ID e integraciones Azure y financieras existentes. La sesión fue iniciada por el usuario en el navegador de Codex. No se crearon servicios cloud, se cambiaron permisos ni se usaron solicitudes crediticias reales.

## Evidencia de la pantalla autenticada

- Identificador exclusivamente ficticio: `PRUEBA-E2E-20261004-1791140528117`.
- Captura: ingresos 30,000 MXN, gastos 10,000 MXN, deuda 0, pagos 0, atraso 0 y score 700. Un ingreso negativo fue rechazado por la validación HTML antes de guardar; el total permaneció en 6.
- Evaluación válida: margen 20,000 MXN y riesgo demo Bajo, versión `reglas-demo-v1`. El historial pasó de 6 a 7 registros y mostró la nueva evaluación.
- Azure OpenAI generó la explicación automáticamente, sin pulsar otro botón. La pantalla identifica `gpt-5-mini-1` y cita DEM-02, versión 1.0, de la guía recuperada de Azure AI Search. La explicación coincide con las reglas observadas; esta comprobación no certifica todas las respuestas futuras de IA.
- Revisión ficticia guardada como Aprobada, versión 1, con la identidad Entra de la sesión y una observación explícita de prueba. No autoriza ningún crédito real. Riesgo original Bajo conservado.
- Reenvío del mismo formulario: una sola fila para ese identificador, mismo momento de guardado y total 7. Las pruebas de interfaz comprueban por separado la reutilización de la explicación para el mismo UUID.
- Recarga de la aplicación: sesión conservada; registro, importes, revisión 1 y observación recuperados desde el detalle. No se afirma persistencia de la explicación de IA: el resultado del formulario se limpia al recargar.
- Filtro Alto: 1 evaluación, margen 5,000 MXN, deuda «Sin datos» y cobertura sobre 0 capturas. El historial no se filtra. Limpiar restaura 7 evaluaciones, Bajo 5 / Medio 1 / Alto 1, margen promedio 17,857.14 MXN y deuda promedio informada 10,000.10 MXN sobre 5 capturas.
- Rango inclusivo UTC 2099-01-01 → 2099-01-02, introducido mediante los controles de fecha: 0 evaluaciones, ambos promedios «Sin datos» y mensaje de ausencia de evaluaciones. Se limpiaron los filtros y se dejó abierto el resumen con total 7.
- Azure AI Search: catálogo real con 2 guías / 14 secciones. Buscar «margen» recuperó DEM-02 y conservó el catálogo.
- Azure ML: ejemplo ficticio de 19 enteros UCI, LIMIT_BAL 200,000 NTD. La consulta desde la interfaz autenticada devolvió «No incumplimiento». El total del dashboard permaneció en 7. No se convierte MXN a NTD ni se mezcla esta clasificación con las reglas demo.
- Banxico y Banco Mundial aparecen disponibles con sus cuatro observaciones, periodos, unidades y procedencia. El botón de actualización usa el servicio con caché; no se interpreta como datos en tiempo real ni historial crediticio privado.

## Pruebas automáticas y acceso HTTP

- Backend actual montado en solo lectura en un contenedor temporal: 57 pruebas aprobadas, incluidas las 5 pruebas PostgreSQL con esquemas aislados. Las respuestas externas en estas pruebas son simuladas; las consultas reales anteriores son evidencia separada. No se modificaron evaluaciones previas.
- Frontend actual construido en una imagen temporal de verificación: 34 pruebas aprobadas, ESLint y Vite aprobados. No se reiniciaron servicios para construir esta imagen.
- Por Nginx, sin token: `/` y `/api/v1/auth/config` responden 200; `/api/v1/auth/me`, historial, dashboard y estados/indicadores de las cuatro integraciones responden 401. No se leyeron ni extrajeron tokens del navegador.
- Consola del navegador de la aplicación: 0 errores al finalizar. Capturas de la predicción ML y del dashboard sin filtros guardadas junto a este reporte.
- Una comprobación real anterior del cliente Azure ML del servidor, el mismo día, obtuvo HTTP 200 en 0.594 segundos y clase booleana `false`, sin guardar escenarios.

## Límites y observaciones pendientes

- El mensaje inicial del laboratorio permanece «Configuración presente; conexión pendiente de una consulta correcta» después de mostrar una predicción válida. Es un detalle de estado visual, no un fallo de la consulta; no se corrigió código de la aplicación durante esta prueba.
- `modelo_configurado` es una etiqueta local. La versión efectiva servida por el despliegue Azure ML no fue verificada mediante metadatos del plano de administración.
- Esta ejecución es local, no una nueva ejecución de GitHub Actions ni publicación Power BI. No se realizaron pruebas de carga, restauración de respaldos, aceptación de negocio ni validación del modelo para crédito real.
- Se conserva un registro ficticio adicional y su revisión como evidencia. No se borraron datos existentes.

Capturas de verificación en esta carpeta: `azure-ml.jpg` y `dashboard.jpg`.

## Corrección posterior del aviso Azure ML

La observación visual anterior se corrigió después de la prueba integral, conservando el registro histórico de cómo se detectó.

- La interfaz mantiene el aviso de configuración inicial hasta efectuar una consulta. Durante el intento muestra «Consultando Azure ML»; una respuesta válida lo sustituye por «Conexión con Azure ML comprobada en esta sesión. Última consulta completada correctamente». Un fallo posterior anuncia que el último intento no se completó y borra la predicción anterior.
- La respuesta debe contener una clase booleana, procedencia Azure ML, modo académico, etiqueta de modelo y advertencia no vacías. Esta validación no verifica la identidad efectiva del modelo desplegado. No se agregaron reintentos automáticos ni persistencia.
- 42 pruebas frontend, ESLint y Vite aprobados durante la construcción de la imagen. Se recreó solo frontend; los identificadores de los contenedores backend y PostgreSQL permanecieron iguales.
- Tras recargar localhost con la sesión Entra existente, el aviso volvió al estado inicial. Se cargó el ejemplo ficticio UCI y se hizo una consulta real: espera visible, respuesta «No incumplimiento» y aviso de conexión correcta visibles juntos. Total del dashboard: 7. Consola: 0 errores. No se crearon evaluaciones en esta comprobación.
- Los estados fallidos y contratos inválidos se comprobaron mediante pruebas automáticas; no se interrumpió el backend ni se alteraron credenciales para provocar un fallo real.
- El aviso expresa el resultado del último intento de la sesión, no supervisión continua del servicio. Editar los valores limpia la predicción; recargar no conserva la comprobación de conexión.

Captura posterior local: `azure-ml-estado-corregido.jpg`, conservada en el equipo y excluida del repositorio público. Seguimiento posterior: [cierre técnico y nueva marca](cierre-tecnico.md).
