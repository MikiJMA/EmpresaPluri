# Reportes y dashboard — Power BI

Función: visualizar cartera, distribución de riesgo, tendencias y seguimiento.
Estado: conexión local e importación en Desktop comprobadas. Proyecto PBIP recibido; página de dashboard creada por edición PBIR, pendiente de abrir y verificar visualmente en Desktop.

## Abrir el dashboard

Abrir `PluriOne_Riesgo_Crediticio.pbix.pbip` (la doble extensión proviene del nombre elegido al guardar; el archivo final es PBIP). No abrir el antiguo `.pbix` para revisar estos cambios. Mantener junto al proyecto las carpetas `.Report` y `.SemanticModel`.

La página inicial `Resumen de riesgo • DEMO` contiene total de evaluaciones, margen e ingresos promedio en MXN, deuda promedio informada, cantidad y cobertura de datos de deuda, distribución por riesgo demo, seguimiento de revisión manual, filtros por riesgo/estado y tabla de detalle con fechas UTC. La página original se conserva sin cambios. Las medidas AVERAGE y COUNT excluyen datos ausentes y conservan ceros; la cobertura usa DIVIDE para no dividir por cero. Los filtros afectan los indicadores de la página. No hay predicción calibrada ni autorización real de créditos.

Comprobación de archivos: 17 JSON de páginas/visuales analizados correctamente; referencias de columnas y medidas verificadas contra Consulta1.tmdl. Esto no sustituye la validación de esquema completo ni el renderizado y ejecución DAX en Desktop. Validación visual pendiente: abrir PBIP, confirmar indicadores y gráficos sin errores, probar filtros y Actualizar con Docker activo. En Importar, los datos no cambian hasta actualizar. No se publicó el reporte ni se modificaron registros PostgreSQL.

La edición externa usa el formato PBIR documentado por Microsoft: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report

Servidor: 127.0.0.1:55433. Base: pluri_credito. Usuario lector: pluri_powerbi. Contraseña privada en .local/powerbi/.env (ignorada por Git). Usar Importar y la vista reportes.evaluaciones_powerbi; excluye RFC, responsable y observaciones. Los valores ausentes permanecen nulos; fechas en UTC. Refrescar desde Power BI para obtener nuevas evaluaciones. No hay publicación cloud ni gateway configurado.

Preparación repetible desde la raíz interior: .venv/Scripts/python.exe scripts/preparar_powerbi.py, después de iniciar Docker y aplicar migraciones. El script crea un lector sin acceso a tablas originales, conserva su contraseña y valida consulta de la vista. PostgreSQL se publica solo en loopback 55433, no en la red. No usa TLS: solo para esta demostración local; conexiones remotas requieren configuración segura distinta. No compartir credenciales ni archivos de reportes con datos sensibles.

Comprobación 23/09/2026: vista con 3 evaluaciones y acceso TCP exitoso, lecturas de tablas originales y planes de escritura rechazados. Durante el diagnóstico, has_table_privilege con parámetros provocó un fallo del proceso PostgreSQL (signal 11); PostgreSQL se recuperó automáticamente. La comprobación utiliza ahora SELECT limitado y EXPLAIN sin ejecución de escritura. La API volvió a responder HTTP 200; investigar versión/imagen antes de producción.

Para completar: verificar renderizado y medidas en Desktop, conciliar indicadores con PostgreSQL y acordar permisos y actualización para cualquier publicación futura.
