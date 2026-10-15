# Entrega de demostración — NexoCredit

## Corte vigente de preparación — 14/10/2026

Entrega **local** del entorno existente; no se publica la aplicación, instala para terceros, convoca reuniones o contacta al asesor. Este documento es una guía de revisión, no un acta de aceptación ni una capacitación realizada. Se conservan las evidencias anteriores con sus fechas.

Verificación local final del **14/10/2026**: **197 pruebas backend/PostgreSQL y 129 frontend aprobadas**, sin omisiones, lint/build, auditoría npm con **cero vulnerabilidades reportadas** y cinco archivos PowerShell. La corrida inicial de hoy fue 190 backend/129 frontend; la final incorpora las regresiones de la corrección Ollama. Las **14 pruebas del empaquetador**, sin omisiones y sin DB/red, están incluidas en 197; no se suman otra vez. Comprueban selección pública, redacción sólo en copia, rutas/enlaces, exclusión de privados y manifiesto. Estas pruebas no equivalen a una nueva CI remota o un ZIP real ya generado; la nueva comprobación real de texto Ollama se registra por separado abajo. [Evidencia de preparación y verificación del 14/10/2026](../evidencias/2026-10-14/entrega-demo.md).

Se conserva el corte **histórico del 13/10/2026**, con 175 backend/PostgreSQL y 129 frontend aprobadas, lint/build y cinco archivos PowerShell: [reglas v2 e importes](../evidencias/2026-10-13/reglas-v2-y-importes.md). Su limitación de auditoría TLS y sus cifras no se reescriben como resultados de hoy. Cero vulnerabilidades reportadas en la auditoría del 14/10 no garantiza ausencia permanente de fallos o seguridad crediticia productiva.

El usuario informó que recargó/entró y abrió, actualizó y guardó Power BI. La comprobación posterior encontró todavía el diálogo **«Abrir»** y un modelo de **5 evaluaciones frente a 10 en PostgreSQL** en ese momento: **29 diferencias en 96 comparaciones SQL–DAX**. Tras las dos altas ficticias hay **12 evaluaciones**, pero la segunda conciliación todavía devolvió cinco en Desktop. **Actualización/conciliación Power BI pendiente**. Por solicitud del usuario no se controla más la interfaz; [pasos manuales](../evidencias/2026-10-14/entrega-demo.md#power-bi). No se presume aceptación, capacitación o actualización cloud.

La primera alta UI ficticia fue score 200, margen $20,000 → **Alto, reglas-demo-v2**. Recuperó la guía v2 por búsqueda local y completó inferencia real scikit-learn, clase `False` (no incumplimiento académico), independiente del formulario MXN. En ese corte de 11 registros, el filtro Alto mostró 2/$12,500 y al limpiarlo 11/$18,636. Ollama respondió entonces con una comparación errónea; el hallazgo histórico se conserva, no se transforma retrospectivamente en éxito.

Después del despliegue corregido se agregó una **segunda alta ficticia** y se comprobó la respuesta real: score 200 pertenece a banda 0–499 → Alto; margen $20,000 aporta mínimo Bajo; final Alto. Los hechos/razón están etiquetados **NO IA**, con comentario académico IA separado y fuente versión **2.0**. Reintentar el botón recuperó el mismo ID/fecha sin duplicar el escenario. Comprobación real aprobada para este caso, no una garantía semántica general. Captura local privada `output/revisiones_visuales/2026-10-14/explicacion-v2-corregida.jpg`, en la raíz exterior; no se sube ni se incluye en el ZIP. [Contrato y límites](../manuales/ACCESO_LOCAL_Y_PROVEEDORES.md#contrato-ollama-corregido--14102026).

Corte PostgreSQL posterior a ambas altas: **12 evaluaciones**, margen promedio **$18,750**, ingresos promedio **$30,000**, deuda promedio exacta **$10,020.05 sobre 10 capturas**, cobertura **83.333 %**; riesgo Bajo 7, Medio 2, Alto 3; revisión Pendiente 10 y Aprobada 2. Son datos ficticios del corte de QA, no contadores permanentes o aprobación de crédito. Los resúmenes monetarios redondean pesos y el detalle conserva centavos.

### Qué contiene el corte vigente

- Nuevas evaluaciones con `reglas-demo-v2`: score 0–499 → Alto, 500–679 → Medio y 680–1000 → Bajo. El margen impone al menos Alto con ≤$7,000 y Medio con >$7,000 y ≤$15,000. Se toma el peor riesgo de score y margen; los registros v1 no se recalculan. [Manual de reglas](../manuales/REGLAS_RIESGO_DEMO.md).
- Resúmenes monetarios redondeados a pesos completos, sin quitar centavos de captura, cálculos, PostgreSQL o detalles de evaluación/pagos. Dashboard y Power BI agregan resultados originales, aunque haya más de una versión; su información requiere un corte equivalente para compararla.
- Usuario local y Microsoft Entra, persistencia, historial, revisión humana, caché/cuotas de explicaciones y seguimiento ficticio de créditos, cuotas, abonos, alertas y eventos. No autoriza créditos reales ni valida depósitos.
- Explicación con Ollama y documentos locales por selección explícita. El catálogo local contiene **3 guías / 15 secciones**, manteniendo guía v1 y añadiendo v2. La plantilla de reglas sigue identificada como no generada por IA. La generación automática puede guardar una explicación y consumir recursos del proveedor seleccionado.
- Laboratorio IA local **scikit-learn**, modelo `nexocredit-uci-logistica-v1`, con 19 variables académicas UCI/NTD. Su clase binaria y métricas no reemplazan las reglas Bajo/Medio/Alto del formulario MXN. No utiliza Ollama para predecir ni guarda consultas UCI como evaluaciones. [Manual y límites](../manuales/LABORATORIO_IA_LOCAL.md).
- Azure OpenAI, Azure Machine Learning, Azure AI Search y Entra permanecen implementados, con adaptadores, keys privadas y [evidencia histórica del 04/10/2026](../manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md). No se garantiza vigencia de la suscripción o conectividad actual. Azure Search conserva el catálogo cloud histórico de **2 guías / 14 secciones**: **la guía v2 está pendiente de carga y comprobación cloud**. Si falta, no se explica v2 con la guía v1.

Las cifras de filas, métricas de modelo, conteos de suites y tiempos del apartado de línea base son muestras **históricas**, no un inventario actual. Para revisar el estado vigente sin exponer secretos, empezar por [el informe técnico](INFORME_TECNICO_ACTUAL.md), [la guía local de práctica](CAPACITACION_DEMO.md) y [los requisitos tecnológicos](../../REQUISITOS_TECNOLOGICOS.md).

### Preparar el ZIP local — generación y verificación

Se generó/revisó un candidato real de 339 archivos: CRC, SHA-256 del ZIP y cada miembro, exclusiones, redacción y huella del modelo correctos. [CI del commit de implementación](../evidencias/2026-10-14/github-actions.md) aprobó 197/129 en ambos trabajos. También aprobó la restauración aislada del respaldo de doce tablas, sin modificar la base original. El ZIP final se entrega con manifiesto propio; sus cantidades y huellas pueden cambiar al incorporar esta documentación. No confundir el hash del candidato con el final.

Desde la carpeta interior `empresa - copia/`, con Python disponible:

```powershell
python .\scripts\preparar_entrega.py --nombre NexoCredit_Entrega_2026-10-14
```

El generador usa sólo la biblioteca estándar. Si `python` no corresponde al entorno previsto, usa el ejecutable Python propio configurado para el proyecto. El nombre no admite rutas y las salidas se crean sin sobrescribir en `output/entregas/` de la **raíz exterior**: ZIP y manifiesto JSON con rutas, tamaños, SHA-256 de cada archivo y del ZIP y Git SHA de referencia. Se conserva el wrapper `NexoCredit/empresa - copia/`, `.github` y el workspace para no romper las rutas de CI. Un Git SHA de referencia no acredita un árbol limpio o una CI nueva.

La copia excluye credenciales, `.env` privados, base/dumps, dependencias instaladas, imágenes Docker, modelos Ollama, CSV UCI, PBIX/ABF y capturas privadas. Incluye el modelo numérico local scikit-learn y sus metadatos; redacta la identificación del plan sólo en la copia y sustituye la ficha privada del alumno por un marcador. No modifica la fuente ni exporta datos de trabajo. La revisión humana sigue siendo necesaria si alguien hubiese pegado un secreto en un archivo público.

No es una entrega autocontenida/offline: en un equipo sin instalación previa necesita **primer build Docker con descargas/configuración nuevas y una cuenta propia**, sin reutilizar llaves, contraseñas o volumen del equipo original. Una carpeta distinta por sí sola no crea otro proyecto/volumen Compose: si NexoCredit ya está instalado, conservar su entorno y consultar operación antes de iniciar otra copia. Después del primer build se activa modo local y se crea la cuenta. Ollama requiere servicio/modelo instalados; sin él, `EXPLICACIONES_PROVEEDOR=local` selecciona una plantilla **NO IA generativa**. `LEEME_PRIMERO.md` dentro del ZIP explica la secuencia; su manifiesto permite comprobar integridad, no certifica aptitud crediticia.

## Línea base documental histórica — 04/10/2026

Corte documental: 04/10/2026. Preparado a partir del código local y de comprobaciones registradas; no es un acta firmada ni aprobación del asesor. No acredita las 500 horas propuestas, ejecución de sprints ni disponibilidad permanente de Azure. La preparación inicial no publicó código ni creó recursos cloud. Seguimiento posterior: [cierre técnico NexoCredit](../evidencias/2026-10-04/cierre-tecnico.md), suites 69 backend/48 frontend, respaldo/restauración aislada y metadatos ML; [CI remota aprobada](../evidencias/2026-10-04/github-actions.md) para commit de código 19223ae, publicado en rama de revisión sin cambiar main.

## Alcance histórico registrado — 04/10/2026 y 11/10/2026

Incremento histórico del 11/10/2026: acceso local y Ollama/documentos locales adicionales, RFC/CURP básico con SAT manual, caché/cuotas y **seguimiento ficticio de créditos/pagos/alertas**. Se conservaron integraciones Azure, scoring y datos históricos. [Informe técnico](INFORME_TECNICO_ACTUAL.md), [guía de práctica preparada](CAPACITACION_DEMO.md) y [evidencia](../evidencias/2026-10-11/seguimiento-crediticio.md). Las capacidades y cifras siguientes describen la comprobación histórica de octubre 4; el guion local vigente se distingue en su apartado propio. No se realizó reunión ni capacitación por aquel incremento.

- Acceso Microsoft Entra ID y rechazo de rutas de negocio sin token.
- Captura ficticia, reglas demo, guardado PostgreSQL, historial y revisión manual con identidad verificada, motivo y versiones. Reintentos sin duplicación y recuperación tras recargar.
- Explicación automática Azure OpenAI con guía DEM-02 de Azure AI Search, sin enviar RFC ni modificar el riesgo. Catálogo de 2 guías / 14 secciones y búsqueda textual.
- Laboratorio Azure ML separado: 19 entradas UCI en NTD, respuesta booleana y aviso correcto de la consulta de esa sesión. No persiste escenarios ni sustituye reglas demo.
- Dashboard React con filtros, totales, promedios que distinguen ausencia de cero y distribución de riesgos. Indicadores públicos de Banxico y Banco Mundial con periodo, unidad, fuente y caché.
- Power BI Desktop conectado a una vista de lectura limitada; 11 visuales y 96 comparaciones SQL–DAX comprobados el 30/09/2026. No publicado en cloud.
- Docker local y GitHub Actions: nueva ejecución 37247212787 aprobada para el commit de código 19223ae; 69 backend y 48 frontend sin omisiones, migraciones, lanzadores, audit, lint y build aprobados. La ejecución histórica del 23/09/2026 se conserva por separado.

Las 13 tecnologías obligatorias y su estado individual se consultan en [REQUISITOS_TECNOLOGICOS.md](../../REQUISITOS_TECNOLOGICOS.md). Scrum sigue sin ejecución acreditada: el backlog organizado no sustituye reuniones, revisión ni retrospectiva.

## Carpeta de revisión

1. [README principal](../../README.md): arranque y límites.
2. [Manual de operación](../manuales/OPERACION.md): acceso, captura, consulta, errores y Power BI.
3. [Plan y requisitos funcionales](../planificacion/PLAN_PROYECTO.md): alcance objetivo frente a implementación parcial/demo.
4. [Índice de evidencias](../evidencias/README.md): enlaces a pruebas, capturas y métricas.
5. [QA](../calidad/QA.md): resultados actuales y comprobaciones históricas con sus fechas.
6. [Backlog de cierre](../../gestion_proyecto/scrum/BACKLOG_CIERRE.md): acciones pendientes y condiciones de cierre, sin horas ni responsables inventados.

## Resultados registrados, no una nueva ejecución

El 04/10/2026 se aprobaron 57 pruebas backend, incluyendo 5 con PostgreSQL real y esquemas aislados. Las respuestas de proveedores en los tests son simuladas. Tras corregir el aviso ML se aprobaron 42 pruebas frontend, ESLint y Vite en una construcción Docker. Son suites separadas, no una sola ejecución combinada ni una nueva validación GitHub Actions.

Las consultas reales autenticadas se documentan por separado en [prueba-e2e.md](../evidencias/2026-10-04/prueba-e2e.md). La muestra web terminó con 7 evaluaciones: Bajo 5, Medio 1, Alto 1; margen promedio 17,857.14 MXN; deuda promedio informada 10,000.10 MXN sobre 5 capturas. Son resultados históricos de una muestra ficticia, no cifras permanentes. La muestra Power BI comprobada el 30/09/2026 tenía 5 evaluaciones y necesita actualizarse para reflejar nuevas filas.

## Guion de demostración local — corte 14/10/2026

Recorrido preparado para el operador en el equipo actual. No convoca a terceros ni acredita capacitación, aceptación o ejecución de los pasos. Los ejemplos son ficticios. Las escrituras o generaciones se realizan sólo si el operador decide demostrar esas acciones, no por leer el guion.

1. Identificar versión del código, corte documental, modo de proveedores y respaldo disponible, sin mostrar `.env`, contraseñas, llaves o dumps.
2. Abrir la aplicación existente en `http://localhost:8080/` con Docker Desktop disponible e iniciar sesión con la cuenta propia local o Microsoft autorizada. No desactivar autenticación ni crear una cuenta por defecto.
3. Consultar historial/dashboard y explicar que un registro v1 conserva su riesgo original. Leer detalle para distinguir importe exacto de resumen en pesos; no recalcular ni agregar registros innecesarios.
4. Explicar la matriz v2 sin guardar: margen $20,000 con score 200 → Alto, 500 → Medio, 700 → Bajo; score 900 con margen $7,000 → Alto. Si se decide crear un escenario nuevo, usar identificador ficticio, ingresos 30,000, gastos 10,000, deuda/pagos/atraso 0 y score 700; esperar `reglas-demo-v2`, margen 20,000 y Bajo. Advertir persistencia y generación automática antes de enviar; Azure puede generar consumo, y Ollama requiere servicio/modelo disponibles.
5. Consultar guía DEM-02 v2 y su fuente/versionado en documentos locales (3 guías / 15 secciones). Si se usa Azure Search, señalar que la carga v2 está pendiente; no presentarla como consulta cloud exitosa ni reutilizar la guía v1 para el resultado nuevo.
6. Abrir una evaluación ficticia para mostrar revisión y, si existe, seguimiento de cuotas/pagos. Diferenciar riesgo, estado de revisión y estado de pago; no guardar revisiones, planes o abonos salvo decisión explícita del operador.
7. Mostrar **Laboratorio IA local**, sus 19 entradas UCI/NTD y métricas. Cargar el ejemplo sólo llena campos; una inferencia local opcional no llama a Azure ni modifica el scoring MXN. No usar datos del solicitante ni presentar la salida como probabilidad calibrada.
8. Mostrar fuentes económicas y evidencia Power BI con sus fechas; una consulta de indicador o actualización Desktop es una operación adicional, no implícita en esta preparación. Comparar sólo cortes equivalentes, sin publicar o compartir credenciales.
9. Registrar únicamente lo realizado, su fecha, resultados y límites en la evidencia correspondiente. No completar asistentes, capacitación, ceremonias, horas, firmas o aceptación si no ocurrieron.

## Pendientes y límites

- Comparación binaria del modelo remoto con el artefacto académico; identidad registrada y versión verificadas mediante metadatos independientes el 04/10/2026, no por la etiqueta local.
- Recuperación productiva completa; el ensayo histórico del 04/10/2026 concilió tres tablas y el seguimiento del 11/10/2026 amplió el esquema a doce. Son ensayos fechados aislados, no una nueva restauración de trabajo ni una garantía empresarial.
- Evidencias reales de Scrum, capacitación y aceptación del alcance demo por el asesor.
- Carga y comprobación de la guía v2 en Azure Search antes de seleccionar documentos Azure para nuevas explicaciones.
- Sistema crediticio final: datos representativos autorizados, políticas oficiales, historial crediticio privado, validación del modelo y seguridad/operación de producción. El seguimiento descriptivo y las alertas internas ficticias sí están implementados; no verifican pagos bancarios ni equivalen a notificaciones externas o evaluación crediticia real.

Una demo funcional no cierra estos requisitos del sistema final. El candidato UCI detectó 32,01 % de los incumplimientos en su conjunto de prueba; no es un modelo validado para clientes de PluriOne. No hay probabilidad calibrada ni autorización automática de crédito.

La CI del commit histórico y los ensayos de respaldo/restauración registrados tienen sus resultados fechados; no se presentan como una CI o restauración nueva del 14/10/2026. No equivalen a aceptación académica o empresarial.

## Manejo seguro de la entrega

Entregar documentación y evidencias revisadas, no copiar indiscriminadamente toda la carpeta. Excluir archivos .env, claves, tokens, sessionStorage, dumps de base, cachés con información privada y credenciales de Power BI. Los ejemplos deben seguir siendo ficticios. No trasladar secretos al repositorio ni a capturas. Conservar las evidencias históricas y añadir seguimientos; no reemplazar un fallo previo por un éxito sin fecha y explicación.
