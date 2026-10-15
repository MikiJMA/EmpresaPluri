# Preparación de entrega local — 14/10/2026

## Alcance y separación de pruebas

NexoCredit se entrega como **prototipo académico local**, no como sistema aprobado para decidir créditos. No se publica la aplicación ni se contacta al asesor. Las evidencias históricas Azure del 04/10 se conservan; no se afirma conectividad cloud, suscripción vigente, aceptación, capacitación o ceremonias Scrum actuales.

La autorización de publicación se limita al código/documentación depurados de `MikiJMA/EmpresaPluri`, rama `codex/cierre-nexocredit-demo`, para comprobar GitHub Actions. No autoriza cambiar `main`, subir configuración privada, base de datos, cuentas o capturas.

## Suites locales

Ejecución inicial completa mediante `scripts/probar-programacion.ps1`: **190 pruebas backend/PostgreSQL y 129 frontend aprobadas**, sin omisiones; cinco archivos de pruebas PowerShell, ESLint, Vite y auditoría npm con cero vulnerabilidades reportadas. Las 190 incluyen 14 pruebas del empaquetador y una prueba integral nueva con PostgreSQL real aislado. No se suman por segunda vez.

Se construyeron las imágenes con los Dockerfiles normales y descarga TLS verificada, sin el Dockerfile de contingencia de la revisión del 13/10. La auditoría que entonces no pudo completarse sí terminó hoy. Un resultado de auditoría sin vulnerabilidades conocidas no certifica seguridad permanente.

Tras corregir el hallazgo Ollama, la ejecución final completa aprobó **197 backend/PostgreSQL y 129 frontend**, sin omisiones, auditoría npm cero vulnerabilidades conocidas, cinco archivos PowerShell, lint y build. Siete regresiones nuevas cubren hechos/categorías calculados por código, conservación v1, margen coherente, salida limitada, contradicciones rechazadas y cambio de clave Ollama. Los ejemplos de proveedores de esas suites son simulados; la inferencia local numérica sí ejecuta el artefacto real.

La prueba `backend/tests/test_entrega_demo.py` usa únicamente PostgreSQL de prueba en loopback y esquemas aleatorios propios. Comprueba cuenta local, JWT, dos evaluaciones v2, idempotencia, dashboard, historial/revisión, documentos, plantilla explícita NO IA, caché/cuotas, inferencia numérica real y seguimiento ficticio: cuotas, pagos parciales exactos, saldos, alertas, eventos, auditoría por rol y revocación de sesión. Las respuestas financieras son simuladas, no consultas Banxico reales. No inserta esos datos en la base de trabajo.

## Aplicación real en el navegador

El usuario recargó y volvió a iniciar sesión local. Se comprobó el asset nuevo `/assets/index-DTtQkTef.js`, las tarjetas de score/margen v2 y los importes resumen sin decimales. Antes de la prueba había diez evaluaciones; el corte histórico del 13/10 tenía nueve y no se presenta como un conteo actual.

Se agregó **un escenario ficticio de QA**, RFC demostrativo `AAAA010101AA1`, ingresos 30,000, gastos 10,000, deuda 100, pagos mensuales 50, atraso 0 y score 200. El resultado guardado fue **Alto**, margen 20,000 y `reglas-demo-v2`: el margen bueno no reduce el riesgo Alto del score. Se conserva el escenario para demostrar la regresión; no se modifica una evaluación anterior ni se convierte en crédito.

La búsqueda textual `reglas-demo-v2` recuperó DEM-02 de `guia-demostracion-v2`, versión 2.0, con los ejemplos y límites correctos. Catálogo local: tres guías / quince secciones. No es una nueva carga Azure Search.

La consulta del ejemplo ficticio del laboratorio completó una **inferencia real local**, modelo `nexocredit-uci-logistica-v1`, clase no incumplimiento. Sus 19 variables UCI/NTD son independientes de las reglas MXN; no se guardó la consulta como evaluación ni se validó aptitud para México.

En el intento inicial Ollama sí respondió, pero se detectó una explicación incorrecta: comparó el score con el margen y describió 200 como mayor que 499. El resultado numérico persistido permaneció correcto. El intento inicial no se aprueba; su corrección y comprobación posterior se detallan a continuación. No se oculta con una plantilla presentada como IA.

Corrección aplicada: hechos, bandas y razón se calculan y etiquetan como **no generados por IA**. Ollama añade sólo un comentario académico sin cifras, categorías o comparaciones, con control de formato/vocabulario; una infracción falla 502 sin mostrar ese texto ni cambiar de proveedor. Este control no es validación semántica universal. Se versionó exclusivamente la clave de caché Ollama; no se borró la respuesta errónea histórica ni se reutiliza bajo el contrato nuevo. Azure conserva su adaptador y no fue consultado. Una llamada local directa ficticia posterior aprobó el contrato. Se reconstruyó/aplicó sólo el backend con el Dockerfile normal y quedó saludable, sin recrear PostgreSQL.

Se agregó un segundo escenario de QA con los mismos valores para probar la corrección automática en la interfaz. La generación real posterior completó correctamente: mostró score 200 en banda 0–499, riesgo por score Alto, margen 20,000 en banda >15,000, mínimo Bajo y resultado final Alto; hechos/razón del servidor y comentario académico IA separados, con fuente DEM-02 v2/2.0. Un reintento mantuvo la misma fecha/registro, sin duplicar. La pantalla fue capturada en `output/revisiones_visuales/2026-10-14/explicacion-v2-corregida.jpg`, relativa a la raíz exterior: archivo local no publicado ni incluido en el paquete. El comentario conserva advertencia de revisión humana; la comprobación no certifica toda salida futura del modelo.

Lectura SQL limitada posterior: **doce evaluaciones**, margen promedio 18,750 MXN, ingresos promedio 30,000; deuda promedio exacta 10,020.05 sobre diez capturas y cobertura 83.333… %. Riesgos: Bajo 7, Medio 2, Alto 3; revisiones: Pendiente 10, Aprobada 2, Rechazada 0. Son diez registros previos más las dos altas ficticias indicadas, no doce clientes. Las revisiones originales no cambiaron. El filtro Alto probado antes de la segunda alta dio dos registros; no se confunde aquel corte con el final.

Indicadores observados en la caché del navegador: Banxico conservó FIX y marcó la tasa de fecha futura como datos parciales/no vigente; Banco Mundial mostró los últimos periodos publicados. Esta observación no equivale a una nueva petición externa ejecutada por las suites, ni utiliza indicadores para cambiar el riesgo.

## Power BI

Validación de fuente: 19 definiciones JSON, 11 visuales, seis medidas y nueve esquemas oficiales; deserialización TMDL de tres tablas, doce columnas y seis medidas. Estas validaciones no acreditan refresco, render o valores actuales de Desktop.

El usuario informó apertura, actualización y guardado manuales. La comprobación posterior encontró todavía el cuadro «Abrir» y un modelo de **cinco evaluaciones**. Se ejecutaron 96 comparaciones SQL–DAX (seis medidas por dieciséis contextos): **29 diferencias** respecto de las diez evaluaciones que entonces tenía PostgreSQL. No se atribuye el refresco como completado. Tras el escenario de QA hay once evaluaciones esperadas; el reporte debe actualizarse y conciliarse contra ese nuevo corte.

La repetición posterior del escenario para comprobar Ollama elevó el corte esperado a doce. Tras una segunda confirmación del usuario, el modelo abierto volvió a devolver cinco frente a doce en SQL: la conciliación sigue fallando. No se exige que un refresco anterior contenga una fila creada después; la conciliación final requiere un mismo corte temporal. El usuario solicitó no controlar más ventanas/navegador: se detuvo la automatización UI y el refresco restante se deja manual.

Pasos manuales: cerrar el cuadro «Abrir» seleccionando el proyecto correcto, abrir `analitica/reportes_power_bi/PluriOne_Riesgo_Crediticio.pbix.pbip`, pulsar **Inicio → Actualizar**, esperar sin errores y **Guardar**. Sin filtros debe mostrar 12 evaluaciones, margen promedio 18.75 mil e ingresos 30.00 mil; deuda informada aproximadamente 10.02 mil y cobertura 83.3 %. Si solicita credenciales, usar el lector limitado configurado en ese equipo, nunca pegarlas en documentos/chat. No publicar el reporte ni cambiar la base por una diferencia de caché.

## Conservación de datos y empaquetado

Se creó antes de la prueba visual un respaldo privado mediante el lanzador PostgreSQL; no se comparte dump, roles, contraseñas o cuentas. Las suites trabajan en una base temporal distinta y la prueba UI agrega exclusivamente el escenario ficticio indicado.

El manifiesto del respaldo previo contiene doce tablas, diez evaluaciones, dos revisiones, una cuenta y cinco migraciones. El ensayo fue inicialmente bloqueado; tras autorización humana explícita se ejecutó y **aprobó una restauración aislada de las doce tablas**: filas/datos, columnas, restricciones y vistas conciliadas. El contenedor temporal, sin puertos y aislado, fue verificado/retirado; la base original no se modificó. Se guardó sólo un informe privado local. El corte restaurado contiene diez evaluaciones, anteriores a las dos altas de QA; no se atribuyen doce filas a ese respaldo.

`scripts/preparar_entrega.py` prepara una copia con wrapper `NexoCredit/empresa - copia/`, workflow exterior y workspace. Excluye antes de abrir: configuración privada, bases/dumps, dependencias, imágenes Docker, modelos Ollama, CSV UCI, PBIX/ABF y capturas. Mantiene plantillas `.env.example` y el modelo numérico scikit-learn. Redacta únicamente la copia del bloque de identificación del plan y genera un marcador para la ficha del alumno; los originales no se modifican.

Se creó/revisó un ZIP candidato real de **339 archivos / 2,108,110 bytes**, con referencia Git `e9e3c0cd4b3154e2b0d5b282c2793126225f1623`. CRC, SHA-256 del archivo y cada miembro, rutas únicas, tamaños, exclusiones privadas, redacción y huella del modelo aprobados. SHA-256 del candidato: `35d5f2d08032a7253357d43606d541971f75914adcd50d875110565f93e3216a`. No es la huella del archivo final tras actualizar esta evidencia. La entrega final se acompaña de su manifiesto propio: consultar allí el número de archivos, SHA del ZIP y referencia Git exactos. Las tres plantillas públicas y definiciones Power BI están incluidas; no las cachés ni datos.

Se añadió `.gitattributes` para conservar LF en los JSON del modelo, cuya huella se verifica por bytes: una conversión automática CRLF en Windows no debe invalidarlo. El generador incluye ese archivo y sus catorce pruebas se repitieron correctamente tras esta mejora. La selección pública se revisó sin encontrar secretos nuevos; cinco rutas de perfil personal de capturas se convirtieron a referencias relativas, sin publicar imágenes privadas.

El paquete no es un instalador offline: necesita Docker Desktop, un primer build con Internet, configuración y cuenta nuevas. Ollama necesita servicio y modelo instalados; la alternativa de plantilla se etiqueta explícitamente NO IA. Power BI requiere Desktop y conexión de lectura propia. Azure y Banxico requieren recursos/configuración y credenciales propias.

## Publicación de código y CI

Commit de implementación `e9e3c0cd4b3154e2b0d5b282c2793126225f1623` guardado y subido sólo a la rama autorizada. [GitHub Actions 38649003430](github-actions.md) terminó con ambos trabajos aprobados y conteos 197/129 comprobados en logs, migraciones, cinco pruebas PowerShell, audit, lint y build. `main` permaneció en su SHA anterior. No se publica el servicio ni se crea PR.

## Pendientes fuera de la entrega de código

- Actualizar/conciliar Power BI con las doce evaluaciones actuales, sin publicar.

La guía v2 de Azure Search, la comparación binaria del modelo Azure, validación crediticia real, carga/producción y aceptación/capacitación/Scrum formales permanecen fuera del cierre académico comprobable aquí.
