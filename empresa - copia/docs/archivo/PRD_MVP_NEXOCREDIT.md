# PRD y definición del MVP — NexoCredit

Versión: 1.0 · Corte de la línea base: 04/10/2026 · Estado: borrador para revisión.
Producto: demostración académica local de análisis de riesgo crediticio y revisión humana.
Este PRD documenta el producto; no aprueba políticas de crédito, presupuestos, horas de estadía ni aceptación del asesor.

## 1. Resumen ejecutivo

NexoCredit permite a un usuario autorizado capturar un escenario ficticio, obtener una clasificación explicada mediante reglas demo, conservarlo en PostgreSQL, consultarlo y registrar una revisión humana. Integra explicación automática con Azure OpenAI y documentación recuperada con Azure AI Search; incorpora indicadores económicos públicos, un laboratorio académico Azure ML separado y análisis en React y Power BI Desktop.

El MVP es una **demostración local autenticada y verificable**, no un sistema para conceder créditos reales. La aplicación permanece en la computadora del usuario; requiere Internet para Entra, Azure y proveedores externos. No es una aplicación completamente offline.

Por decisión expresa del usuario, esta entrega no incluye alojamiento público, acceso remoto ni instalación en la computadora del asesor. Publicar código en GitHub no equivale a desplegar la aplicación. La marca visible es NexoCredit; los identificadores técnicos existentes se conservan para no romper las conexiones.

## 2. Problema, propuesta de valor y objetivos

Problema objetivo: la captura, interpretación y seguimiento de escenarios financieros necesitan un flujo consistente que distinga datos ausentes, reglas aplicadas, explicaciones de IA y decisiones humanas. Es una hipótesis de producto, no un diagnóstico medido de procesos empresariales.

Propuesta de valor: reunir captura, trazabilidad básica, explicación y consulta en una interfaz, haciendo visibles las fuentes y limitaciones.

Objetivos del MVP:

1. Demostrar el flujo autenticado de captura, evaluación, guardado, consulta y revisión.
2. Mostrar resultados reproducibles de las reglas demo sin presentarlos como probabilidad de incumplimiento.
3. Generar automáticamente una explicación fundamentada en una guía recuperada, sin enviar RFC al modelo ni alterar el resultado.
4. Separar claramente el laboratorio UCI, los indicadores económicos y el scoring principal.
5. Demostrar el uso funcional de las 13 tecnologías obligatorias y registrar honestamente los pendientes.
6. Entregar código, contratos, manuales y evidencia verificable para revisión académica.

Hipótesis por validar con usuarios: un analista puede completar el flujo y explicar su resultado sin confundirlo con una aprobación real. No hay todavía mediciones de adopción, ahorro de tiempo, retorno económico o reducción del incumplimiento.

## 3. Usuarios y responsabilidades

| Actor | Necesidad | Acceso y límite |
|---|---|---|
| Analista autorizado | Capturar escenarios, consultar evaluaciones, entender factores y registrar revisión | Rol Analista en Entra; solo datos ficticios |
| Administrador autorizado | Operar la demo y atender configuración/incidentes | Rol Administrador; actualmente comparte las mismas rutas funcionales que Analista. No existe una consola administrativa diferenciada |
| Alumno/desarrollador | Mantener código, pruebas, integraciones y documentación | Operación técnica; no sustituye al asesor ni valida políticas de crédito |
| Asesor/revisor | Evaluar alcance, evidencia y resultados | Revisión local acompañada o documental; no se presume una cuenta Entra ni acceso remoto autorizado |

Product Owner y Scrum Master son responsabilidades por acordar. No se asignan automáticamente al asesor ni se inventan participantes, ceremonias o firmas.

## 4. Definición del MVP y límites

Flujo mínimo de valor:

**Iniciar sesión → capturar datos ficticios → evaluar y guardar → recibir explicación automática → consultar detalle → registrar revisión → consultar indicadores y reportes.**

El laboratorio Azure ML es un recorrido académico independiente, no un paso obligatorio de cada evaluación MXN.

El MVP incluye todas las funciones Must de la matriz MoSCoW. Las Should y Could pueden mejorar el producto, pero no bloquean esta demostración si su exclusión queda registrada. Algunas ya pueden existir parcialmente; prioridad de producto no equivale a estado de implementación.

Las 13 tecnologías siguen siendo obligatorias. En particular, Azure ML es Must como laboratorio académico integrado, no como modelo acreditado para la población objetivo. Scrum es Must como proceso con evidencia real; disponer de un backlog no acredita su ejecución.

No objetivos de esta versión:

- Autorizar, rechazar o desembolsar créditos reales.
- Verificar identidad fiscal, consultar Buró de Crédito o afirmar que el score capturado está validado.
- Usar datos personales reales, políticas empresariales oficiales o expedientes privados.
- Convertir automáticamente el formulario MXN a las 19 variables UCI en NTD.
- Prometer precisión predictiva, disponibilidad continua, cumplimiento normativo o escalabilidad no medidos.
- Ofrecer aplicación web pública, gateway Power BI, despliegue automático o acceso remoto al asesor.

## 5. Casos de uso y criterios de aceptación

| ID | Caso de uso | Resultado y manejo de fallos |
|---|---|---|
| UC01 | Acceder con Microsoft | FastAPI verifica token y permisos; sin token devuelve 401, sin permiso/rol 403. La sesión vencida solicita nuevo acceso |
| UC02 | Evaluar un escenario ficticio | Valida campos, calcula margen y riesgo demo, guarda una evaluación. Si la base falla, no muestra un guardado exitoso |
| UC03 | Reenviar y consultar | La misma clave y los mismos datos recuperan la misma evaluación; una clave reutilizada con datos diferentes produce 409. Historial y detalle sobreviven a la recarga |
| UC04 | Recibir explicación automática | Se solicita después del guardado confirmado, sin botón adicional. Usa la evaluación del servidor y guía DEM-02; un fallo de IA no altera ni elimina el registro |
| UC05 | Revisar manualmente | Guarda estado, observación, responsable obtenido de Entra, fecha y versión. Rechaza versiones desactualizadas; conserva revisiones previas y riesgo original |
| UC06 | Leer y buscar documentos | Presenta las 2 guías / 14 secciones demo, con fuente y versión; búsqueda textual controlada. Ante fallo de Search, informa indisponibilidad, sin inventar documentos |
| UC07 | Consultar dashboard | Totales y promedios sobre todos los registros coincidentes; filtros React por fechas UTC inclusivas y riesgo. Ausencia de deuda no se convierte en cero |
| UC08 | Consultar contexto económico | Muestra FIX/tasa Banxico e inflación/PIB Banco Mundial con periodo, unidad, fuente y caché. Un proveedor fallido no invalida al otro |
| UC09 | Probar laboratorio ML | Exige exactamente 19 enteros UCI válidos y muestra una clase booleana con advertencia académica. No guarda ese escenario ni modifica el scoring principal |
| UC10 | Analizar con Power BI | Actualiza desde una vista PostgreSQL de lectura limitada; 11 visuales y filtros por riesgo/revisión. No incluye RFC, responsable ni observaciones en la vista |
| UC11 | Verificar y recuperar la demo | CI y suites aisladas aprobadas; respaldo manual privado y restauración conciliada en destino temporal, nunca sobre la base original |

La ausencia de configuración PostgreSQL puede devolver una evaluación marcada expresamente como no guardada, por compatibilidad del prototipo. **La aceptación del MVP exige PostgreSQL configurado y persistencia comprobada**; ese modo degradado no acredita UC02/UC03 completos.

## 6. Datos y reglas de negocio

### Captura principal

| Campo | Regla del MVP |
|---|---|
| RFC/identificador ficticio | Texto no vacío; no verifica estructura fiscal ni identidad |
| Ingresos mensuales | MXN, mayor que cero, máximo técnico 1,000,000,000 |
| Gastos mensuales | MXN, no negativos, máximo técnico 1,000,000,000; incluyen pagos de créditos |
| Deuda actual total | MXN, no negativa, máximo técnico 1,000,000,000 |
| Pagos mensuales de créditos | MXN, no negativos, máximo técnico 1,000,000,000 |
| Días de atraso actuales | Entero entre 0 y 36,500; atraso del pago vencido más antiguo pendiente |
| Score capturado | Entero entre 0 y 1000; fuente no verificada |

Deuda, pagos y atraso son obligatorios en la interfaz actual, pero la API admite omisión/nulo para compatibilidad con registros anteriores. Cero es un dato, no un sustituto de ausencia. Se rechazan campos adicionales y valores numéricos no finitos.

### Clasificación demo

Margen mensual = ingresos − gastos, redondeado a dos decimales. Aplicación en este orden:

| Prioridad | Condición | Resultado |
|---|---|---|
| 1 | Margen > 15,000 y score >= 680 | Bajo |
| 2 | No cumple la anterior y margen > 7,000 | Medio |
| 3 | Cualquier otro caso | Alto |

Versión de reglas: `reglas-demo-v1`. Un margen exactamente 15,000 no cumple Bajo; uno exactamente 7,000 queda en Alto. Deuda, pagos, atraso e indicadores económicos no cambian actualmente esta clasificación. No volver a restar los pagos ya incluidos en gastos.

Los estados Pendiente, Aprobada y Rechazada corresponden exclusivamente a **revisión demo**, no a autorización real. La IA no puede cambiar score, clasificación, revisión ni registros de negocio.

## 7. Matriz MoSCoW

La matriz prioriza esta entrega local, no elimina requisitos del sistema final.

| Prioridad / ID | Requisito | Alcance y estado de la línea base |
|---|---|---|
| Must / M01 | Autenticación y autorización Entra | MSAL, token, ámbito y rol validados en servidor; implementado en demo |
| Must / M02 | Captura validada y reglas explicables | Campos, límites, margen, clasificación y versión; implementado |
| Must / M03 | PostgreSQL, historial y detalle | Guardado transaccional, UUID/idempotencia y ausencia distinta de cero; implementado localmente |
| Must / M04 | Revisión humana trazable | Estado, motivo, identidad, fecha, versiones y control de conflictos; implementado en demo, no auditoría completa |
| Must / M05 | Explicación automática Azure OpenAI + Search | Tras guardar, cita DEM-02, no envía RFC, no altera decisiones; implementado y consulta real comprobada |
| Must / M06 | Catálogo y búsqueda Azure AI Search | 2 guías / 14 secciones, lectura y búsqueda; implementado, contenidos académicos |
| Must / M07 | Laboratorio Azure ML separado | 19 variables UCI, clase booleana, versión registrada y advertencias; conectado, sin validación crediticia |
| Must / M08 | APIs financieras públicas | Banxico y Banco Mundial con fuente/periodo y fallos independientes; implementado |
| Must / M09 | Dashboard React y reporte Power BI | Métricas conciliadas, filtros, cobertura y lectura restringida; comprobados localmente |
| Must / M10 | Docker y CI GitHub Actions | Arranque/migraciones, suites, npm audit, lint y build sin secretos productivos; comprobados |
| Must / M11 | Respaldo y restauración aislada | Ensayo manual conciliado y archivos privados; comprobado, sin recuperación productiva completa |
| Must / M12 | Identidad NexoCredit y mensajes claros | Marca demostrativa consistente; diferencia reglas, IA y revisión; implementado |
| Must / M13 | PRD, manuales, evidencia y Scrum real | Documentación/backlog disponibles; aceptación, capacitación y ceremonias aún pendientes |
| Should / S01 | Accesibilidad y prueba de tareas | Recorrido por teclado, etiquetas, foco/errores y evaluación de comprensión; no se acredita conformidad completa |
| Should / S02 | Rendimiento local medido | Benchmark reproducible sin servicios externos de pago; objetivo propuesto en métricas |
| Should / S03 | Mayor reproducibilidad | Fijar dependencias Python e imágenes base por versión/digest; pendiente de cierre completo |
| Should / S04 | Comparación binaria del modelo | Conciliar artefacto remoto con huella local y entradas ficticias; pendiente, no basta la etiqueta configurada |
| Should / S05 | Manual y práctica con asesor | Práctica real con datos ficticios y registro de observaciones; pendiente |
| Could / C01 | Exportación de agregados demo | CSV sin identificadores ni observaciones; mejora propuesta, no implementada por este PRD |
| Could / C02 | Evidencia de IA reproducible | Guardado optativo de explicación, guía y versión, previa decisión de retención/privacidad; hoy solo memoria de pantalla |
| Could / C03 | Mejoras visuales de analítica | Gráficos complementarios y comparaciones temporales; no necesarios para validar el flujo mínimo |
| Won't this release / W01 | Alojamiento y acceso remoto | Excluidos expresamente por el usuario |
| Won't this release / W02 | Crédito real e historial privado | Sin autorización de datos, políticas ni modelo validado; fuera del MVP |
| Won't this release / W03 | Automatización de decisiones | Sin aprobación/rechazo/desembolso automático ni conversión MXN→UCI |
| Won't this release / W04 | Operación productiva/cloud Power BI | Sin SLA, gateway, despliegue continuo ni promesa de disponibilidad permanente |

Permisos administrativos diferenciados, auditoría integral, cuotas por usuario, cifrado/retención y monitoreo no son requisitos cerrados por esta demo. Serían **Must de una futura versión productiva**, no mejoras opcionales para operar con clientes reales.

## 8. Arquitectura técnica

Se mantiene un **monolito modular FastAPI**, organizado por funciones, con una SPA React y adaptadores externos. No se requieren microservicios, colas ni otra base de datos para este MVP.

```text
                        Microsoft Entra ID
                               ↕
                    React + MSAL (navegador)
                               ↓ HTTP local / JSON
                  Nginx → FastAPI (Python)
                               ├─ PostgreSQL → vista limitada → Power BI Desktop
                               ├─ Azure AI Search → contexto para Azure OpenAI
                               ├─ Azure ML (laboratorio UCI independiente)
                               └─ Banxico / Banco Mundial (contexto público)

Docker Compose: frontend, backend, PostgreSQL y migraciones
GitHub Actions: validación de código; no despliega la aplicación
```

| Tecnología obligatoria | Responsabilidad |
|---|---|
| Python | Reglas, validación, adaptadores, operación y evaluación académica |
| FastAPI | API REST, contratos OpenAPI, dependencias de acceso y errores |
| React.js | Captura, navegación, estados, detalle, revisión y visualización |
| Azure OpenAI Service | Redacción de explicación a partir de resultado guardado y guía citada |
| Azure Machine Learning | Entrenamiento/evaluación académica y endpoint del laboratorio |
| Azure AI Search | Catálogo, búsqueda y recuperación de fragmentos demo |
| PostgreSQL | Evaluaciones, revisiones, versiones de migración y vista de reportes |
| Power BI | Reporte Desktop independiente de los filtros React |
| Docker | Empaquetado y operación local con volumen persistente |
| GitHub Actions | Suites, migraciones, lanzadores, auditoría npm, lint y construcción |
| Microsoft Entra ID | Identidad y autorización delegada |
| APIs financieras | Contexto económico público, normalizado y con procedencia |
| Scrum | Backlog, objetivos de sprint, inspección, adaptación y evidencia real |

### Comunicaciones y contratos

- React–API: REST sobre HTTP local con JSON; mismo origen mediante Nginx. Las llamadas externas usan HTTPS con validación de certificados.
- Identidad: MSAL; requisito arquitectónico OAuth 2.0 Authorization Code + PKCE y OIDC, siguiendo [Microsoft](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow). API con `Authorization: Bearer`, validación JWT de firma, audiencia, emisor, tenant, cliente, vigencia, ámbito y rol. No implementar manualmente un nuevo protocolo de login.
- Origen probado: `http://localhost:8080/`. No asumir que abrir otro puerto/origen funciona con los registros actuales.
- PostgreSQL: protocolo TCP, conexión interna Docker; Power BI usa loopback 55433 y lector limitado. HTTP/TCP local sin TLS no se autoriza para redes públicas.
- Fechas persistidas en UTC; filtros de dashboard incluyen ambos días UTC. Identificadores UUID.
- No se incorporan WebSockets, mensajería ni sincronización offline en esta entrega.

Contratos principales existentes: `/api/v1/evaluar`, `/evaluaciones`, `/evaluaciones/{id}`, `/evaluaciones/{id}/revisiones`, `/evaluaciones/{id}/explicacion`, `/dashboard`, `/azure-search/documentos`, `/azure-search/buscar`, `/azure-ml/predecir` y `/datos-financieros/indicadores`; todas bajo `/api/v1`. `GET /` comprueba disponibilidad de API, no por sí solo salud de base/proveedores. Configuración pública y OpenAPI no dan acceso a datos de negocio.

Errores: 401 identidad, 403 permisos, 404 recurso inexistente, 409 conflicto/idempotencia, 422 validación, 503 configuración/dependencia no disponible; integraciones pueden devolver 502 ante contrato/fallo remoto y 504 por timeout. No reenviar mensajes privados del proveedor.

### Modelo de datos

- `evaluaciones`: UUID, fecha TIMESTAMPTZ, solicitud JSONB y resultado JSONB con versión de reglas.
- `revisiones`: UUID, relación a evaluación, versión, estado, observación, responsable y fecha; versión única por evaluación.
- `schema_migrations`: versiones SQL aplicadas, con ejecución repetible.
- `reportes.evaluaciones_powerbi`: vista que excluye RFC, responsable y observaciones; no es una réplica editable.
- Las explicaciones, escenarios UCI y cachés externas no se persisten como evaluaciones en el diseño actual. La caché financiera es por proceso/proveedor.

## 9. Requisitos no funcionales y salvaguardas

1. Datos ficticios exclusivamente. Ningún aviso de la UI equivale a consentimiento para usar expedientes reales.
2. Claves solo en configuración privada del servidor; fuera de Git, frontend y capturas compartidas. Los .env actuales no están cifrados.
3. No enviar RFC, identidad o revisiones a OpenAI, ni datos de solicitantes a proveedores financieros. Azure ML recibe solo las variables UCI.
4. Explicación automática únicamente tras guardado confirmado. Deduplicación por UUID en memoria de pantalla; no se presume una cuota/deduplicación global entre sesiones.
5. Recuperación documental antes de generar: si falla, informar sin inventar una guía. La IA requiere revisión humana; `store=false` no garantiza retención cero del proveedor.
6. Fallos externos aislados del resultado y persistencia. Sin reintentos externos automáticos que puedan multiplicar consumo.
7. Límites actuales: timeout OpenAI 60 s, ML 30 s, Search 8 s; dos generaciones OpenAI simultáneas por proceso. No son SLA ni cuotas productivas.
8. Caché financiera: una hora para datos válidos y un minuto para errores; mostrar periodo de observación separado de hora de consulta. No presentar datos vencidos como vigentes.
9. Respaldo manual privado y ensayo aislado. El dump actual no cifra ni incluye roles globales/ACL; el volumen Docker no es un respaldo.
10. Migraciones repetibles y pruebas con PostgreSQL temporal, sin usar la base de trabajo.
11. Marca NexoCredit consistente; adaptación de las dos guías propia solo en presentación, conservando fuentes/versiones y originales Search.
12. No prometer WCAG, cumplimiento legal, penetración segura, disponibilidad 24/7 ni carga productiva sin evaluación específica.

## 10. Métricas de éxito

Metas propuestas para aceptación, no resultados inventados. Las pruebas automáticas y las observaciones de una muestra ficticia no demuestran adopción ni aptitud crediticia.

| Dimensión | Meta de aceptación | Línea base / método |
|---|---|---|
| Reglas demo | 100 % de los casos de aceptación coinciden con la tabla de reglas, incluidos umbrales y score | Suites existentes aprobadas; ampliar/mantener casos al cambiar código |
| Persistencia e idempotencia | Sin duplicados para mismo UUID/datos; conflicto cuando cambian; registro recuperable tras recargar | Comprobado en tests y prueba integral ficticia; no significa pérdida cero ante cualquier desastre |
| Revisión | Identidad del servidor, versión incremental y riesgo original sin cambios en todos los casos de aceptación | Pruebas y recorrido local existentes; auditoría completa fuera de alcance |
| Acceso | Todos los casos definidos de token ausente/inválido o permisos insuficientes se rechazan | Pruebas negativas y 401 real; no equivale a una auditoría de penetración |
| Explicación | En 6 escenarios ficticios acordados, 6 explicaciones con guía/sección/versión correctas y sin contradicción de reglas | Meta propuesta; una consulta real correcta no certifica 6/6 ni todas las respuestas futuras |
| Documentos | Recuperar el catálogo completo de 2 guías / 14 secciones y conservar fuente/versión | Observado; no deben inventarse documentos ante error |
| APIs financieras | Cada observación muestra unidad, periodo y fuente; cada fallo mantiene estado veraz | Ambos proveedores disponibles el 04/10/2026; no hay porcentaje de uptime medido |
| Power BI | Cero diferencias SQL–DAX en los 16 contextos y 6 medidas del protocolo de prueba | 96 comparaciones sin diferencias el 30/09/2026; repetir al cambiar medidas/vista y alinear corte de datos |
| Calidad de código | Todas las suites pasan sin omisiones inesperadas; lint/build/migraciones aprobados | Línea base: 69 backend y 48 frontend; CI final 37247558296, SHA 914ac8aa7abfeefae746dda4bd9c59ec9191719d |
| Dependencias | Sin vulnerabilidades altas/críticas conocidas reportadas por npm audit en la versión revisada | Audit reportó 0 en CI fechada; reevaluar, no garantía futura |
| Restauración | Cero diferencias en filas/huellas/esquema/vistas del respaldo ensayado; origen intacto | 3 tablas conciliadas en destino aislado; no se fijó RPO/RTO productivo |
| Usabilidad | Completar captura, consulta y revisión sin ayuda correctiva; distinguir “riesgo demo” de “aprobación” | Objetivo propuesto para prueba acompañada con participantes confirmados; aún no medido |
| Rendimiento local (Should) | p95 <= 2 s para evaluar/guardar o consultar dashboard, sin incluir IA/proveedores | Supuesto técnico propuesto: equipo documentado, servicios calientes, 100 operaciones ficticias y un usuario; sin benchmark realizado |

No se define un KPI de disminución de mora, AUC mínima productiva o aprobación automática. El candidato UCI tiene AUC de prueba 0.775274 y sensibilidad 32.01 % en su experimento local; no permite fijar metas para clientes mexicanos ni una probabilidad calibrada individual.

## 11. Supuestos y decisiones documentadas

| ID | Supuesto/decisión | Efecto y límite |
|---|---|---|
| A01 | MVP local en Windows con Docker Desktop y navegador compatible con MSAL | Entorno existente, no promesa de instalador portable ni de acceso remoto |
| A02 | Un usuario interactivo para la aceptación inicial | Supuesto de prueba; no demuestra capacidad multiusuario |
| A03 | REST/JSON, UTC, UUID y PostgreSQL 17 | Se conservan contratos y componentes existentes, sin inventar otra base |
| A04 | Equipo/servicios actuales disponibles durante la revisión | Requiere Internet y configuración privada; costes Azure no aprobados por este PRD |
| A05 | Authorization Code + PKCE/OIDC delegado a MSAL | Decisión de seguridad arquitectónica; no cambia registros o permisos existentes |
| A06 | Sin nuevos servicios de colas/caché para la demo | La caché por proceso no se presenta como distribuida |
| A07 | Mantener representación monetaria actual durante el MVP | Hoy la API usa float y round. Para una evolución contable, proponer Decimal/NUMERIC con migración y regresión explícitas; no afirmar que ya está implementado |
| A08 | Sprints de dos semanas como propuesta de organización | Calendario, capacidad y responsabilidades pendientes de acuerdo; 500 horas son propuesta, no tiempo acreditado |

No se asumen detalles sustantivos ausentes: política crediticia oficial, autorización de históricos, definición de incumplimiento/horizonte, presupuesto, participantes Scrum, aceptación del asesor o licencias. Esos acuerdos no pueden reemplazarse por una “mejor práctica” técnica.

## 12. Plan de entrega, Scrum y Definition of Done

Secuencia propuesta, sin fechas u horas inventadas:

1. Congelar alcance y revisar este PRD/MoSCoW con usuario y asesor.
2. Completar manuales y evidencia depurada; registrar un guion de demostración local.
3. Realizar la revisión acompañada: flujos UC01–UC11, límites y fallos cubiertos en pruebas, sin provocar gastos o escrituras no acordados.
4. Registrar hallazgos y priorizar correcciones; repetir suites/CI si cambia código.
5. Registrar aceptación o rechazo y capacitación solo después de que ocurran.

Scrum exige responsables, objetivos, backlog y eventos reales de planificación, seguimiento, revisión y retrospectiva; el backlog existente no sustituye estos eventos. Se propone registrarlos conforme a la [Guía Scrum](https://scrumguides.org/scrum-guide.html), sin adjudicar retrospectivamente reuniones u horas.

Definition of Done del MVP propuesto:

- Todos los Must tienen evidencia y criterios de aceptación satisfechos.
- Pruebas automáticas, migraciones, lint/build y CI identificada por commit pasan.
- Manuales, PRD y límites son coherentes con el código; secretos y datos privados no forman parte de la entrega.
- Se demuestra guardado/revisión, fallo de IA sin pérdida del resultado, estados externos veraces y separación UCI/MXN.
- Respaldo/restauración aislada conciliados; ningún ensayo sobrescribe datos de trabajo.
- Revisión con asesor, observaciones, decisión y evidencia Scrum registradas realmente.

**Estado actual:** núcleo técnico de la demo comprobado; no MVP formalmente aceptado. Falta cerrar revisión/capacitación/evidencia Scrum, aprobar este PRD y ejecutar las nuevas metas de aceptación propuestas. La comparación binaria ML permanece pendiente; no se transforma en validación crediticia por completar ese punto.

## 13. Riesgos y dependencias

| Riesgo | Tratamiento |
|---|---|
| Confundir demo o estado Aprobada con concesión real | Avisos explícitos, revisión humana y ausencia de acciones de desembolso |
| Explicación incorrecta de IA | Contexto citado, validación de contrato, rúbrica de aceptación y revisión humana |
| Sesión, cuota o servicio externo no disponible | Estados/fallos sanitizados; core y registros conservados cuando falla una integración |
| Coste por IA/ML o abuso del proxy | Acceso local, sin reintentos automáticos; antes de ampliar uso acordar presupuesto y cuotas |
| Usar UCI como predictor para clientes reales | Laboratorio separado, métricas y población explícitas; no conversión de variables |
| Fuga de secretos/capturas/cachés | Exclusión de Git y entrega depurada; la retirada de seguimiento no elimina commits históricos |
| Pérdida de base o respaldo incompleto | Ensayo aislado realizado; ampliar roles/ACL/cifrado/retención y objetivos antes de producción |
| Cifras web y Power BI con cortes diferentes | Actualizar y anotar corte; no confundir dashboard vivo con reporte importado |
| Acreditar Scrum o 500 horas sin evidencia | Registros posteriores a los eventos reales; responsables/calendario por acordar |

Dependencias: Docker y equipo local, cuenta Entra autorizada, PostgreSQL, configuraciones privadas, recursos Azure existentes, token Banxico, acceso de red y Power BI Desktop para revisar el reporte. No crear nuevas suscripciones ni compartir credenciales desde este documento.

## 14. Fuentes de la línea base

- [README y alcance actual](../../README.md).
- [Tecnologías obligatorias y estado](../../REQUISITOS_TECNOLOGICOS.md).
- [Plan previo y requisitos RF01–RF09](../planificacion/PLAN_PROYECTO.md).
- [Backlog de cierre](../../gestion_proyecto/scrum/BACKLOG_CIERRE.md).
- [QA y registros históricos](../calidad/QA.md).
- [Prueba integral ficticia](../evidencias/2026-10-04/prueba-e2e.md).
- [Cierre técnico local](../evidencias/2026-10-04/cierre-tecnico.md).
- [Primera CI del cierre y límites](../evidencias/2026-10-04/github-actions.md).
- [CI del commit final 914ac8a](https://github.com/MikiJMA/EmpresaPluri/actions/runs/37247558296).
- Contratos revisados en validación, scoring, rutas, persistencia e integraciones del backend.

Los resultados anteriores son evidencia fechada; este PRD no ejecuta nuevamente consultas Azure, pruebas de carga, CI ni cambios de datos. Tampoco modifica código, despliegues, permisos, secretos o decisiones de negocio.
