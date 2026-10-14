# MVP — NexoCredit

## Producto mínimo viable, matriz MoSCoW y plan de aceptación

| Dato de control | Valor |
|---|---|
| Versión | 1.4 |
| Fecha de edición | 13/10/2026 |
| Línea base técnica | 04/10/2026 |
| Incremento actual | 13/10/2026: reglas-demo-v2 y resúmenes sin decimales; Azure y campos de keys conservados |
| Estado | Propuesta de alcance y aceptación; núcleo técnico comprobado |
| Documento complementario | [PRD — NexoCredit](PRD_NEXOCREDIT.md) |
| Documento anterior | [PRD/MVP combinado, conservado](../archivo/PRD_MVP_NEXOCREDIT.md) |
| Entorno objetivo | Demo local existente; sin alojamiento o acceso remoto |
| Aceptación formal | Pendiente de revisión y registro |

Este documento define qué debe contener la entrega mínima, cómo priorizarla y cómo verificarla. No autoriza nuevas llamadas de pago, cambios cloud, publicación, uso de datos reales ni instalación para el asesor. La prioridad de una función no determina si ya está implementada.

### Adenda 1.4 — MoSCoW del cambio de reglas — 13/10/2026

Esta adenda prevalece para nuevas evaluaciones sobre el contrato histórico `reglas-demo-v1`. No cambia los resultados guardados ni convierte los rangos ilustrativos en un score oficial.

| Prioridad | Alcance del incremento | Criterio de aceptación |
|---|---|---|
| Must | `reglas-demo-v2`: score 0–499 Alto, 500–679 Medio, 680–1000 Bajo | Diferenciar 499/500 y 679/680; no permitir que un buen margen mejore un score Alto |
| Must | Margen como riesgo mínimo: ≤$7,000 Alto, >$7,000 y ≤$15,000 Medio, >$15,000 Bajo | Resultado igual a la peor categoría de score y margen; calcular con centavos, no con el resumen redondeado |
| Must | Conservar resultados anteriores v1 y su versión | Sin recalcular historial; un reenvío idempotente recupera el resultado original |
| Must | Ayuda y explicación acordes con `version_modelo` | Guía 1.0 para v1 y 2.0 para v2; fallo explícito si no hay guía compatible, sin usar v1 para explicar v2 |
| Must | Resúmenes monetarios en pesos completos | Redondeo visual, ausencia distinta de cero, centavos conservados en captura/cálculos/almacenamiento y detalles de pagos |
| Must | Mantener todas las tecnologías Azure y sus campos de keys | Alternativas locales adicionales, sin borrar adaptadores, credenciales ni evidencias previas |
| Should | Revisar legibilidad en escritorio y móvil | Rangos y advertencias comprensibles, sin depender de un desplegable para conocer la regla |
| Won't en este incremento | Recalcular registros, validar crédito real o atribuir aceptación al asesor | Ninguna conversión de histórico, política oficial o firma inventada |

Con margen de $20,000, score 200 → Alto, 500 → Medio y 700 → Bajo. Con score 900 y margen de $7,000 → Alto. Las categorías son de la demo y no expresan probabilidad de incumplimiento.

El catálogo documental **local** incluye 3 guías / 15 secciones, con fuente `guia-demostracion-v2` / versión 2.0 para las nuevas explicaciones. Azure AI Search conserva la evidencia histórica de 2 guías / 14 secciones hasta cargar y comprobar esa guía. Esta adenda no efectúa nuevas consultas ni cargas cloud. Si se selecciona Azure Search para explicar v2 sin su guía nueva, la ausencia debe mostrarse como fallo, no como éxito basado en contenido v1.

Los importes de tarjetas y resúmenes se redondean a pesos: `$18,333.33` → `$18,333`; los valores originales no cambian. La captura admite centavos; detalle y pagos conservan la precisión necesaria. El margen a dos decimales determina el riesgo aunque su representación se redondee. Las tasas y porcentajes no se convierten a pesos enteros.

La matriz D01–D08 de la sección 7.2 queda como regresión histórica v1: D08 sigue siendo Medio para un registro v1, pero la misma solicitud **nueva** bajo v2 produce Alto. Deben verificarse ambos contratos por versión sin insertar fixtures en la base de trabajo. Esta nota no afirma nuevas suites, despliegue, conectividad externa o aceptación formal. [Manual y criterios completos de las reglas](../manuales/REGLAS_RIESGO_DEMO.md).

### Conservación de Azure — 12/10/2026

**Must:** mantener Azure OpenAI Service, Azure Machine Learning, Azure AI Search y Microsoft Entra ID como integraciones implementadas en la demo, con sus evidencias del 04/10/2026, adaptadores y campos de configuración. La continuidad local no elimina ninguna tecnología obligatoria. Criterio: poder seleccionar Azure explícitamente y completar sus nueve campos en el archivo privado del servidor sin introducir secretos en frontend/documentación, borrar credenciales o cambiar resultados anteriores. [Implementación y ubicación de keys](../manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md).

El modelo scikit-learn local ya incluido es una alternativa académica adicional, no el mismo candidato AutoML ni un nuevo scoring validado para el formulario principal. Sus métricas y pruebas están [documentadas por separado](../manuales/LABORATORIO_IA_LOCAL.md). Esta edición no acredita una nueva llamada Azure, suscripción activa o aceptación formal.

### Seguimiento de la entrega local

Acceso local/Microsoft, Azure/Ollama/plantilla explícitos, documentos Azure/local, revisión RFC/CURP básica con SAT manual, caché/cuotas durables y seguimiento ficticio de planes/abonos/alertas están implementados. Las métricas de línea base posteriores conservan su evidencia separada; no se reetiquetan como CI nueva o aceptación.

| Incremento MoSCoW | Función | Estado / aceptación técnica |
|---|---|---|
| Must — continuidad local | Usuario local y proveedores explícitos sin eliminar Azure | Implementado, sin cuenta/contraseña predeterminada ni ML local inventado |
| Must — seguimiento | Plan de cuotas, pagos parciales y cálculos descriptivos | Implementado; decimal exacto, idempotencia y sobrepago probados |
| Must — alertas | Vencidas, atención con motivo y resolución por saldo | Implementado al operar/recalcular, no scheduler permanente |
| Must — trazabilidad del incremento | Eventos con responsable y lectura global administrativa | Implementado, no auditoría íntegra de toda la aplicación |
| Should — rendimiento local | Medición reproducible acotada | Ejecutada en fixture pequeño; sin certificación de carga productiva |
| Could — ampliación analítica del ledger | Nuevas páginas/medidas Power BI | No incluida: reporte existente conserva evaluaciones |
| Won't — esta implementación | Crédito real, fuente Buró, políticas oficiales, notificación externa y cierre formal | No se simulan ni se activan por este incremento |

Para operar/verificar: [seguimiento](../manuales/SEGUIMIENTO_CREDITICIO.md), [evidencia vigente](../evidencias/2026-10-11/seguimiento-crediticio.md), [arquitectura y datos](../desarrollo/ARQUITECTURA_Y_DATOS.md). Los criterios anteriores siguen como línea base, con prevalencia de esta actualización en acceso, caché y seguimiento. Capacitación/ceremonias/aceptación no se dan por realizadas.

## 1. Definición del MVP

El MVP de NexoCredit es una demostración académica local y autenticada en la que se puede capturar un escenario ficticio, obtener un riesgo demo mediante reglas explícitas, conservarlo, recibir una explicación automática fundamentada y registrar una revisión humana. Debe ser posible recuperar el registro, consultar analítica y demostrar las integraciones obligatorias sin presentarlas como capacidades crediticias productivas.

La unidad mínima de valor es una **evaluación ficticia guardada, comprensible y revisable**. Un resultado que solo aparece en pantalla, sin persistencia o sin distinguir su explicación de una decisión, no completa esa unidad.

### 1.1 Por qué el alcance incluye varias tecnologías

El proyecto exige Python, FastAPI, React.js, Azure OpenAI Service, Azure Machine Learning, Azure AI Search, PostgreSQL, Power BI, Docker, GitHub Actions, Microsoft Entra ID, APIs financieras y Scrum. El MVP no elimina estos requisitos. Reduce profundidad y uso: una demo local, reglas fijas, guías académicas, indicadores públicos, un laboratorio separado y analítica Desktop.

Por eso “mínimo” no significa usar solo un formulario y una base. Significa cumplir cada responsabilidad obligatoria de manera funcional y verificable, sin añadir operación crediticia real, despliegue público o procesos empresariales no acordados.

### 1.2 Resultado observable

Al terminar la demostración, el revisor debe poder contestar:

- Qué campos se capturaron y cuáles afectan el cálculo.
- Qué regla produjo la categoría y qué versión se utilizó.
- Dónde quedó guardada la evaluación y cómo se recupera.
- Qué información recibió la IA y qué guía fundamenta su texto.
- Quién registró la revisión y cómo se conserva el historial.
- Qué datos económicos son públicos y de qué periodo.
- Por qué el experimento UCI no decide el escenario MXN.
- Qué evidencia existe y qué actividades siguen pendientes.

## 2. Escenario de entrega y restricciones

La aplicación se ejecuta en el equipo actual, con Docker Desktop y navegador. El origen probado es http://localhost:8080/. PostgreSQL mantiene un volumen persistente; Power BI Desktop usa un lector local limitado.

La aplicación no es completamente offline. Entra, Azure y los proveedores públicos requieren Internet. El código publicado en GitHub es fuente consultable, no una aplicación alojada. El usuario excluyó acceso remoto e instalación en el equipo del asesor.

La aceptación inicial supone un usuario interactivo. No acredita capacidad multiusuario, alta disponibilidad ni una prueba de carga. Las revisiones simultáneas se verifican como comportamiento de integridad, no como certificación de escala.

Los escenarios deben ser ficticios. No se comparten tokens, claves, dumps, archivos .env, configuraciones Desktop privadas ni expedientes. El texto “Aprobada” se refiere a revisión demo, no a autorización de crédito.

## 3. Método de priorización MoSCoW

| Categoría | Regla de decisión |
|---|---|
| Must have | Su ausencia impide aceptar el MVP o cumplir una tecnología obligatoria |
| Should have | Mejora relevante, pero se puede diferir con límites y riesgos documentados |
| Could have | Aporta comodidad o presentación; no modifica el flujo mínimo |
| Won't have this release | Exclusión explícita de esta entrega, no promesa de implementación posterior |

No se asignan porcentajes de esfuerzo ni fechas sin estimación y capacidad acordadas. MoSCoW no sustituye una decisión de presupuesto ni convierte una función pendiente en completada.

Las mejoras de seguridad, validación crediticia y operación necesarias para clientes reales no se consideran “opcionales” de una futura producción. Simplemente no se pretende operar con esa población en este MVP.

## 4. Matriz MoSCoW de la entrega

### 4.1 Must have

| ID | Capacidad mínima | Justificación | Estado de línea base |
|---|---|---|---|
| M01 | Identidad y autorización Microsoft Entra ID | Evitar negocio anónimo y obtener responsable verificable | Implementada en demo |
| M02 | Captura validada y reglas versionadas | Resultado reproducible y límites explícitos | Implementada |
| M03 | PostgreSQL, idempotencia, historial y detalle | Conservar unidad mínima de valor | Implementados localmente |
| M04 | Revisión humana versionada | Separar clasificación y juicio humano | Implementada; no auditoría integral |
| M05 | Explicación automática OpenAI con contexto Search | Cumplir IA generativa sin botón adicional | Implementada; consulta real observada |
| M06 | Catálogo y búsqueda Azure AI Search | Fundamentación y documentos accesibles | Dos guías / catorce secciones observadas |
| M07 | Laboratorio Azure ML separado | Demostrar tecnología sin atribuir validación crediticia | Endpoint conectado; límites documentados |
| M08 | Indicadores Banxico y Banco Mundial | Contexto económico público con procedencia | Integraciones comprobadas |
| M09 | Dashboard React y Power BI Desktop | Consulta agregada y analítica obligatoria | Comprobación local fechada |
| M10 | Docker, migraciones y GitHub Actions | Ejecución y verificación reproducibles | Comprobados |
| M11 | Respaldo y restauración aislada | Proteger trabajo y verificar recuperación | Ensayo manual comprobado |
| M12 | Identidad NexoCredit y mensajes de alcance | Evitar marca anterior y expectativas incorrectas | Presentación adaptada |
| M13 | Documentación, evidencia, revisión y proceso Scrum real | Entrega académica verificable | Documentos/backlog; aceptación y eventos pendientes |

### 4.2 Should have

| ID | Mejora | Beneficio | Condición de cierre |
|---|---|---|---|
| S01 | Prueba de accesibilidad y tareas | Detectar barreras y confusión | Recorrido por teclado, foco, etiquetas y observaciones reales |
| S02 | Benchmark local reproducible | Medir respuesta sin atribuir SLA | Equipo, muestra y p95 documentados |
| S03 | Mayor fijación de dependencias e imágenes | Reducir diferencias entre entornos | Versiones/digests, regresión y documentación |
| S04 | Comparación binaria del candidato ML remoto/local | Mejorar trazabilidad del artefacto servido | Huellas y método verificables |
| S05 | Práctica guiada ampliada con asesor | Facilitar uso y registrar aprendizaje | Sesión realizada y observaciones registradas |

M13 exige documentación básica y revisión formal realmente registrada. S05 se refiere a una práctica o capacitación ampliada, no a omitir la aceptación básica. S04 puede diferirse para la demo local con advertencia; antes de afirmar identidad exacta del artefacto sería un requisito obligatorio de esa afirmación.

### 4.3 Could have

| ID | Mejora | Alcance permitido si se acuerda |
|---|---|---|
| C01 | Exportación de agregados demo | CSV sin identificadores, responsables ni observaciones |
| C02 | Persistencia optativa de explicación | Solo tras definir privacidad, versión, retención y coste |
| C03 | Gráficos complementarios | Comparaciones temporales que no alteren reglas |

Estas mejoras pertenecen a la propuesta histórica. C02 ya se implementó posteriormente como caché privada PostgreSQL de 24 h; su caducidad limita reutilización, no elimina el texto. C01/C03 no se declaran implementadas por esta actualización. Consultar los límites del incremento y su evidencia, sin convertirlo en aceptación formal.

### 4.4 Won't have this release

| ID | Exclusión | Motivo |
|---|---|---|
| W01 | Alojamiento, acceso remoto o instalación para el asesor | Decisión expresa del usuario |
| W02 | Crédito real, Buró e historial privado | Sin datos/políticas/autorización y validación pertinentes |
| W03 | Aprobar, rechazar o desembolsar automáticamente | La demo apoya comprensión, no decisiones reales |
| W04 | Operación productiva, gateway y cloud Power BI | Sin SLA, CD, presupuesto o controles acordados |

También queda excluida la conversión automática de MXN a variables UCI. Las unidades, población, fecha y significado de variables son diferentes.

## 5. Especificación verificable de cada Must

### M01 — Acceso seguro en servidor

Se utiliza MSAL y verificación JWT en FastAPI. Los roles Analista y Administrador permiten las funciones demo actuales; no se presume administración diferenciada.

**Criterios de aceptación:**

1. Una cuenta autorizada puede iniciar sesión y acceder a negocio.
2. Ausencia o token inválido produce 401; ámbito/rol insuficiente produce 403.
3. Firma, emisor, audiencia, tenant, cliente y vigencia se verifican en servidor.
4. La indisponibilidad de verificación no habilita acceso anónimo.
5. Configuración pública y OpenAPI no exponen evaluaciones o secretos.

**Evidencia mínima:** pruebas negativas, configuración depurada y recorrido de sesión válido. No se reclama pentest o cumplimiento productivo.

### M02 — Datos y clasificación demo

El formulario recoge RFC ficticio, ingresos, gastos, deuda, pagos, atraso y score. El cálculo utiliza ingresos, gastos y score; no simula un histórico de Buró.

**Criterios de aceptación:**

1. Se validan tipos, rangos, campos adicionales y valores no finitos.
2. El resultado nuevo indica margen, Bajo/Medio/Alto, `reglas-demo-v2` y advertencia; los anteriores conservan `reglas-demo-v1`.
3. Se respetan los cortes de score 500/680 y de margen 7,000/15,000: el peor riesgo de las dos variables determina la categoría, conforme a la adenda 1.4.
4. Deuda/pagos/atraso no modifican estas reglas demo.
5. Los pagos no se restan dos veces de los ingresos.

**Límite:** dinero con float/round actual; no se declara una implementación Decimal.

### M03 — Persistencia e idempotencia

PostgreSQL guarda solicitud y resultado con UUID y fecha UTC. El historial es paginado; detalle recupera el registro completo.

**Criterios de aceptación:**

1. Con base configurada, una evaluación guardada permanece tras recarga.
2. Mismo Idempotency-Key y mismos datos devuelven la misma evaluación.
3. Misma clave y otros datos producen 409.
4. UUID inexistente produce 404.
5. Un fallo de base no se muestra como guardado confirmado.
6. El modo no guardado sin configuración no se utiliza para dar por aceptado este Must.

**Evidencia mínima:** prueba de guardado/recuperación y casos idempotentes sobre PostgreSQL de ensayo.

### M04 — Revisión humana e integridad

Se conserva cada revisión con estado, motivo, identidad Entra, fecha y versión. Las revisiones anteriores y el riesgo original permanecen.

**Criterios de aceptación:**

1. Se admiten exclusivamente los estados demo definidos.
2. Se registra motivo válido y responsable obtenido del servidor.
3. Una versión anterior desactualizada produce 409 sin sobrescritura.
4. La nueva versión queda asociada a la evaluación.
5. La interfaz distingue “Aprobada — revisión demo” de crédito aprobado.

**Límite:** no hay auditoría completa de lecturas; registros anteriores a Entra pueden contener responsable declarado.

### M05 — Explicación automática fundamentada

Después de confirmar el guardado, el frontend solicita la explicación del UUID. Search aporta DEM-02 y OpenAI redacta sin controlar el riesgo.

**Criterios de aceptación:**

1. No se requiere un segundo botón para iniciar la generación.
2. El servidor explica datos persistidos, no un resultado arbitrario enviado por el cliente.
3. No se incluyen RFC, identidad, UUID ni revisiones en el contenido enviado al modelo.
4. La respuesta incluye guía/sección/versión y aviso de revisión humana.
5. Un fallo de IA o Search no elimina ni modifica el registro.
6. Una respuesta tardía no se muestra sobre otro escenario.

**Límite:** deduplicación en memoria por UUID, no global. La validación de estructura y fuentes no garantiza exactitud universal.

### M06 — Documentos y búsqueda

Se presentan las dos guías y catorce secciones académicas, con fuentes y versiones.

**Criterios de aceptación:**

1. El catálogo es completo para la línea base.
2. La búsqueda valida texto de 2–200 caracteres y limita fragmentos.
3. Se mantiene la procedencia del contenido.
4. No se admiten destinos o filtros arbitrarios.
5. Fallo remoto genera estado de error, no documentos fabricados.

**Límite:** son guías demo propias, no políticas empresariales aprobadas.

### M07 — Laboratorio Azure ML

El laboratorio utiliza diecinueve variables UCI y presenta una clase booleana remota.

**Criterios de aceptación:**

1. Tipos, orden y límites de variables se validan.
2. La configuración y el resultado remoto se distinguen.
3. Se muestran población Taiwán/2005 y unidades NTD.
4. No se llama probabilidad a una etiqueta.
5. No se guarda ni modifica una evaluación principal.
6. El fallo remoto afecta solo el laboratorio.

**Evidencia mínima:** contrato probado, metadatos fechados y prueba de integración ya registrada. La comparación binaria S04 sigue pendiente.

### M08 — Contexto económico

Banxico aporta FIX y tasa objetivo; Banco Mundial, inflación y crecimiento del PIB de México.

**Criterios de aceptación:**

1. Cada observación contiene valor, unidad, periodo y fuente.
2. Hora de consulta y periodo observado se distinguen.
3. Un proveedor fallido no invalida al otro.
4. Se muestran estados veraces de configuración, disponibilidad y caché.
5. Cero, negativos y ausencias no se confunden.
6. No se envían datos del solicitante ni se altera el riesgo.

**Límite:** no son datos de tiempo real ni un monitor continuo.

### M09 — Analítica coherente

React calcula agregados en servidor para toda la población filtrada. Power BI Desktop importa una vista limitada.

**Criterios de aceptación:**

1. Totales y promedios no se calculan solo sobre la página del historial.
2. Deuda ausente no se convierte en cero; cero capturado sí participa.
3. Fechas UTC inclusivas y filtros se interpretan correctamente.
4. Power BI no importa RFC, responsable o notas desde la vista.
5. Las seis medidas se concilian en los dieciséis contextos definidos.
6. La comparación web/Power BI indica corte y actualización manual.

**Evidencia mínima:** SQL/DAX, filtros y capturas con fecha. No implica publicación cloud.

### M10 — Entorno y calidad automatizada

Docker Compose mantiene frontend, backend, PostgreSQL y migraciones. GitHub Actions verifica sin secretos productivos ni llamadas cloud.

**Criterios de aceptación:**

1. La aplicación inicia en el entorno local acordado.
2. Migraciones repetidas no duplican estructura ni registros de versión.
3. Suites backend/frontend, lanzadores, lint/build y audit cumplen el protocolo.
4. La evidencia identifica commit y ejecución.
5. Los ensayos aislados no usan ni borran la base de trabajo.

**Línea base:** 69 pruebas backend y 48 frontend aprobadas; no se fija ese número como condición inmutable si cambia la suite.

### M11 — Recuperación ensayada

El respaldo manual produce dump y manifiesto privados. La prueba restaura en un contenedor temporal controlado y compara datos.

**Criterios de aceptación:**

1. Se conserva la identidad del origen y el respaldo.
2. Esquema, filas, huellas y vista se concilian en destino aislado.
3. La base original queda intacta.
4. Los artefactos no se agregan a la entrega pública.
5. Se documentan límites: sin cifrado, roles globales/ACL o RPO/RTO productivo.

El lanzador de prueba crea un respaldo nuevo por defecto; probar uno existente requiere el argumento correspondiente. No debe confundirse ensayo de un respaldo nuevo con restauración del archivo que el operador tenía previamente.

### M12 — Marca y mensajes

La marca de presentación es NexoCredit. Los identificadores técnicos existentes se conservan si renombrarlos rompería conexiones.

**Criterios de aceptación:**

1. Login, navegación y textos propios presentan la marca nueva.
2. No se presenta NexoCredit como razón social o empresa acreditada.
3. Se distinguen reglas demo, explicación IA y revisión.
4. Indicadores públicos y UCI muestran sus límites.
5. Los nombres técnicos antiguos no se interpretan como un fallo de marca funcional.

### M13 — Entrega, revisión y Scrum

La documentación básica debe explicar operación, datos ficticios, contratos, límites, recuperación y evidencia. El PRD/MVP deben revisarse realmente.

**Criterios de aceptación:**

1. Manuales, alcance y código no se contradicen.
2. La evidencia identifica fechas, versión y pruebas realmente realizadas.
3. Se registra revisión del asesor/usuario y su decisión, después de ocurrir.
4. Se acuerdan responsables y se conservan registros reales de los eventos Scrum aplicados.
5. No se acreditan retrospectivamente participantes, ceremonias o 500 horas.

**Situación:** documentación y backlog existentes; aceptación y proceso real no cerrados.

## 6. Historias de usuario y criterios Given–When–Then

Estas historias concretan los Must. Los criterios son un protocolo de aceptación; su presencia no significa que todos hayan sido ejecutados en esta edición.

| Historia | Necesidad | Criterio observable |
|---|---|---|
| US01 / M01 | Como analista, quiero acceder con Microsoft | Dada una cuenta autorizada, cuando inicia sesión, entonces el servidor permite negocio con identidad válida |
| US02 / M02 | Quiero capturar un escenario ficticio válido | Dados campos fuera de rango, cuando evalúo, entonces recibo validación y no un éxito aparente |
| US03 / M02 | Quiero conocer por qué obtuve una categoría | Dados ingresos/gastos/score, cuando evalúo, entonces margen y riesgo corresponden a la regla versionada |
| US04 / M03 | Quiero evitar duplicados al reenviar | Dada la misma clave y solicitud, cuando reenvío, entonces recupero el UUID original |
| US05 / M03 | Quiero consultar después de recargar | Dado un guardado confirmado, cuando recargo y abro detalle, entonces recupero solicitud y resultado |
| US06 / M05 | Quiero explicación sin otro botón | Dado un UUID guardado, cuando termina la evaluación, entonces inicia generación sin otra acción |
| US07 / M05 | Quiero conservar el resultado aunque falle IA | Dado un fallo simulado de generación, cuando termina, entonces el registro sigue recuperable y el fallo es visible |
| US08 / M04 | Quiero dejar una revisión identificable | Dada una versión vigente, cuando reviso, entonces se conserva nueva versión con responsable del servidor |
| US09 / M04 | Quiero que no se pierdan revisiones concurrentes | Dada una versión desactualizada, cuando envío, entonces recibo 409 y no sobrescribo |
| US10 / M06 | Quiero conocer las fuentes | Dado un catálogo disponible, cuando abro documentos, entonces veo guías/secciones/versiones reales |
| US11 / M08 | Quiero indicadores confiables en su contexto | Dado un proveedor fallido, cuando consulto, entonces su error no elimina datos válidos del otro |
| US12 / M07 | Quiero explorar ML sin mezclar experimentos | Dadas variables UCI, cuando consulto, entonces recibo clase académica sin cambiar evaluación MXN |
| US13 / M09 | Quiero analítica de toda mi selección | Dados filtros, cuando consulto, entonces los agregados corresponden a todos los registros coincidentes |
| US14 / M10–11 | Quiero comprobar y recuperar sin dañar datos | Dado un ensayo aislado, cuando termina, entonces evidencia y origen quedan verificables |
| US15 / M12–13 | Quiero una entrega que pueda evaluar | Dada una demostración, cuando la reviso, entonces identifico alcance, pendientes y evidencia sin secretos |

## 7. Datos ficticios para aceptación

### 7.1 Reglas de preparación

Utilizar identificadores como DEMO-A01, no RFC o expedientes reales. Los importes están en MXN para el formulario principal. Score es capturado, no verificado.

Para una nueva campaña integral se propone un conjunto versionado de veinte fixtures que cubra las tres categorías, umbrales, score, ausencia histórica y cero capturado. La cantidad es una propuesta de prueba, no el número actual de registros en PostgreSQL.

No se deben insertar esos fixtures en la base de trabajo sin acuerdo. Las pruebas automáticas deben usar destinos aislados. Las comparaciones manuales se documentan con un corte fijo.

### 7.2 Matriz histórica de límites deterministas — reglas-demo-v1

Esta tabla conserva los resultados de la línea base v1. Para solicitudes nuevas v2 prevalece la adenda 1.4 del 13/10/2026; el caso D08 cambia a Alto sólo para una nueva evaluación, no para el registro histórico.

| Caso | Ingresos | Gastos | Score | Margen esperado | Riesgo esperado |
|---|---:|---:|---:|---:|---|
| D01 | 30,000.00 | 10,000.00 | 700 | 20,000.00 | Bajo |
| D02 | 30,000.00 | 15,000.00 | 700 | 15,000.00 | Medio |
| D03 | 30,000.00 | 22,999.99 | 700 | 7,000.01 | Medio |
| D04 | 30,000.00 | 23,000.00 | 700 | 7,000.00 | Alto |
| D05 | 30,000.00 | 10,000.00 | 679 | 20,000.00 | Medio |
| D06 | 30,000.00 | 35,000.00 | 700 | -5,000.00 | Alto |
| D07 | 30,000.00 | 14,999.99 | 680 | 15,000.01 | Bajo |
| D08 | 30,000.00 | 14,999.99 | 0 | 15,000.01 | Medio |

La interpretación se realiza después del redondeo actual a dos decimales. Los casos de representación flotante y redondeo deben tratarse como regresión si se migra a Decimal; no se cambia silenciosamente la regla.

Para cada caso, variar deuda/pagos/atraso no debe alterar reglas-demo-v1. Los gastos ya incluyen pagos de crédito. Si un caso muestra otro resultado, investigar antes de dar por válida la explicación de IA.

### 7.3 Casos inválidos y de ausencia

| Caso | Entrada | Resultado requerido |
|---|---|---|
| V01 | Ingreso cero o negativo | Rechazo de validación |
| V02 | Gasto/deuda/pagos negativos | Rechazo de validación |
| V03 | Score fraccionario, menor que 0 o mayor que 1000 | Rechazo de validación |
| V04 | Atraso fraccionario, negativo o mayor que 36,500 | Rechazo de validación |
| V05 | Número no finito o campo adicional | Rechazo de contrato |
| V06 | RFC vacío | Rechazo; no exigir una verificación fiscal inexistente |
| V07 | Deuda histórica nula | Excluir de promedio; no sustituir por cero |
| V08 | Deuda capturada igual a cero | Incluir como valor informado |
| V09 | Página de historial con menos filas que el total | Dashboard conserva total de la población filtrada |

La UI exige deuda/pagos/atraso, pero la API admite ausencia para compatibilidad histórica. Ese comportamiento no debe declararse una contradicción sin distinguir ambos contratos.

## 8. Estrategia de pruebas

### 8.1 Capas de validación

1. **Unidad y contrato:** validadores, reglas, estados, referencias y límites.
2. **Persistencia:** PostgreSQL temporal, migraciones, idempotencia y revisiones.
3. **Frontend:** cambios de estado, deduplicación de pantalla y respuestas tardías.
4. **Integración simulada:** fallos externos, contratos malformados y timeout sin gasto.
5. **Prueba real controlada:** conectividad y flujo con recursos existentes, cuando se acuerde.
6. **Analítica:** SQL, agregados API y DAX sobre mismo corte.
7. **Operación:** arranque, respaldo y restauración aislada.
8. **Aceptación humana:** comprensión, observaciones y decisión registradas.

Una prueba con mocks acredita comportamiento del software bajo el escenario definido, no conectividad real. Una consulta cloud exitosa acredita ese momento, no uptime ni exactitud de todas las respuestas.

### 8.2 Matriz de integración y fallos

| ID | Escenario | Método preferido | Resultado exigido |
|---|---|---|---|
| T01 | Acceso sin token | Solicitud local / suite | 401 sin datos de negocio |
| T02 | Token o permisos incorrectos | Mock/verificación de contrato | 401/403 según condición |
| T03 | Guardado e historial | PostgreSQL aislado | Registro recuperable |
| T04 | Reenvío idéntico y cambiado | PostgreSQL aislado | Mismo UUID / 409 |
| T05 | Dos revisiones sobre misma versión | Ensayo aislado | Una válida y conflicto sin pérdida |
| T06 | OpenAI no disponible | Mock | Registro intacto y error de explicación |
| T07 | Search sin contexto válido | Mock | No inventar guía ni explicación fundamentada |
| T08 | Respuesta IA tardía tras cambiar escenario | Prueba frontend | No asociarla al UUID nuevo |
| T09 | JSON/referencia de IA incorrectos | Mock | Rechazo controlado |
| T10 | Banxico falla y Banco Mundial responde | Mock | Estados independientes |
| T11 | Valor cero/negativo/nulo de indicador | Fixture | Semántica conservada |
| T12 | Variables UCI inválidas | Contrato local | No invocar endpoint |
| T13 | Salida ML no booleana o timeout | Mock | Error, no probabilidad inventada |
| T14 | Sin registros o deuda nula | SQL/fixtures | Conteos y promedios semánticamente correctos |
| T15 | Corte/filtros Power BI | Desktop + SQL | Conciliación sin diferencias |
| T16 | Restauración de respaldo | Destino temporal | Huellas/esquema/filas conciliados; origen intacto |
| T17 | Recarga y nueva generación | Observación controlada | Explicar límite de memoria y posible coste |
| T18 | Datos enviados a proveedores | Inspección de pruebas/contratos | Exclusión de campos privados indicada |

Los IDs T identifican este protocolo ampliado. La evidencia existente puede cubrir algunos comportamientos, pero no se considera automáticamente una ejecución completa de T01–T18.

### 8.3 Rúbrica de explicaciones IA

Se propone validar seis escenarios ficticios antes de cerrar la meta de calidad semántica. Cada explicación debe:

- Calcular o describir correctamente margen y score utilizados.
- Respetar el orden y los límites estrictos de las reglas.
- No atribuir al modelo una probabilidad de incumplimiento.
- Citar guía, sección y versión recuperadas.
- No inventar identidad, deuda externa o política empresarial.
- No sugerir que autoriza crédito.

La meta propuesta es seis de seis sin contradicciones de la regla y con referencia correcta. Un fallo requiere revisar el caso y la causa; no “corregir” el scoring para ajustarlo al texto. Las seis llamadas reales no se ejecutan por redactar esta matriz ni se autorizan sin considerar consumo.

### 8.4 Protocolo de analítica

Utilizar un corte idéntico de datos y aplicar los dieciséis contextos de filtrado definidos para las seis medidas. Registrar conteo total, margen promedio, deuda promedio informada, cobertura de deuda, evaluaciones con deuda e ingresos promedio.

Meta: cero diferencias en noventa y seis comparaciones. La evidencia del 30/09/2026 ya registró ese resultado para su muestra. Repetir al cambiar vista o medidas; una muestra de otra fecha no hereda automáticamente la conciliación.

Los filtros React, historial y Power BI son controles diferentes. Una captura web actual y un reporte importado anterior no constituyen por sí mismos un defecto de agregación.

## 9. Métricas de aceptación

| Métrica | Meta del MVP | Medición y situación |
|---|---|---|
| Reglas correctas | 100 % de casos definidos | Tabla D y suite; preservar versión |
| Reenvíos idénticos duplicados | 0 | Misma clave/mismos datos |
| Revisiones perdidas por conflicto | 0 en casos de aceptación | Versiones y restricciones |
| Acceso negativo permitido | 0 en casos definidos | 401/403 y pruebas; no pentest |
| Explicaciones sin contradicción/fuente correcta | 6/6 propuestas | Rúbrica pendiente de campaña |
| Catálogo demo | 2 guías / 14 secciones | Línea base observada |
| Indicadores con procedencia | 100 % de observaciones mostradas | Fuente, unidad, periodo |
| Diferencias SQL–DAX | 0 en protocolo | 96 comparaciones históricas |
| Suites y construcción | Sin fallos u omisiones inesperadas | Baseline 69 backend / 48 frontend |
| Restauración conciliada | Sin diferencias en ensayo | Tres tablas y vista, destino aislado |
| Comprensión de límites | Meta/participantes por acordar | No hay medición de usuario acreditada |
| Respuesta local, Should | p95 <= 2 segundos propuestos | Cien operaciones, un usuario, sin externos |

Ninguna métrica implica reducción de mora ni adecuación del modelo para México. AUC 0.775274 y sensibilidad 32.01 % corresponden al experimento UCI local, no a este formulario.

## 10. Trazabilidad de requisitos, pruebas y tecnologías

| Must | Requisitos PRD | Casos de uso | Pruebas clave | Tecnología responsable |
|---|---|---|---|---|
| M01 | PRD-RF01 | UC01 | T01–T02 | Entra, React/MSAL, FastAPI |
| M02 | PRD-RF02–03 | UC02 | D01–D08, V01–V06 | Python, FastAPI, React |
| M03 | PRD-RF04–05 | UC02–03 | T03–T04 | PostgreSQL, FastAPI |
| M04 | PRD-RF06 | UC05 | T05 | PostgreSQL, Entra, React |
| M05 | PRD-RF07 | UC04 | T06–T09, T17–T18 | OpenAI, Search, React |
| M06 | PRD-RF08 | UC06 | T07, catálogo/búsqueda | Azure AI Search |
| M07 | PRD-RF10 | UC09 | T12–T13 | Azure ML, Python |
| M08 | PRD-RF09 | UC08 | T10–T11, T18 | Banxico, Banco Mundial |
| M09 | PRD-RF11–12 | UC07/10 | T14–T15, V07–V09 | React, PostgreSQL, Power BI |
| M10 | PRD-RF13 | UC11 | Suites y migraciones | Docker, GitHub Actions |
| M11 | PRD-RF14 | UC11 | T16 | PostgreSQL, Docker |
| M12 | PRD-RF15 | Todos | Revisión visual y límites | React y documentación |
| M13 | Alcance/entrega del PRD | Todos | Revisión formal/evidencia | Scrum y entregables |

La tabla permite localizar responsabilidades; no afirma que todos los escenarios nuevos estén ejecutados. Los RF del plan previo mantienen su numeración original.

## 11. Puertas de aceptación y Definition of Done

### 11.1 G0 — Alcance revisado

PRD, MoSCoW, límites y supuestos se revisan con usuario/asesor. Las observaciones y la decisión se registran realmente. No se requiere habilitar acceso remoto para esta revisión.

**Estado:** documentos disponibles; aprobación pendiente.

### 11.2 G1 — Núcleo íntegro

Autenticación, validación, guardado, consulta, idempotencia y revisión tienen evidencia. No se acepta una evaluación no guardada como equivalente a la unidad mínima de valor.

**Estado:** comportamiento técnico comprobado en línea base; mantenerlo al cambiar código.

### 11.3 G2 — Integraciones honestas

OpenAI/Search, finanzas y ML cumplen contratos, minimización y separación. Los fallos no fabrican éxito ni modifican riesgo.

**Estado:** integraciones observadas y pruebas existentes; la nueva rúbrica de seis explicaciones sigue propuesta. Metadatos ML no equivalen a comparación binaria.

### 11.4 G3 — Analítica y recuperación

Medidas comparables, corte identificado y respaldo/restauración aislada conciliados.

**Estado:** evidencia fechada disponible; repetir si cambian los elementos relevantes.

### 11.5 G4 — Calidad y entrega depurada

La versión sometida a revisión debe identificar commit, suites y CI. No debe incluir configuraciones privadas o datos sensibles.

**Estado:** CI final de línea base aprobada. Este documento no ejecuta una CI nueva ni afirma que main haya recibido los cambios.

### 11.6 G5 — Cierre académico real

Manual básico, revisión, observaciones y evidencia Scrum se registran cuando ocurren. La capacitación ampliada S05 puede diferirse; la revisión/aceptación básica M13 no.

**Estado:** pendiente. No se acredita el cierre formal por tener una carpeta de Scrum.

### 11.7 Definition of Done

El MVP se considera aceptable cuando:

- Todos los Must cumplen sus criterios o existe una decisión explícita de cambiar el alcance.
- Las pruebas relevantes pasan y la evidencia corresponde a la versión entregada.
- Se conoce el corte de datos de analítica y no se confunden muestras distintas.
- Se comprueba persistencia, revisión y degradación sin pérdida de resultado.
- Las integraciones conservan fuentes, contratos y límites de datos.
- El ensayo de recuperación no afecta la base original.
- Los manuales y documentos no contradicen el comportamiento.
- Se registra aceptación o rechazo real y el proceso Scrum aplicado.

Actualmente puede afirmarse “núcleo técnico de demo comprobado”. No puede afirmarse “MVP formalmente aceptado”, “modelo validado para crédito” o “producto listo para clientes”.

## 12. Backlog de cierre propuesto

| ID | Trabajo | Prioridad | Dependencia | Evidencia esperada |
|---|---|---|---|---|
| BC01 | Revisar PRD/MVP y resolver observaciones | Must | Usuario/asesor disponible | Decisión fechada |
| BC02 | Conciliar manual básico con rutas y límites | Must | Línea base identificada | Revisión documental |
| BC03 | Consolidar trazabilidad de evidencia existente | Must | Documentos de QA/CI | Índice por versión/caso |
| BC04 | Ejecutar metas de aceptación nuevas acordadas | Must para metas aceptadas | Autoridad y coste definidos | Protocolo y resultados reales |
| BC05 | Registrar revisión académica y resolución de hallazgos | Must | BC01–BC04 | Observaciones/correcciones/decisión |
| BC06 | Acordar y documentar el proceso Scrum real | Must | Responsabilidades/capacidad | Registros de eventos reales |
| BC07 | Evaluar tareas/teclado y comprensión | Should | Participantes confirmados | Hallazgos y limitaciones |
| BC08 | Medir benchmark local | Should | Equipo y protocolo fijados | Muestra y p95 |
| BC09 | Fijar dependencias e imágenes restantes | Should | Análisis de impacto | Versiones y regresión |
| BC10 | Comparar huellas de artefacto ML | Should | Acceso autorizado a artefactos | Método y hashes |
| BC11 | Realizar práctica guiada ampliada | Should | Asesor disponible | Registro de práctica |
| BC12 | Evaluar exportación/gráficos/explicación persistida | Could | Decisión de alcance | Diseño previo, no código asumido |

BC04 no significa ejecutar todas las pruebas cloud ahora. El protocolo debe indicar qué cubren suites existentes, qué se simula y qué consultas reales se acuerdan. Un bloqueo de presupuesto no autoriza ocultar un resultado pendiente.

No se estiman horas sin capacidad. El plan histórico de 500 horas es una propuesta, no un registro trabajado. Las tareas pueden reagruparse tras la revisión de alcance.

## 13. Organización Scrum propuesta

Se propone trabajar en sprints de dos semanas si el calendario académico y la capacidad lo permiten. Es una estructura sugerida, no una descripción de eventos pasados.

### 13.1 Responsabilidades por acordar

El responsable de producto prioriza y acepta objetivos; quien facilita Scrum atiende impedimentos y mejora del proceso; quienes desarrollan y verifican mantienen la calidad. No se asignan nombres ni se atribuye al asesor un cargo sin confirmación.

### 13.2 Secuencia posible de cierre

| Bloque de trabajo | Objetivo | Resultado |
|---|---|---|
| A — Alinear alcance | Revisar documentación y metas | Backlog confirmado y criterios acordados |
| B — Validar entrega | Ejecutar comprobaciones faltantes sin ampliar alcance | Evidencia y defectos priorizados |
| C — Revisar y aceptar | Demostrar, resolver hallazgos y registrar decisión | Entrega aceptada o pendientes explícitos |

Los bloques no son sprints acreditados y no tienen fechas ficticias. La planificación debe registrar objetivo, selección de trabajo y capacidad real. El seguimiento registra progreso e impedimentos. La revisión registra el resultado presentado y las observaciones. La retrospectiva registra mejoras para el siguiente trabajo.

La referencia de proceso es la [Guía Scrum](https://scrumguides.org/scrum-guide.html). Un backlog o plantilla no sustituye los eventos ni constituye evidencia de horas.

### 13.3 Definition of Ready para una tarea

Antes de ejecutar una tarea se requiere necesidad clara, alcance delimitado, criterio verificable, dependencia identificada y autoridad suficiente. Si implica cloud o datos, se conoce consumo y destino. Si implica una corrección, se conoce el defecto y la regresión necesaria.

## 14. Guion de demostración local

Este guion es una propuesta para una sesión acordada. No crea cuentas, no inicia servicios ni realiza llamadas por sí mismo.

### 14.1 Preparación

1. Identificar versión/commit y corte que se mostrará.
2. Comprobar aplicación local y sesión autorizada.
3. Preparar datos ficticios y explicar que no se consultará Buró.
4. Verificar configuración sin mostrar secretos.
5. Acordar si se permite generación real de IA/consulta ML y su consumo.
6. Preparar evidencia de fallos simulados; no provocar una caída productiva.
7. Abrir Power BI Desktop solo si forma parte de la sesión y actualizar conscientemente.

### 14.2 Recorrido principal

Ingresar DEMO-A01 con ingresos 30,000, gastos 10,000 y score 700; deuda/pagos/atraso ficticios válidos. Mostrar margen 20,000, riesgo Bajo y versión. Confirmar guardado antes de presentar la explicación automática.

Abrir el detalle y recuperar la misma evaluación. Registrar una revisión demo con motivo claro. Mostrar identidad del responsable y versión, sin revelar token. Explicar que el riesgo original permanece.

Mostrar historial y dashboard con filtros. Si se compara Power BI, utilizar corte equivalente e identificar actualización manual.

### 14.3 Recorridos complementarios

Abrir documentos, mostrar fuente y buscar una regla. Consultar indicadores y distinguir periodo/hora de consulta. Abrir laboratorio UCI y explicar variables/unidades antes de cualquier llamada acordada.

Presentar evidencia de CI y restauración. Mostrar que un fallo de IA simulado deja el resultado guardado. No es necesario causar un fallo real de Entra, PostgreSQL o proveedores para acreditar manejo de errores.

### 14.4 Cierre de la sesión

Solicitar observaciones sobre comprensión y recorrido, registrar hallazgos y dejar la decisión de aceptación explícita. No generar firmas, resultados o capacitación automática a partir de este guion.

## 15. Paquete de entrega y cuidado de información

### 15.1 Material que se puede incluir

- PRD y MVP separados.
- README, requisitos tecnológicos, manual básico y límites.
- Contratos y código de la versión revisada.
- Evidencia de QA, CI, prueba integral y recuperación depurada.
- Fuente de reporte Power BI y definición de medidas sin cachés privadas.
- Backlog y registros Scrum realmente existentes.
- Guion y observaciones de revisión cuando ocurran.

### 15.2 Material que no se debe incluir

Tokens Entra, claves Azure/Banxico, .env privados, dumps, archivos con datos sensibles, cachés Desktop o configuraciones locales de conexión. Tampoco un binario de modelo no requerido por la ejecución backend.

Eliminar un archivo del seguimiento Git no borra su historia anterior. El paquete debe revisarse sin afirmar que esa exclusión sanea por sí sola todo el historial.

El paquete no incluye instalador remoto ni instrucciones para abrir puertos públicos. Un enlace al repositorio permite consultar código; no garantiza que el asesor pueda ejecutar el entorno ni sustituye la demostración local acordada.

## 16. Riesgos, decisiones y condiciones de no aceptación

| Condición | Consecuencia |
|---|---|
| Se afirma guardado sin confirmación PostgreSQL | No acepta M03 |
| IA modifica categoría o revisión | No acepta M04/M05 |
| No se explica separación UCI/MXN | No acepta M07 |
| Se presentan valores inventados ante fallo externo | No acepta M06/M08 |
| Power BI compara cortes distintos como si fueran iguales | Repetir conciliación antes de aceptar esa métrica |
| Se exponen secretos en entrega o capturas | Detener entrega afectada y tratar incidente |
| Se declara Scrum/horas sin registros reales | No acepta M13 |
| Se amplía a clientes reales sin nuevos controles | Fuera del alcance aprobado |
| Se publica aplicación pese a W01 | Cambio no autorizado por este MVP |

Si una meta Should no se cumple, registrar el riesgo y la decisión de diferir. Si un Must no se cumple, no usar el resto de las pruebas para declarar aceptación total. Una aceptación parcial debe especificar exactamente qué fue revisado.

Antes de cualquier evolución productiva se necesitarían autorización de datos, políticas, validación poblacional/temporal del modelo, calibración, revisión por segmentos, roles diferenciados, auditoría, cuotas, cifrado/retención, TLS y operación/recuperación acordadas.

## 17. Evidencia disponible y límites actuales

| Elemento | Evidencia de línea base | Qué no demuestra |
|---|---|---|
| CI final | Run 37247558296, SHA 914ac8aa7abfeefae746dda4bd9c59ec9191719d | Despliegue productivo o merge a main |
| Backend/frontend | 69 y 48 pruebas, sin omisiones en esa ejecución | Todos los escenarios futuros |
| npm audit | Cero reportado en la ejecución registrada | Ausencia permanente de vulnerabilidades |
| Power BI | 6 medidas, 16 contextos, 96 comparaciones sin diferencias | Sincronización continua |
| Finanzas | Ambos proveedores disponibles el 04/10/2026 | Uptime o datos en tiempo real |
| Azure ML | Metadatos correctos y tráfico 100 % al candidato v1 | Identidad binaria ni validez para México |
| Experimento UCI | 5,955 registros; AUC 0.775274, sensibilidad 32.01 % | Probabilidad individual calibrada |
| Recuperación | Tres tablas conciliadas en destino aislado | Roles/ACL, cifrado o RPO/RTO empresarial |
| Marca | Presentación NexoCredit | Renombrado de toda la infraestructura |
| Scrum | Backlog/documentos | Ceremonias, participantes u horas acreditados |

La referencia CI es [la ejecución final registrada](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247558296). Las pruebas no contienen secretos productivos ni realizan llamadas Azure de negocio.

## 18. Fuentes y siguiente decisión

- [PRD — NexoCredit](PRD_NEXOCREDIT.md).
- [README y alcance](../../README.md).
- [Tecnologías obligatorias](../../REQUISITOS_TECNOLOGICOS.md).
- [Plan previo](../planificacion/PLAN_PROYECTO.md).
- [QA](../calidad/QA.md).
- [Entrega demo](../entrega/ENTREGA_DEMO.md).
- [Backlog de cierre](../../gestion_proyecto/scrum/BACKLOG_CIERRE.md).
- [Prueba integral del 04/10/2026](../evidencias/2026-10-04/prueba-e2e.md).
- [Cierre técnico](../evidencias/2026-10-04/cierre-tecnico.md).
- [Evidencia de CI](../evidencias/2026-10-04/github-actions.md).

La siguiente decisión es revisar y aprobar el alcance de estos documentos y acordar la validación pendiente. El núcleo técnico no necesita fingir un cierre académico: puede presentarse con sus pruebas y límites, mientras se registran de forma real aceptación y Scrum.

Esta edición únicamente desarrolla documentación separada. No modifica código, datos, base, permisos, secretos, recursos Azure ni publicación.
