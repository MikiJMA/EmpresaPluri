# Reportes y dashboard — Power BI

Función: visualizar evaluaciones, distribución de riesgo demo y seguimiento de revisión manual.
Estado: demostración local terminada y guardada en Power BI Desktop el 30/09/2026. Conexión PostgreSQL, actualización de datos, indicadores y filtros comprobados. Sin publicación cloud ni gateway.

## Abrir el dashboard

Abrir `PluriOne_Riesgo_Crediticio.pbix.pbip` (la doble extensión proviene del nombre elegido al guardar; el archivo final es PBIP). No abrir el antiguo `.pbix` para revisar estos cambios. Mantener junto al proyecto las carpetas `.Report` y `.SemanticModel`.

La publicación de código conserva las definiciones PBIP/PBIR/TMDL, no el antiguo PBIX, `.pbi/cache.abf` ni `.pbi/localSettings.json`. Estos archivos locales se mantienen en el equipo y se excluyen del nuevo árbol Git; retirar su seguimiento no elimina copias en commits anteriores. Al clonar, abrir el PBIP y configurar la conexión privada para actualizar los datos en Desktop. No publicar dumps, contraseñas ni cachés del modelo.

La página inicial `Resumen de riesgo • DEMO` contiene total de evaluaciones, margen e ingresos promedio en MXN, deuda promedio informada, cantidad y cobertura de datos de deuda, distribución por riesgo demo, seguimiento de revisión manual, filtros por riesgo/estado y tabla de detalle con fechas UTC. La página original se conserva. AVERAGE excluye datos ausentes y conserva ceros. Los conteos usan COALESCE para mostrar cero cuando no hay registros o datos de deuda. La cobertura usa DIVIDE: muestra 0 % si existen evaluaciones pero ninguna tiene deuda informada; queda en blanco si no hay evaluaciones. No se reemplazan deudas ausentes por cero. Los filtros afectan los indicadores de la página. No hay predicción calibrada ni autorización real de créditos.

Comprobación del 30/09/2026: 19 JSON de definición validados contra los esquemas oficiales de Microsoft; 11 visuales del dashboard y sus referencias y límites de página comprobados. TMDL deserializado con la biblioteca instalada de Power BI: 3 tablas, 12 columnas de datos en Consulta1 y 6 medidas. Las seis medidas ejecutadas en el modelo abierto coinciden con PostgreSQL en 16 contextos de filtro (96 comparaciones), incluyendo resultados vacíos. También se probaron los controles directamente en Desktop: Medio, Alto, Aprobada, Pendiente, Bajo + Pendiente y limpieza de filtros. Proyecto y caché actualizada guardados. En Importar, los datos no cambian hasta actualizar. No se publicó el reporte ni se modificaron registros PostgreSQL.

La muestra comprobada contiene 5 evaluaciones: margen promedio de 17,000.00 MXN, ingresos promedio de 30,000.00 MXN, deuda promedio informada de 16,666.83 MXN, 3 evaluaciones con dato de deuda y cobertura del 60 %. Distribución: Bajo 3, Medio 1, Alto 1; revisión: Pendiente 4, Aprobada 1. Son cifras de la muestra local, no resultados permanentes ni decisiones de crédito. Las tarjetas abrevian importes en miles; las medidas mantienen el valor sin esa abreviación.

## Verificación repetible

Desde la carpeta interior, con las dependencias frontend/backend instaladas:

```powershell
node ./analitica/reportes_power_bi/verificar_reporte.mjs
pwsh -File ./analitica/reportes_power_bi/verificar_modelo.ps1
./.venv/Scripts/python.exe ./scripts/verificar_powerbi.py
pwsh -File ./analitica/reportes_power_bi/verificar_dax.ps1 -Puerto <puerto_del_modelo_abierto>
```

Usar PowerShell 7 para las bibliotecas .NET de Desktop. La primera herramienta necesita red para descargar únicamente esquemas públicos de Microsoft; no transmite el contenido del reporte. La segunda valida TMDL, pero no ejecuta DAX. La tercera consulta agregados SQL con el lector local y comprueba que no pueda consultar las tablas originales. La cuarta compara SQL con DAX real y falla ante diferencias; no refresca, guarda ni publica. El puerto local de Analysis Services cambia al reabrir Desktop: no confundirlo con el puerto PostgreSQL 55433. Las pruebas de DAX no sustituyen las pruebas de controles y renderizado.

La edición externa usa el formato PBIR documentado por Microsoft: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report

Servidor: 127.0.0.1:55433. Base: pluri_credito. Usuario lector: pluri_powerbi. Contraseña privada en .local/powerbi/.env (ignorada por Git). Usar Importar y la vista reportes.evaluaciones_powerbi; excluye RFC, responsable y observaciones. Los valores ausentes permanecen nulos; fechas en UTC. Refrescar desde Power BI para obtener nuevas evaluaciones. No hay publicación cloud ni gateway configurado.

Preparación repetible desde la raíz interior: .venv/Scripts/python.exe scripts/preparar_powerbi.py, después de iniciar Docker y aplicar migraciones. El script crea un lector sin acceso a tablas originales, conserva su contraseña y valida consulta de la vista. PostgreSQL se publica solo en loopback 55433, no en la red. No usa TLS: solo para esta demostración local; conexiones remotas requieren configuración segura distinta. No compartir credenciales ni archivos de reportes con datos sensibles.

Comprobación 23/09/2026: vista con 3 evaluaciones y acceso TCP exitoso, lecturas de tablas originales y planes de escritura rechazados. Durante el diagnóstico, has_table_privilege con parámetros provocó un fallo del proceso PostgreSQL (signal 11); PostgreSQL se recuperó automáticamente. La comprobación utiliza ahora SELECT limitado y EXPLAIN sin ejecución de escritura. La API volvió a responder HTTP 200; investigar versión/imagen antes de producción.

Alcance cerrado: demostración local en Desktop. Para cualquier publicación futura faltan autorización del usuario, destino, permisos, configuración segura y estrategia de actualización/gateway. Tampoco se acredita con estas pruebas la aptitud de un modelo predictivo para créditos reales.
