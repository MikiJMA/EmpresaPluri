# PRD — NexoCredit

## Documento de requisitos del producto

| Dato de control | Valor |
|---|---|
| Versión | 1.4 |
| Fecha de edición | 13/10/2026 |
| Línea base técnica | 04/10/2026 |
| Seguimiento funcional | 13/10/2026: reglas-demo-v2 y resúmenes en pesos; IA local y Azure conservados |
| Estado | Borrador para revisión y aceptación |
| Producto | NexoCredit: demostración académica local de análisis crediticio |
| Documento complementario | [MVP y matriz MoSCoW](MVP_NEXOCREDIT.md) |
| Documento anterior | [PRD/MVP combinado, conservado](../archivo/PRD_MVP_NEXOCREDIT.md) |
| Aprobación de usuario/asesor | Pendiente de registro; no se presume |

Este documento define necesidades, comportamiento, restricciones y criterios de éxito. No concede autorización para tratar expedientes reales, contratar servicios, publicar la aplicación, modificar políticas crediticias ni acreditar horas o ceremonias que no hayan ocurrido.

“Comprobado” significa que existe evidencia identificable de la línea base, no que se haya repetido la prueba al redactar esta edición. “Propuesto” identifica requisitos o actividades que todavía deben validarse. Los ejemplos son ficticios.

### Adenda 1.4 — Reglas versionadas y presentación monetaria — 13/10/2026

Para las evaluaciones nuevas, `reglas-demo-v2` establece que un score menor representa mayor riesgo demo. El score entero mantiene su escala capturada 0–1000; no procede de una consulta a Buró ni acredita una probabilidad de incumplimiento.

| Variable | Rango | Riesgo que aporta |
|---|---|---|
| Score | 0–499 | Alto |
| Score | 500–679 | Medio |
| Score | 680–1000 | Bajo |
| Margen mensual | ≤$7,000 | Alto |
| Margen mensual | >$7,000 y ≤$15,000 | Medio |
| Margen mensual | >$15,000 | Bajo |

**PRD-RF03 actualizado:** el resultado usa la categoría de mayor riesgo entre score y margen, con orden Bajo < Medio < Alto. Por ejemplo, margen $20,000 y score 200 producen Alto; el mismo margen y score 500 producen Medio; score 700 produce Bajo. Un score 900 con margen $7,000 produce Alto. Estos límites son ilustrativos de NexoCredit, no una escala oficial o política empresarial validada.

**Historial y compatibilidad:** `PRD-RF04–05` preservan los datos, centavos, resultado y `version_modelo` de evaluaciones anteriores. No se recalculan registros v1 ni se cambia un resultado guardado por reenviar la misma clave idempotente y solicitud. Las tablas de reglas v1 de la sección 9.2 permanecen como contrato histórico, no como regla para nuevas capturas. La ayuda visual y la explicación deben respetar la versión del registro.

**PRD-RF07–08 actualizados:** la guía de explicación se selecciona por versión: fuente `guia-demostracion-v1` / versión 1.0 para v1, y `guia-demostracion-v2` / versión 2.0 para v2. La falta de guía compatible no autoriza reutilizar una guía antigua ni inventar referencias. El catálogo local contiene 3 guías / 15 secciones. Azure AI Search conserva su evidencia histórica de 2 guías / 14 secciones hasta una carga y comprobación nuevas; este incremento no realiza nuevas consultas o cargas cloud. Azure OpenAI, Azure ML, Search, Entra y los campos privados de sus keys permanecen en alcance.

**Presentación monetaria:** los resúmenes React muestran pesos completos, redondeados al entero más cercano; `$18,333.33` aparece como `$18,333`. No se truncan importes ni se elimina precisión de captura, cálculos o PostgreSQL. El margen se sigue calculando a dos decimales, y sus límites no se evalúan usando la presentación redondeada. Los detalles de evaluación y pagos conservan centavos; tasas, porcentajes y métricas ML mantienen su precisión pertinente.

**Criterios del incremento:** distinguir los cortes 499/500 y 679/680; comprobar que un margen insuficiente sólo empeora la categoría; mantener intactos resultados v1; diferenciar ausencia de cero; y utilizar la guía correspondiente al resultado. Esta adenda no declara nuevas suites ejecutadas, despliegue, conectividad Azure o aceptación formal. [Reglas, ejemplos y límites de operación](../manuales/REGLAS_RIESGO_DEMO.md).

### Azure implementado y continuidad local — 12/10/2026

Se conserva como alcance implementado de la demo **Azure OpenAI Service, Azure Machine Learning, Azure AI Search y Microsoft Entra ID**, con consultas/identidad comprobadas el 04/10/2026 y [evidencias identificadas](../manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md). No se reclasifican como tecnologías eliminadas o simplemente preparadas. Sus keys se configuran exclusivamente en el `.env` privado del servidor; las plantillas mantienen los nueve campos Azure sin valores sensibles.

El laboratorio scikit-learn local es una alternativa adicional: modelo UCI independiente, 19 entradas NTD, clase académica y métricas propias, sin cambiar las reglas del formulario principal. Esta adenda sustituye la desactivación del ML local del incremento anterior, no su registro histórico. El código Azure y sus requisitos siguen vigentes, aunque la selección operativa actual sea local. [Manual del laboratorio](../manuales/LABORATORIO_IA_LOCAL.md). La integración previa no acredita disponibilidad cloud actual ni validación crediticia.

### Incremento funcional registrado — 11/10/2026

La línea base histórica se conserva con sus fechas. La versión actual añade acceso local además de Microsoft, Ollama y documentos locales por selección explícita, revisión opcional de formato/fecha RFC–CURP con consulta SAT manual, caché PostgreSQL de explicaciones y reserva durable de diez intentos/hora por cuenta. Las llaves permanecen sólo en configuración privada. Una explicación generada ya no vive únicamente en memoria: se reutiliza 24 h, sin eliminación automática al vencer.

Se añadió seguimiento interno ficticio: plan de cuotas ligado a una evaluación, abonos parciales, saldo vencido/atraso/puntualidad, indicadores descriptivos de deuda y pagos, alertas versionadas y eventos transaccionales. La auditoría global nueva exige Administrador; no cambia el rol de cuentas existentes. No importa Buró, verifica depósitos, calcula intereses ni propone aprobar créditos. No altera resultados de scoring o revisiones anteriores.

Estas capacidades actuales sustituyen las limitaciones históricas de acceso exclusivamente Microsoft, explicación sólo en pantalla y ausencia total de alertas. Las alertas se recalculan al crear/pagar o por acción explícita, no mediante vigilancia permanente. El laboratorio UCI continúa separado y el modo ML local deshabilitado; no se inventa una predicción equivalente. [Arquitectura actual y doce tablas](../desarrollo/ARQUITECTURA_Y_DATOS.md), [operación de seguimiento](../manuales/SEGUIMIENTO_CREDITICIO.md) y [evidencia](../evidencias/2026-10-11/seguimiento-crediticio.md).

#### Requisitos incrementales

| ID | Requisito implementado en demo | Criterio verificable |
|---|---|---|
| RF10 | Plan de cuotas y abonos parciales | Importes exactos; fechas y suma del plan; sin sobrepago ni duplicación concurrente |
| RF11 | Análisis descriptivo del seguimiento | Saldo/atraso/cumplimiento/puntualidad reproducibles; ausencia distinta de cero |
| RF12 | Alertas de cuotas vencidas trazables | Pendiente/Atendida/Resuelta y versión; atender no liquida; cambios conservan eventos |
| RF13 | Facultad administrativa adicional | Lectura de auditoría global sólo Administrador, comprobada con 403 para Analista |

La actualización no acredita políticas oficiales, fuentes privadas, representatividad del modelo ni formación/aceptación real. No se involucró al asesor durante esta implementación.

## 1. Resumen ejecutivo

NexoCredit reúne en una aplicación el registro de escenarios financieros ficticios, una clasificación mediante reglas explícitas, su explicación con inteligencia artificial y el seguimiento de una revisión humana. El usuario captura datos en React; FastAPI valida y calcula el resultado; PostgreSQL conserva la evaluación y sus revisiones. Azure AI Search recupera documentación demo y Azure OpenAI redacta una explicación automática después del guardado.

La solución incorpora dos recorridos adicionales, separados del cálculo principal: indicadores económicos públicos de Banxico y Banco Mundial, y un laboratorio de Azure Machine Learning basado en un conjunto académico UCI. Power BI Desktop permite analizar agregados desde una vista PostgreSQL de lectura limitada.

El producto no predice de forma acreditada la probabilidad de incumplimiento de una persona. Las categorías Bajo, Medio y Alto son resultados de reglas de demostración. Los estados Aprobada y Rechazada pertenecen a la revisión demo y no autorizan operaciones financieras.

La entrega se mantiene local, por decisión del usuario. El código puede consultarse en GitHub, pero eso no convierte la aplicación en un servicio disponible públicamente. Tampoco se incluye instalación en la computadora del asesor. Microsoft y los servicios externos requieren Internet; acceso local, seguimiento y documentos locales no requieren Azure. Ollama necesita su servicio/modelo instalado.

La parte técnica ya cuenta con pruebas y evidencia. La aceptación formal del producto, la práctica con el asesor, algunas metas nuevas de validación y la evidencia real del proceso Scrum no se consideran cerradas por redactar este PRD.

## 2. Contexto y problema de producto

### 2.1 Situación que se busca atender

Un ejercicio de evaluación financiera pierde valor si el dato capturado, el cálculo, la explicación y la revisión aparecen desconectados. Se necesita un recorrido en el que el usuario pueda conocer qué ingresó, qué regla se aplicó, qué información fue enviada a servicios externos y quién registró una revisión.

También es necesario evitar tres confusiones frecuentes en una demostración tecnológica:

1. Presentar una regla sencilla como si fuera un modelo predictivo validado.
2. Considerar una explicación generada como una decisión o una garantía de exactitud.
3. Confundir una integración preparada en carpetas con un servicio realmente conectado y probado.

Este problema es una hipótesis de diseño y aprendizaje. No se dispone de una investigación empresarial que cuantifique tiempos perdidos, mora, costes operativos o necesidades de una cartera real.

### 2.2 Propuesta de valor

El valor de NexoCredit consiste en ofrecer una demostración verificable de extremo a extremo: identidad, captura, reglas, persistencia, explicación fundamentada, revisión y analítica. La propuesta no depende de prometer mejores decisiones crediticias, sino de mostrar coherencia, trazabilidad básica y límites comprensibles.

Para el usuario técnico, proporciona una arquitectura organizada por funciones y pruebas reproducibles. Para el asesor, proporciona casos de uso, evidencia fechada y una distinción explícita entre alcance implementado y evolución futura. Para un analista demo, permite entender y revisar un escenario sin tener que interpretar directamente respuestas de APIs.

### 2.3 Hipótesis pendientes de validación

| Hipótesis | Cómo se podría validar | Situación |
|---|---|---|
| Un usuario comprende la diferencia entre riesgo demo y aprobación real | Prueba de comprensión al finalizar un recorrido ficticio | No medida |
| La explicación automática facilita interpretar las reglas | Observación de tareas y rúbrica de explicación, sin asumir causalidad | Propuesta |
| El historial y la revisión reducen confusión sobre cambios de estado | Recuperar un registro y reconstruir sus revisiones con el usuario | Propuesta |
| El dashboard y Power BI muestran cifras consistentes | Comparar agregados para un mismo corte y filtros | Existe evidencia técnica parcial y fechada |

## 3. Visión, objetivos y resultados esperados

### 3.1 Visión del producto

Construir una plataforma académica que permita demostrar un flujo responsable de análisis financiero: datos identificables, cálculo reproducible, IA subordinada al resultado, intervención humana y evidencia de funcionamiento.

### 3.2 Objetivos de esta versión

- Unificar las funciones necesarias para completar un escenario demo sin acudir a herramientas técnicas.
- Conservar evaluaciones y revisiones entre recargas mediante PostgreSQL.
- Mostrar la versión de las reglas y no modificarla por una respuesta de IA.
- Generar una explicación automáticamente, sin exigir un segundo botón.
- Recuperar y citar documentación propia de demostración.
- Incorporar contexto económico público con fuente, unidad y periodo.
- Mostrar Azure ML como experimento independiente con población y limitaciones explícitas.
- Conciliar la analítica web y Power BI cuando se comparan cortes equivalentes.
- Demostrar las trece tecnologías obligatorias con responsabilidades verificables.
- Entregar documentación y evidencia que permitan una revisión académica honesta.

### 3.3 Resultados que no se prometen

No se fijan metas de reducción de mora, incremento de créditos aprobados, rentabilidad, precisión individual, conversión comercial ni ahorro de horas. Tampoco se promete disponibilidad permanente, conformidad normativa, accesibilidad certificada o seguridad productiva sin una evaluación específica.

La mejora de estos resultados requeriría investigación, datos autorizados, una definición de incumplimiento y evaluación con una población pertinente. No puede inferirse de las pruebas de software ni de la métrica de un conjunto académico.

## 4. Usuarios, actores y responsabilidades

| Actor | Trabajo que necesita realizar | Responsabilidad y límite |
|---|---|---|
| Analista demo | Capturar, evaluar, consultar y revisar escenarios ficticios | Interpretar los avisos y no usar el producto para conceder crédito |
| Administrador autorizado | Operar la demo y atender configuración | Cuenta con rol Entra; hoy comparte las mismas rutas funcionales que Analista |
| Desarrollador/alumno | Mantener código, integraciones, pruebas y manuales | Registrar evidencia real y proteger configuraciones privadas |
| Asesor/revisor | Verificar objetivos, recorrido y entregables | Revisar localmente o mediante documentación; no se presume acceso remoto |
| Responsable de producto | Resolver prioridades y aceptar el alcance | Responsabilidad por confirmar; este PRD no asigna una persona |

La aplicación no dispone de una consola administrativa diferenciada ni de una separación exhaustiva entre permisos de lectura, escritura y configuración. Los roles actuales permiten el acceso funcional definido para la demo.

Product Owner y Scrum Master deben acordarse si se utiliza Scrum formalmente. El asesor no recibe esos cargos automáticamente. Una persona mencionada en la conversación no se considera participante confirmado de una ceremonia.

### 4.1 Necesidades de experiencia

El analista necesita conocer si los datos fueron guardados antes de interpretar una explicación. El revisor necesita identificar el estado más reciente y recuperar los anteriores. El asesor necesita reconocer qué parte utiliza reglas, qué parte utiliza IA generativa y qué parte corresponde al laboratorio experimental.

Por ello, la interfaz debe priorizar mensajes de estado y procedencia por encima de una apariencia de “automatización completa”. Las vistas vacías, los datos ausentes y los errores son parte del producto, no excepciones que deban ocultarse.

## 5. Alcance y restricciones

### 5.1 Alcance funcional

La versión incluye autenticación Entra, formulario principal, clasificación demo, guardado, historial y detalle, revisión manual versionada, explicación automática, documentos y búsqueda, indicadores financieros, dashboard React, laboratorio Azure ML y reporte Power BI Desktop.

La operación técnica incluye Docker Compose, migraciones, pruebas locales aisladas, GitHub Actions y respaldo/restauración manual ensayada. La gestión incluye backlog y documentación; los eventos Scrum y la aceptación deben acreditarse cuando ocurran.

### 5.2 Fuera de alcance

- Alojamiento público, acceso remoto e instalación para el asesor.
- Integración con Buró de Crédito o expedientes privados.
- Verificación fiscal o identidad de solicitantes.
- Políticas oficiales de una empresa o institución financiera.
- Aprobación, rechazo o desembolso de crédito real.
- Convertir el formulario MXN al modelo UCI en NTD.
- Entrenamiento continuo, decisiones automáticas o publicación cloud de Power BI.
- Gateway, CD productivo, operación 24/7 y compromiso de recuperación empresarial.

La marca visible es NexoCredit. Algunos nombres técnicos anteriores permanecen en recursos, rutas de archivos o infraestructura para preservar conexiones. No se asume que cambiar textos de la interfaz renombra recursos Azure, repositorios o bases.

### 5.3 Restricciones de operación

El origen probado es http://localhost:8080/. Cambiarlo puede requerir revisar el registro de redirección de Entra y la configuración de la aplicación. Los puertos locales no están autorizados para exposición pública.

Los secretos se mantienen en archivos privados excluidos de Git. Esos archivos no están cifrados actualmente y pueden ser leídos por administradores del equipo. El MVP no incluye un gestor central de secretos.

No se crean nuevos recursos o suscripciones desde este PRD. Las llamadas reales a Azure pueden generar consumo, por lo que una campaña de pruebas cloud requiere acuerdo previo.

## 6. Recorrido de producto

### 6.1 Flujo principal

1. El usuario abre la aplicación local e inicia sesión con Microsoft.
2. El servidor verifica la identidad, el ámbito y el rol.
3. El usuario captura un escenario ficticio y recibe validaciones de campos.
4. El servidor calcula margen y clasificación con reglas versionadas.
5. La evaluación se guarda y el cliente recibe su identificador.
6. Se inicia la explicación automática sobre ese registro guardado.
7. La interfaz muestra resultado, procedencia y estado de explicación.
8. El usuario recupera el detalle y registra una revisión manual.
9. Consulta agregados, contexto económico o reporte Desktop según su tarea.

El éxito de la evaluación y el éxito de la explicación son estados diferentes. Una evaluación puede quedar guardada aunque Azure OpenAI no responda. La interfaz no debe describir ese escenario como pérdida del registro ni como generación exitosa.

### 6.2 Recorridos complementarios

Documentos permite consultar guías demo y buscar fragmentos. Indicadores aporta contexto público sin alterar el scoring. Laboratorio recibe sus propias variables UCI y no crea una evaluación MXN. Power BI importa datos y requiere actualización manual, por lo que puede mostrar un corte anterior al dashboard web.

## 7. Casos de uso detallados

### UC01 — Acceder con Microsoft

**Actor:** Analista o Administrador autorizado. **Precondición:** aplicación local y registro Entra configurados; Internet disponible.

El usuario inicia sesión mediante MSAL. La SPA obtiene un token destinado a la API y lo utiliza en solicitudes de negocio. El servidor comprueba firma, emisor, audiencia, tenant, cliente, vigencia, ámbito y rol.

Sin token válido se devuelve 401; con permisos insuficientes, 403. Una indisponibilidad de la verificación externa no debe convertirse en autorización permisiva. Al vencer la sesión se solicita nuevo acceso.

**Postcondición:** usuario identificado para las operaciones de negocio. La configuración pública del login y OpenAPI no autorizan acceso a evaluaciones.

### UC02 — Capturar, evaluar y guardar

**Actor:** Analista. **Precondición:** sesión válida y PostgreSQL configurado para la aceptación del MVP.

El usuario completa los campos del escenario ficticio. FastAPI valida tipos, rangos y valores finitos, calcula el margen y aplica las reglas en su orden. Se conserva solicitud y resultado con UUID, fecha y versión de reglas.

Los errores de captura se comunican sin guardar un resultado aparentemente válido. Si PostgreSQL falla, se informa que no se confirmó el guardado. El modo de compatibilidad sin base puede devolver un resultado no guardado, pero no satisface este caso para aceptar el MVP.

**Postcondición:** evaluación recuperable, o fallo explícito sin afirmación de éxito.

### UC03 — Reintentar, consultar historial y abrir detalle

**Actor:** Analista. **Precondición:** evaluación existente o solicitud con identificador de idempotencia.

El reenvío de los mismos datos y la misma clave UUID recupera la misma evaluación. Reutilizar esa clave con otro contenido genera conflicto 409. El historial entrega páginas con orden estable; abrir el detalle permite recuperar los datos y revisiones.

Un UUID inexistente produce 404, no un escenario vacío fabricado. La recarga no elimina registros PostgreSQL. La explicación en memoria sí puede perderse al recargar, y no debe confundirse con la persistencia de la evaluación.

**Postcondición:** consulta consistente, sin duplicar por un reenvío idéntico.

### UC04 — Recibir explicación automática

**Actor:** Analista; iniciador técnico: frontend. **Precondición:** guardado confirmado y dependencias configuradas.

El cliente solicita la explicación del UUID. El servidor recupera la evaluación almacenada y la guía DEM-02, y envía al modelo únicamente ingresos, gastos, score, resultado y contexto documental. La respuesta se valida y se presenta con referencia y advertencia.

Si Search no entrega contexto válido, no se inventa una guía. Si la generación falla, permanece el resultado guardado. Una respuesta tardía no debe aparecer como explicación de otro escenario. La IA no puede escribir revisiones ni cambiar clasificación.

**Postcondición:** explicación válida mostrada o error visible, sin modificación del dato de negocio.

### UC05 — Registrar revisión manual

**Actor:** usuario autorizado. **Precondición:** evaluación existente y versión conocida.

El usuario selecciona Pendiente, Aprobada o Rechazada y agrega una observación. El servidor obtiene el responsable de Entra, controla la versión anterior y crea una revisión nueva. Las revisiones previas se conservan.

Si otro proceso ya creó una revisión sobre esa versión, se devuelve 409 y el cliente debe recuperar el estado actualizado. No se sobrescribe silenciosamente. La identidad declarada por el navegador no sustituye la identidad verificada.

**Postcondición:** nueva revisión trazable y riesgo original intacto. Los registros antiguos pueden tener responsables declarados antes de Entra; no se reescribe su historia.

### UC06 — Consultar documentos y buscar

**Actor:** usuario autorizado. **Precondición:** Azure AI Search configurado.

El catálogo entrega las dos guías y sus catorce secciones con fuente y versión. La búsqueda recibe texto controlado, recupera hasta cinco fragmentos y conserva su procedencia.

La consulta no acepta filtros arbitrarios, URLs de destino ni instrucciones Lucene del usuario. Ante error se muestra indisponibilidad, no documentos ficticios. Las guías son contenido académico propio, no políticas oficiales.

**Postcondición:** información documental identificable o fallo honesto.

### UC07 — Analizar el dashboard React

**Actor:** Analista o revisor. **Precondición:** datos PostgreSQL disponibles.

El usuario aplica filtros por riesgo y fechas UTC inclusivas. Los agregados consideran todos los registros coincidentes, no solo la página visible del historial. La deuda promedio considera valores capturados, incluyendo cero, y excluye ausencias.

Sin registros, la interfaz distingue cero conteos de promedios sin denominador. Los filtros de este panel no implican que Power BI o el historial cambien automáticamente.

**Postcondición:** lectura de indicadores con filtros y población comprensibles.

### UC08 — Consultar indicadores económicos

**Actor:** usuario autorizado. **Precondición:** acceso a proveedores; Banxico requiere token privado.

El backend consulta series públicas fijas de Banxico y Banco Mundial. Devuelve valor, unidad, periodo, fuente y estado. Conserva independencia entre proveedores y aplica caché limitada.

Si Banxico no está configurado o falla, Banco Mundial puede seguir mostrándose. Cero y valores negativos no se convierten en ausencia. La fecha de consulta no sustituye el periodo económico observado.

**Postcondición:** contexto público sin datos de solicitantes y sin alterar riesgo.

### UC09 — Ejecutar el laboratorio Azure ML

**Actor:** usuario autorizado. **Precondición:** endpoint académico configurado.

El usuario captura las diecinueve variables UCI admitidas. El servidor valida enteros, orden y límites, llama al endpoint y presenta una clase booleana junto con las advertencias del experimento.

No se envían campos del formulario principal por conversión implícita. Una etiqueta no se transforma en probabilidad. El escenario del laboratorio no se guarda como evaluación ni modifica revisiones.

**Postcondición:** resultado experimental separado o fallo explícito.

### UC10 — Revisar Power BI Desktop

**Actor:** operador y asesor local. **Precondición:** Desktop, lector PostgreSQL y conexión privada disponibles.

El operador actualiza el reporte desde la vista limitada y prueba filtros por riesgo y revisión. Para comparar cifras con SQL o web utiliza el mismo corte y contexto.

La actualización es manual; tener el archivo abierto no demuestra que incluya los últimos registros. La vista no contiene RFC, responsable ni observaciones. No existe publicación cloud acreditada.

**Postcondición:** análisis local con corte identificado y medidas conciliables.

### UC11 — Verificar y recuperar la demo

**Actor:** operador técnico. **Precondición:** herramientas y permisos locales adecuados.

Se ejecutan suites aisladas, migraciones y construcción. El respaldo manual genera artefactos privados y el ensayo de restauración compara esquema, filas y huellas en un destino temporal.

El ensayo no debe sobrescribir la base de trabajo. El volumen Docker no sustituye un respaldo. La restauración probada no acredita recuperación completa de roles globales, ACL ni objetivos empresariales de desastre.

**Postcondición:** evidencia técnica vinculada a una versión y datos de origen preservados.

## 8. Requisitos funcionales

Los identificadores PRD-RF son propios de esta edición; no reemplazan retroactivamente los RF del plan previo. La relación con MoSCoW se detalla en el documento MVP.

| ID | Requisito y resultado exigido | Casos |
|---|---|---|
| PRD-RF01 | Autenticar con Entra y autorizar negocio en servidor | UC01 |
| PRD-RF02 | Validar captura, rangos y ausencia frente a cero | UC02 |
| PRD-RF03 | Calcular reglas demo reproducibles y devolver su versión | UC02 |
| PRD-RF04 | Guardar solicitud/resultado con UUID e idempotencia | UC02–03 |
| PRD-RF05 | Recuperar historial paginado y detalle persistente | UC03 |
| PRD-RF06 | Registrar revisiones con identidad y control de versión | UC05 |
| PRD-RF07 | Explicar automáticamente solo registros confirmados | UC04 |
| PRD-RF08 | Recuperar catálogo y fragmentos con procedencia | UC06 |
| PRD-RF09 | Consultar indicadores públicos con fallos independientes | UC08 |
| PRD-RF10 | Separar laboratorio UCI y clasificación principal | UC09 |
| PRD-RF11 | Calcular dashboard sobre la población filtrada completa | UC07 |
| PRD-RF12 | Exponer una vista limitada para Power BI Desktop | UC10 |
| PRD-RF13 | Operar localmente con migraciones y pruebas aisladas | UC11 |
| PRD-RF14 | Respaldar y probar restauración sin afectar el origen | UC11 |
| PRD-RF15 | Mantener identidad NexoCredit y límites visibles | Todos |

## 9. Datos de entrada y reglas de negocio

### 9.1 Diccionario del formulario principal

| Nombre funcional / API | Tipo y dominio | Interpretación |
|---|---|---|
| RFC / rfc | Texto no vacío | Identificador ficticio; no valida estructura fiscal |
| Ingresos / ingresos_mensuales | Número > 0 y <= 1,000,000,000 | Ingresos mensuales en MXN |
| Gastos / gastos_mensuales | Número >= 0 y <= 1,000,000,000 | Incluye los pagos mensuales de créditos |
| Score / score_buro_actual | Entero estricto 0–1000 | Capturado, no verificado contra Buró |
| Deuda / deuda_actual | Número no negativo, máximo 1,000,000,000 | Saldo informado, no confirmado externamente |
| Pagos / pagos_mensuales_creditos | Número no negativo, mismo máximo | Suma mensual informada de créditos |
| Atraso / dias_atraso_actual | Entero estricto 0–36,500 | Días del pago vencido más antiguo pendiente |

La UI solicita deuda, pagos y atraso. La API mantiene compatibilidad con registros anteriores admitiendo omisión o nulo para esos tres campos. No se normaliza automáticamente la ausencia a cero. Se rechazan números no finitos y propiedades no permitidas.

### 9.2 Algoritmo determinista histórico — reglas-demo-v1

Contrato de la línea base anterior, conservado para interpretar sus registros. Las evaluaciones nuevas usan `reglas-demo-v2`, definida en la adenda 1.4 del 13/10/2026 y en el [manual de reglas](../manuales/REGLAS_RIESGO_DEMO.md); los resultados v1 no se recalculan.

Margen mensual = ingresos menos gastos, redondeado a dos decimales con la implementación actual. Se aplican las condiciones en este orden:

| Orden | Condición | Categoría |
|---|---|---|
| 1 | Margen estrictamente mayor que 15,000 y score mayor o igual a 680 | Bajo |
| 2 | Si no cumple la anterior, margen estrictamente mayor que 7,000 | Medio |
| 3 | Cualquier otro caso | Alto |

Versión: reglas-demo-v1. Un margen de 15,000 no cumple Bajo. Un margen de 7,000 queda en Alto. Con margen de 20,000 y score 679, el resultado es Medio.

Deuda, pagos, atraso e indicadores macroeconómicos se conservan o presentan, pero no alteran esta versión. Restar otra vez los pagos produciría un doble conteo, porque ya están dentro de gastos.

La representación monetaria actual utiliza float y round. Una futura migración a Decimal/NUMERIC puede mejorar semántica contable, pero requiere contratos y regresión; no se describe como implementada.

### 9.3 Revisión y cambios

Una revisión contiene estado, motivo, responsable, fecha y versión. El motivo admite 1–2000 caracteres y el responsable 1–120; el servidor establece la identidad autenticada. La versión anterior permite detectar concurrencia.

Cambiar la revisión no recalcula ni reemplaza el riesgo original. Cambiar reglas requerirá una versión nueva y una decisión explícita sobre evaluaciones históricas; no se reinterpretan automáticamente bajo reglas distintas.

### 9.4 Datos del laboratorio

Azure ML recibe diecinueve enteros UCI en orden definido. Se aplican límites int32 y reglas específicas, como LIMIT_BAL positivo, PAY_AMT no negativo y estados PAY entre -2 y 9.

El conjunto corresponde a Taiwán, 2005, con importes NTD. No tiene equivalencia acreditada con el formulario MXN ni con una cartera mexicana. La salida aceptada es una clase booleana, no una probabilidad calibrada.

## 10. Arquitectura de la solución

### 10.1 Estilo y componentes

Se conserva un monolito modular FastAPI con una SPA React y adaptadores externos. Para el volumen y alcance de la demo no se justifica introducir microservicios, un bus de eventos o una segunda base.

~~~text
Microsoft Entra ID ⇄ React + MSAL
                         │
                  HTTP local / JSON
                         ▼
                 Nginx → FastAPI
                         ├─ PostgreSQL → vista limitada → Power BI Desktop
                         ├─ Azure AI Search → contexto → Azure OpenAI
                         ├─ Azure ML — laboratorio UCI separado
                         └─ Banxico / Banco Mundial — contexto público

Docker Compose: frontend, backend, PostgreSQL y migraciones
GitHub Actions: verificación de código, no despliegue productivo
Scrum: organización y evidencia del trabajo, no componente de ejecución
~~~

### 10.2 Responsabilidad de las tecnologías obligatorias

| Tecnología | Responsabilidad concreta | Evidencia o límite |
|---|---|---|
| Python | Reglas, validación, adaptadores y herramientas técnicas | Código ejecutable, no solo carpeta |
| FastAPI | API REST y controles de acceso | Contratos y rutas de negocio |
| React.js | Interfaz, estados, navegación y dashboard | Pruebas frontend y construcción |
| Azure OpenAI Service | Explicación automática del resultado guardado | Consulta real observada; revisión humana |
| Azure Machine Learning | Experimento académico y endpoint UCI | Metadatos de despliegue; no validación poblacional |
| Azure AI Search | Catálogo y recuperación de guías | Dos guías, catorce secciones |
| PostgreSQL | Persistencia, revisiones y vista analítica | Migraciones y restauración probada |
| Power BI | Analítica Desktop | Medidas y filtros contrastados |
| Docker | Ejecución local y aislamiento de pruebas | Compose y volumen persistente |
| GitHub Actions | Verificación continua | CI identificada por commit |
| Microsoft Entra ID | Identidad y autorización delegada | Verificación JWT y roles |
| APIs financieras | Contexto económico público | Banxico y Banco Mundial |
| Scrum | Priorización, inspección y adaptación | Backlog disponible; eventos por acreditar |

### 10.3 Límites de confianza y comunicaciones

El navegador no es una fuente confiable para recalcular resultados ni identificar responsables. FastAPI decide permisos, valida entradas y obtiene los registros que se explican. El token se transmite como Bearer y se valida con firma RS256 y claves públicas de Entra.

Se adopta Authorization Code con PKCE y OIDC delegado a MSAL como decisión arquitectónica, conforme a la [documentación de Microsoft](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow). No se incorpora un protocolo de login manual ni se entrega un client secret al navegador.

React y API usan REST/JSON en el mismo origen mediante Nginx. Las conexiones a proveedores externos usan HTTPS y validación TLS. PostgreSQL utiliza TCP interno Docker; Power BI utiliza loopback 55433 con lector limitado. HTTP y TCP locales sin TLS no constituyen un diseño autorizado para redes públicas.

UUID identifica evaluaciones y operaciones idempotentes. TIMESTAMPTZ conserva instantes UTC; las fechas del plan son DATE con corte diario UTC. No se introduce sincronización offline, WebSockets o cola de mensajes. La caché/cuota PostgreSQL comparte estado de explicación entre procesos.

### 10.4 Contratos API principales

Todos los siguientes contratos están bajo /api/v1. La tabla resume responsabilidades; OpenAPI y código son la referencia de nombres completos y esquemas.

| Método / recurso | Responsabilidad |
|---|---|
| POST /evaluar | Validar, clasificar y guardar; recibe Idempotency-Key |
| GET /evaluaciones | Historial; página por defecto 20, máximo 100 y offset |
| GET /evaluaciones/{id} | Detalle de evaluación y revisiones |
| POST /evaluaciones/{id}/revisiones | Crear revisión con versión e identidad |
| POST /evaluaciones/{id}/explicacion | Explicar desde datos persistidos |
| GET /dashboard | Agregados de la población coincidente |
| GET /azure-search/documentos | Catálogo documental validado |
| POST /azure-search/buscar | Búsqueda textual controlada |
| POST /azure-ml/predecir | Predicción académica separada |
| GET /datos-financieros/indicadores | Contexto público normalizado |

GET / comprueba disponibilidad básica de la API, no toda la salud de sus dependencias. Los endpoints “estado” de integraciones describen configuración; no acreditan conectividad por sí solos. /auth/config es público para iniciar sesión; /auth/me requiere identidad.

401 representa falta de identidad válida; 403, permisos insuficientes; 404, recurso inexistente; 409, conflicto; 422, entrada inválida. Las integraciones pueden informar 503 por indisponibilidad/configuración, 502 por fallo o contrato remoto y 504 por timeout, sin revelar mensajes privados del proveedor.

### 10.5 Persistencia y consistencia

| Objeto | Información | Regla de integridad |
|---|---|---|
| evaluaciones | UUID, fecha, solicitud JSONB, resultado JSONB | Objetos JSON válidos e índice de orden fecha/id |
| revisiones | UUID, evaluación, versión, estado, motivo, responsable, fecha | FK y versión única por evaluación |
| schema_migrations | Versión SQL y fecha de aplicación | Migraciones registradas y repetibles |
| reportes.evaluaciones_powerbi | Vista de lectura para analítica | Sin RFC, responsable ni observaciones |

La revisión utiliza bloqueo de fila y restricciones para impedir sobrescrituras concurrentes. Las migraciones emplean control de versión y bloqueo de ejecución. La explicación se conserva en caché privada separada, no como una nueva evaluación. La petición UCI y la caché financiera no se guardan como evaluaciones. Las tablas históricas de esta sección se amplían según el diccionario vigente de doce tablas enlazado arriba.

La información JSONB permite conservar la solicitud y la versión del resultado. No convierte la base en un repositorio de documentos oficiales ni garantiza compatibilidad ilimitada ante cambios de contrato.

## 11. Integraciones y tratamiento de fallos

### 11.1 Azure OpenAI y fundamentación

La explicación usa el despliegue técnico gpt-5-mini-1 y la guía DEM-02 versión 1.0. El servidor no acepta del cliente una clasificación arbitraria para justificarla; recupera el registro persistido.

Solo se envían ingresos, gastos, score, resultado y guía. RFC, identidad Entra, UUID y observaciones no forman parte de ese contenido. La llamada utiliza store=false; esto no garantiza retención cero por el proveedor.

El límite actual es 2000 tokens de salida, incluyendo razonamiento, con timeout de 60 segundos y dos generaciones simultáneas por proceso. No existe cuota global por usuario. La validación de JSON y referencias no elimina la posibilidad de error semántico.

La deduplicación frontend es por UUID en memoria de pantalla. Evita solicitudes repetidas del mismo recorrido, pero se pierde con recarga o cierre de sesión. No se presume persistencia ni deduplicación global entre dispositivos.

### 11.2 Azure AI Search

Search ofrece catálogo y búsqueda sobre contenido académico propio. El catálogo valida completitud hasta el límite técnico de cincuenta secciones. La búsqueda admite texto de 2–200 caracteres y devuelve hasta cinco fragmentos.

Se utiliza clave privada de consulta, timeout de ocho segundos y errores sanitizados. Las rutas públicas del producto no escriben en el índice. La adaptación de la marca en las guías propias se realiza en presentación; no se presume una migración de documentos Azure.

### 11.3 Azure ML

La comprobación de metadatos del 04/10/2026 mostró endpoint/despliegue correcto y tráfico 100 % dirigido al modelo registrado candidato versión 1. No se comparó todavía la huella binaria remota con el artefacto local.

El experimento local evaluó 5,955 registros y obtuvo AUC 0.775274 y sensibilidad 32.01 %. Es evidencia de ese experimento, no de desempeño para clientes mexicanos. El trabajo AutoML original falló al final en etiquetado tras guardar artefactos; la recuperación del candidato no se presenta como un entrenamiento íntegramente exitoso nuevo.

El adaptador tiene timeout de treinta segundos, no reintenta automáticamente y no persiste escenarios. Los binarios de modelo no se cargan en el backend para el flujo principal.

### 11.4 APIs financieras

Banxico utiliza SF43718 para FIX MXN/USD y SF61745 para tasa objetivo anual. Banco Mundial utiliza las series FP.CPI.TOTL.ZG de inflación y NY.GDP.MKTP.KD.ZG de crecimiento del PIB para MEX.

Las consultas tienen destinos y series fijas, sin enviar datos del solicitante. Se comprueba TLS, se rechazan redirecciones y se limita el contenido JSON. Los valores finitos negativos y cero conservan su significado.

La caché es por proveedor y proceso: una hora para datos válidos y un minuto para errores. No es distribuida ni un monitor en segundo plano. Los estados disponible, parcial, no configurado y error evitan reemplazar un fallo por una cifra inventada.

### 11.5 Degradación controlada

| Dependencia que falla | Comportamiento requerido |
|---|---|
| Entra/verificación | Rechazar acceso, no habilitar modo anónimo de negocio |
| PostgreSQL | No confirmar guardado ni revisión |
| Search | Informar fallo documental y no inventar contexto |
| OpenAI | Mantener evaluación y mostrar fallo de explicación |
| Azure ML | Mostrar fallo solo del laboratorio |
| Un proveedor financiero | Mantener resultados válidos del otro |
| Power BI sin actualizar | Identificar corte; no afirmar sincronización |

## 12. Requisitos de experiencia e interfaz

La navegación debe permitir reconocer evaluación, seguimiento, documentos, indicadores y laboratorio como tareas diferentes. El resultado principal debe mostrar clasificación demo, margen, versión y advertencia; la explicación debe indicar fuente y posibilidad de error.

Los estados deben distinguir: validando, enviando, guardado, generando, generado, fallido y sin datos. Un cambio de campos o de UUID debe impedir que una explicación vieja se muestre como resultado nuevo.

Los errores de formulario deben explicar qué corregir sin borrar la captura válida. Los conflictos de revisión requieren refrescar el detalle; los fallos externos no deben inducir a pulsar repetidamente ni asegurar consumo gratuito.

Como mejora Should se propone verificar teclado, foco, etiquetas y comprensión con tareas. No se afirma conformidad WCAG ni una prueba de usabilidad ya realizada.

## 13. Requisitos no funcionales

| ID | Dimensión | Exigencia para esta demo |
|---|---|---|
| PRD-NF01 | Seguridad | Autorización en servidor; secretos fuera del frontend y la entrega |
| PRD-NF02 | Integridad | Reglas versionadas, idempotencia y revisiones sin sobrescritura |
| PRD-NF03 | Privacidad | Datos ficticios y minimización por proveedor |
| PRD-NF04 | Resiliencia | Fallos externos aislados; mensajes veraces |
| PRD-NF05 | Mantenibilidad | Organización por funciones, contratos y pruebas |
| PRD-NF06 | Recuperabilidad | Respaldo manual y ensayo aislado conciliado |
| PRD-NF07 | Reproducibilidad | Entorno y commit identificados; migraciones repetibles |
| PRD-NF08 | Observabilidad | Estado y evidencia fechada sin exponer secretos |
| PRD-NF09 | Rendimiento | Medición local propuesta, sin SLA productivo |
| PRD-NF10 | Comprensibilidad | Diferenciar regla, explicación, revisión y experimento |

Para rendimiento se propone p95 <= 2 segundos en evaluar/guardar y dashboard, excluyendo proveedores: cien operaciones ficticias, un usuario, servicios calientes y equipo documentado. Es una meta nueva, no un benchmark completado.

El respaldo actual no cifra ni recupera roles globales/ACL. No existe política automática de retención, RPO/RTO acordado o procedimiento productivo integral. Las imágenes base y dependencias Python no están todas fijadas por digest/versión exacta.

## 14. Privacidad, seguridad y gobierno de datos

La aceptación debe utilizar escenarios ficticios. El RFC se transmite al backend y se conserva en PostgreSQL; no debe afirmarse que nunca sale del navegador. No se envía a OpenAI, a las consultas públicas financieras ni a la vista Power BI.

Los archivos .env, dumps, cachés Desktop y configuraciones privadas no deben compartirse con el asesor ni publicarse. Retirar archivos del seguimiento Git no elimina copias de commits anteriores. Si se detecta una credencial expuesta, debe tratarse como incidente y evaluarse su revocación, no ocultarse mediante un cambio de texto.

Este PRD no establece una base jurídica, consentimiento ni política de retención para expedientes reales. La duración de los datos ficticios y de los respaldos debe acordarse localmente. Tampoco existe una auditoría íntegra de todas las lecturas o una separación de funciones productiva.

Antes de utilizar clientes reales serían obligatorios controles adicionales: autorización de datos, retención/cifrado, acceso por función, auditoría, validación crediticia, evaluación de sesgos, operación y revisión de riesgos. No son capacidades implícitas del MVP.

## 15. Métricas de éxito y método de medición

Cada cifra debe conservar fecha, versión de software, población y método. Un porcentaje obtenido en fixtures no representa adopción ni desempeño financiero.

| Métrica | Definición / meta | Línea base y límite |
|---|---|---|
| Consistencia de reglas | Casos correctos / casos definidos; meta 100 % | Suites aprobadas; mantener umbrales |
| Idempotencia | Evaluaciones duplicadas en reenvíos idénticos; meta 0 | Cubierta por pruebas; no equivale a desastre sin pérdida |
| Integridad de revisión | Casos con identidad/versión/riesgo intactos; meta 100 % | Pruebas y flujo local |
| Rechazo de acceso indebido | Casos negativos rechazados / definidos; meta 100 % | No constituye pentest |
| Fundamentación de explicación | Seis casos con referencia correcta y sin contradicción; meta 6/6 | Protocolo nuevo pendiente |
| Completitud documental | Dos guías y catorce secciones con procedencia | Catálogo observado |
| Veracidad de indicadores | Valores con fuente/unidad/periodo y fallos explícitos | Ambos proveedores disponibles el 04/10/2026 |
| Conciliación Power BI | Diferencias SQL–DAX; meta 0 | 96 comparaciones en 16 contextos y 6 medidas el 30/09/2026 |
| Calidad automatizada | Suites, migraciones, lint/build y audit aprobados | 69 backend y 48 frontend; CI fechada |
| Recuperación ensayada | Diferencias de esquema/filas/huellas; meta 0 | Tres tablas conciliadas en destino aislado |
| Comprensión de límites | Participantes que distinguen demo/crédito; meta a confirmar | Sin participantes ni medición aún |
| Tiempo local | p95 <= 2 segundos con protocolo declarado | Should; aún no medido |

Los ejemplos de cinco evaluaciones en Power BI y siete en la prueba web pertenecen a cortes distintos. No son un contador permanente del producto ni deben utilizarse para afirmar que los dos paneles discrepan sin alinear fechas.

La CI final identificada es [run 37247558296](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247558296), commit 914ac8aa7abfeefae746dda4bd9c59ec9191719d: 69 pruebas backend y 48 frontend aprobadas sin omisiones, además de las verificaciones registradas. No consultó servicios Azure productivos. npm audit reportó cero en esa ejecución; el resultado no es garantía futura.

## 16. Supuestos, decisiones y asuntos por resolver

| ID | Decisión o supuesto | Justificación y efecto |
|---|---|---|
| A01 | Windows, Docker Desktop y navegador compatible | Mantener el entorno existente |
| A02 | Un usuario interactivo para la aceptación inicial | Limitar el protocolo, no acreditar concurrencia productiva |
| A03 | REST/JSON, UUID, UTC y PostgreSQL 17 | Conservar contratos y almacenamiento actuales |
| A04 | Monolito modular, sin colas | Complejidad proporcional a la demo |
| A05 | MSAL para el protocolo de identidad | Evitar implementación manual de autenticación |
| A06 | Dinero con representación actual durante MVP | No introducir migración contable sin regresión |
| A07 | Internet y servicios existentes durante revisión | Dependencia, no disponibilidad garantizada |
| A08 | Sprints de dos semanas como propuesta | Calendario/capacidad por acordar |
| A09 | Sin nueva exposición pública | Respeta la decisión del usuario |

No se sustituyen por supuestos técnicos los detalles sustantivos ausentes: presupuesto, licencias, políticas oficiales, definición de incumplimiento, horizonte del modelo, autorización de históricos, participantes Scrum o aprobación del asesor.

La persistencia de explicación ya está implementada para la demo con finalidad/retención/límites documentados; antes de datos reales deben definirse políticas adecuadas de acceso, eliminación y coste. Ampliar usuarios o desplegar públicamente continúa fuera de la autorización local. Los resultados históricos de CI/modelo/Power BI conservan su fecha y no prueban una nueva ejecución.

## 17. Riesgos y mitigaciones

| Riesgo | Impacto | Tratamiento y condición de revisión |
|---|---|---|
| Confusión demo/aprobación real | Uso inadecuado | Avisos y prueba de comprensión |
| Error de explicación IA | Interpretación incorrecta | Guía, contrato y revisión humana |
| Desajuste UCI/población objetivo | Conclusión predictiva inválida | Laboratorio separado; no convertir MXN |
| Cuota o fallo cloud | Recorrido parcial y posible coste | Estados separados y pruebas acordadas |
| Exposición de configuración | Acceso no autorizado | Entrega depurada y control local |
| Pérdida de base/backup incompleto | Pérdida de trabajo | Respaldo y ensayo; ampliar antes de producción |
| Corte distinto en Power BI | Comparación engañosa | Actualizar y anotar filtros/corte |
| Acreditación ficticia de Scrum | Evidencia académica inválida | Registrar solo eventos ocurridos |
| Dependencias cambiantes | Reproducibilidad limitada | CI y revisión de versiones |
| Exposición accidental de puertos | Superficie de ataque | Mantener loopback; no publicar |

No se asignan probabilidades cuantitativas sin datos. El operador debe revisar estos riesgos cuando cambien población, conectividad, volumen, datos o propósito.

## 18. Validación, entrega y control de cambios

El [MVP separado](MVP_NEXOCREDIT.md) establece MoSCoW, historias, pruebas y puertas de aceptación. Todos los Must deben contar con evidencia; Should/Could se registran sin convertirlos en hechos implementados.

La entrega técnica se vincula a un commit y un corte de datos. Los manuales deben concordar con el código. Los ensayos cloud se autorizan de forma explícita cuando impliquen consumo. La revisión con el asesor se registra después de ocurrir, con observaciones y decisión.

Se propone gestionar el trabajo mediante backlog, objetivos y eventos reales de Scrum, conforme a la [Guía Scrum](https://scrumguides.org/scrum-guide.html). La planificación propuesta no prueba que se hayan ejecutado reuniones ni las 500 horas de un plan anterior.

Los cambios de reglas, contratos, permisos, datos o servicios requieren análisis de impacto, nueva evidencia y actualización documental. Una petición de publicar o usar datos reales requiere reconsiderar los no objetivos, no solo activar una variable de entorno.

### 18.1 Evolución posterior, no autorizada por este documento

Primero puede mejorarse usabilidad, medición local y reproducibilidad. Después, si se acuerda, puede evaluarse persistencia de explicaciones y retención. Una versión crediticia real exigiría datos y políticas autorizadas, validación temporal y poblacional, calibración, controles por segmentos, supervisión humana y operación segura.

Comparar la huella del modelo remoto con el artefacto local es una mejora de trazabilidad técnica. Aunque se complete, no resuelve validez del modelo para la población mexicana ni habilita decisiones reales.

### 18.2 Situación de aceptación

El núcleo técnico de la demo está comprobado en la línea base. La aprobación de este PRD, la capacitación/práctica, la revisión del asesor y la evidencia real de Scrum siguen pendientes. Este documento no declara cerrado el MVP formal.

## 19. Fuentes y evidencia

- [README del proyecto](../../README.md).
- [Requisitos tecnológicos y estado](../../REQUISITOS_TECNOLOGICOS.md).
- [Plan previo](../planificacion/PLAN_PROYECTO.md).
- [QA y registros históricos](../calidad/QA.md).
- [Entrega y límites de la demo](../entrega/ENTREGA_DEMO.md).
- [Backlog de cierre](../../gestion_proyecto/scrum/BACKLOG_CIERRE.md).
- [Prueba integral ficticia](../evidencias/2026-10-04/prueba-e2e.md).
- [Cierre técnico local](../evidencias/2026-10-04/cierre-tecnico.md).
- [Evidencia CI del cierre](../evidencias/2026-10-04/github-actions.md).
- [CI del commit final](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247558296).
- [Validación del formulario](../../backend/app/validacion_datos/credito.py).
- [Reglas de clasificación](../../backend/app/evaluacion_crediticia/scoring.py).
- [Persistencia PostgreSQL](../../backend/app/persistencia_postgresql/README.md).
- [Autenticación Entra](../../backend/app/autenticacion_entra_id/README.md).
- [Integraciones backend](../../backend/app/integraciones/README.md).

Esta edición amplía y organiza documentación. No ejecuta pruebas nuevas, no modifica código, datos, secretos, permisos, recursos cloud ni despliegues.
