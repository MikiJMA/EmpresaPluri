# NexoCredit — demostración de análisis de riesgo crediticio

NexoCredit es una marca demostrativa, no una razón social ni una aprobación empresarial. Los identificadores técnicos existentes se conservan para mantener las conexiones; la documentación histórica del proyecto no se altera retrospectivamente.

Accesos de Windows: [operacion](operacion/README.md). Documentación: [índice](docs/README.md), [PRD](docs/producto/PRD_NEXOCREDIT.md) y [MVP](docs/producto/MVP_NEXOCREDIT.md). Para una vista limpia en VS Code, abrir [NexoCredit.code-workspace](../NexoCredit.code-workspace) desde la raíz exterior.

## Tecnologías obligatorias

Python, FastAPI, React.js, Azure OpenAI Service, Azure Machine Learning, Azure AI Search, PostgreSQL, Power BI, Docker, GitHub Actions, Microsoft Entra ID, APIs financieras y Scrum. Consultar [función, ubicación y estado de cada tecnología](REQUISITOS_TECNOLOGICOS.md). El uso técnico de estas herramientas no acredita producción ni ejecución de Scrum por sí solo.

**Azure sí está implementado en la demo**: OpenAI, Machine Learning, AI Search y acceso Microsoft Entra conservan su código y evidencias reales del 04/10/2026. La alternativa local no los elimina. Los campos para sus keys se mantienen en el `.env` privado de Docker y en las plantillas sin secretos. [Implementación Azure y dónde colocar las llaves](docs/manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md). Esto no afirma vigencia de la suscripción o conectividad cloud actual.

## Estado real

Limpieza local del 14/10/2026: retirados a la Papelera la plantilla y dependencias antiguas de `docs/archivo`, `.venv-roto`, temporales de pruebas sin referencias y cachés Python (aproximadamente 35,7 MB). Se conservan el entorno activo, las dependencias frontend, credenciales, PostgreSQL, reportes, modelos, documentación y evidencias. No se alteraron imports ni rutas de ejecución. El PRD/MVP combinado histórico permanece como antecedente.

### Preparación de entrega — 14/10/2026

[GitHub Actions del código](docs/evidencias/2026-10-14/github-actions.md) aprobó ambos trabajos con 197/129. ZIP candidato real revisado; la copia final se acompaña de manifiesto de integridad, sin datos privados. Power BI conserva sus definiciones pero requiere el refresco manual pendiente, sin control automático de ventanas.

Suite local final: **197 backend/PostgreSQL y 129 frontend**, sin omisiones, cinco archivos PowerShell, lint/build y auditoría npm con cero vulnerabilidades conocidas. Se añadió una prueba integral aislada, corrección Ollama comprobada en vivo y un generador de ZIP público con manifiesto SHA-256, sin base, cuentas o llaves. Restauración aislada del respaldo de doce tablas aprobada. Las comprobaciones del navegador, hallazgos y pendientes de Power BI/CI/ZIP están separados en la [evidencia de entrega](docs/evidencias/2026-10-14/entrega-demo.md); no se presenta como aceptación o publicación de la aplicación. [Guía de entrega e instalación](docs/entrega/ENTREGA_DEMO.md).

### Reglas de riesgo y presentación monetaria — 13/10/2026

Las nuevas evaluaciones usan **`reglas-demo-v2`**: score **0–499 → Alto**, **500–679 → Medio** y **680–1000 → Bajo**. El margen mensual impone un riesgo mínimo: **$7,000 o menos → Alto**, **más de $7,000 y hasta $15,000 → Medio**, **más de $15,000 → Bajo**. El resultado toma la categoría más riesgosa de ambas: un buen margen nunca mejora un score de riesgo Alto. Son rangos propios de la demo, no una escala oficial de Buró ni un modelo predictivo. [Reglas, ejemplos y conservación del historial](docs/manuales/REGLAS_RIESGO_DEMO.md).

Los resúmenes monetarios de la interfaz se redondean a pesos completos, sin decimales: `$18,333.33` se presenta como `$18,333`. Esto sólo cambia la presentación; captura, cálculos y almacenamiento conservan los centavos. Los detalles de importes y pagos mantienen la precisión necesaria. El riesgo se calcula con el margen a dos decimales, no con su cifra visual redondeada.

Las evaluaciones anteriores mantienen su resultado y versión `reglas-demo-v1`; no se recalculan, y sus explicaciones utilizan la guía histórica correspondiente. Las nuevas explicaciones requieren la guía de versión 2.0. El catálogo **local** incluye ahora **3 guías / 15 secciones**. La evidencia histórica de **Azure AI Search** sigue siendo **2 guías / 14 secciones** hasta cargar y comprobar la guía nueva en ese proveedor; este incremento no realiza consultas ni cargas cloud. Los adaptadores Azure y sus campos de keys permanecen. No se atribuyen a esta nota pruebas, despliegues, aceptación o disponibilidad externa no registrados.

Comprobación del incremento del 13/10/2026: 175 pruebas backend/PostgreSQL y 129 frontend, lint/build y cinco archivos PowerShell aprobados. Docker actualizado con imágenes locales verificadas tras fallo DNS del registro, sin recrear PostgreSQL. Datos/esquema e identidad coinciden con el respaldo: nueve evaluaciones, dos revisiones y una cuenta conservadas. [Resultados, QA visual y límites](docs/evidencias/2026-10-13/reglas-v2-y-importes.md). Sin generación IA real, carga Azure o CI nueva.

### IA predictiva local adicional — 12/10/2026

**Laboratorio IA** incorpora un modelo entrenado localmente con scikit-learn, `nexocredit-uci-logistica-v1`, sin llave ni suscripción Azure. El modo local ahora lo activa explícitamente. No utiliza el pickle AutoML ni las entradas MXN del formulario principal: son 19 variables académicas UCI/NTD separadas, con clase binaria, origen, advertencias y métricas visibles. Las integraciones Azure siguen disponibles y las reglas principales no cambian. [Manual del laboratorio](docs/manuales/LABORATORIO_IA_LOCAL.md) y [entrenamiento reproducible](inteligencia_artificial/prediccion_local/README.md).

Prueba independiente: AUC 0,71505, sensibilidad 60,92 %, precisión positiva 37,51 % y exactitud 70,28 %, menor que 78,86 % del clasificador siempre negativo. No aprobado para decisiones crediticias ni validado para México. 165 pruebas backend/PostgreSQL, 120 frontend, lint/build y cinco archivos PowerShell aprobados. Auditoría npm actual no completada por un certificado TLS, sin desactivar su validación. Docker saludable y las huellas/contenedor PostgreSQL coinciden con el respaldo previo. [Evidencia y límites del incremento](docs/evidencias/2026-10-12/ia-predictiva-local.md). No actualiza retrospectivamente las evidencias Azure o CI anteriores.

### Alternativa local adicional — 11/10/2026

Acceso local con usuario/contraseña y sesiones cortas, además de Microsoft Entra ID. Adaptadores Azure conservados; selección explícita de proveedor por función. Ollama usa un modelo instalado en el equipo y la búsqueda documental local recupera las mismas dos guías / 14 secciones. También existe una plantilla de reglas marcada como no generada por IA. El laboratorio ML local está deshabilitado: no se carga el pickle AutoML sin su entorno compatible. Las evaluaciones, revisiones, PostgreSQL, APIs financieras y Power BI mantienen sus responsabilidades. Ver [operación, ubicación de llaves y límites](docs/manuales/ACCESO_LOCAL_Y_PROVEEDORES.md). Las evidencias Azure del 04/10/2026 no prueban vigencia de la suscripción ni conectividad actual.

Comprobación inicial del 11/10/2026: 109 pruebas backend/PostgreSQL y 64 frontend aprobadas tras ajustar el mínimo de contraseña local a seis caracteres, lint/build y cinco archivos PowerShell aprobados, generación real con `llama3.1:8b` y modo local aplicado en Docker conservando 9 evaluaciones y 2 revisiones. Ver [evidencia de ese cambio](docs/evidencias/2026-10-11/acceso-local-y-ollama.md).

Comprobación posterior del 11/10/2026: 116 pruebas backend/PostgreSQL y 79 frontend aprobadas, lint/build, auditoría npm y cinco archivos PowerShell. Se corrigió el rechazo del FIX cuando Banxico publica la tasa con fecha futura, se presenta el nombre del responsable sin su identificador técnico y la guía del score queda abierta. Se añadió [revisión opcional de RFC/CURP](docs/manuales/REVISION_RFC_CURP.md), limitada a formato y fecha, con consulta oficial manual en SAT. No certifica identidad ni guarda CURP. Aplicación Docker saludable con 9 evaluaciones, 2 revisiones y una cuenta local creada por el usuario conservadas. No se ejecutó CI remota nueva. Ver [pruebas, consultas reales y límites](docs/evidencias/2026-10-11/banxico-responsable-rfc.md).

Correcciones tras pruebas de ruptura del 11/10/2026: validación estricta de importes, errores 422 saneados, identificadores nuevos limitados sin exigir formato SAT a la demo, paginación acotada y contratos de respuestas/Error Boundary en React. Acceso con contadores separados de fallos/ráfagas y proxy explícito. Caché privada PostgreSQL de explicaciones, reutilización 24 horas y cuota de diez nuevas generaciones por cuenta/hora, sin enviar identidad al modelo. La explicación ya no reside únicamente en memoria de la pantalla. [Pruebas y límites de estas correcciones](docs/evidencias/2026-10-11/correcciones-ruptura.md).

Segunda ronda corregida del 11/10/2026: observaciones visibles sin NUL/controles ocultos, fechas de calendario y contratos de datos coherentes, reserva durable de cuota antes de generar y errores TLS controlados. Las nuevas capturas rechazan pagos superiores a los gastos que los incluyen y atraso pendiente con deuda cero; no reescriben registros antiguos ni cambian el scoring. **139 pruebas backend/PostgreSQL y 96 frontend aprobadas**, lint/build, auditoría npm y cinco archivos PowerShell. Docker local actualizado sin recrear PostgreSQL, con los mismos 9 registros de evaluación, 2 revisiones y 1 cuenta. [Resultados y alcance](docs/evidencias/2026-10-11/correcciones-ruptura-ronda-2.md).

Seguimiento implementado del 11/10/2026: nueva sección **Créditos y pagos**, con planes ficticios, cuotas, abonos parciales exactos, saldos/atraso/puntualidad y alertas persistidas/versionadas. Eventos transaccionales con responsable; auditoría global nueva sólo Administrador. No importa Buró, verifica depósitos, calcula intereses ni cambia `reglas-demo-v1`. Migración 005 aditiva: se conservan 9 evaluaciones, 2 revisiones y 1 cuenta, sin convertirlas automáticamente en créditos. [Manual](docs/manuales/SEGUIMIENTO_CREDITICIO.md), [arquitectura](docs/desarrollo/ARQUITECTURA_Y_DATOS.md), [pruebas y límites](docs/evidencias/2026-10-11/seguimiento-crediticio.md). No se involucró al asesor ni se certificaron capacitación o Scrum.

### Estado histórico Azure y cierre técnico — 04/10/2026

Actualizado el 04/10/2026. Demo local autenticada comprobada de extremo a extremo. Tras el cierre técnico y cambio de marca: 69 pruebas backend/PostgreSQL y 48 frontend aprobadas, sin omisiones; lint, build y tres archivos de pruebas PowerShell aprobados. GitHub Actions confirmó esos mismos conteos en el commit de código `19223ae`, con ambos trabajos aprobados; [ejecución y SHA completo](docs/evidencias/2026-10-04/github-actions.md). Publicado en rama de revisión, sin cambiar main ni desplegar la aplicación. Las pruebas automáticas usan respuestas externas simuladas; las consultas Azure y financieras reales tienen evidencia separada. Ver [cierre técnico local](docs/evidencias/2026-10-04/cierre-tecnico.md), [entrega de demostración](docs/entrega/ENTREGA_DEMO.md) y [QA](docs/calidad/QA.md).

Microsoft Entra ID: acceso mediante MSAL y protección de las rutas de negocio en FastAPI. Se comprueban firma, audiencia, emisor, tenant, cliente, ámbito y rol. Analista y Administrador tienen actualmente acceso al mismo conjunto de rutas; no hay funciones administrativas diferenciadas. La sesión real se probó y las rutas de negocio rechazan solicitudes sin token.

Detalle y revisión manual demo: desde el historial, Ver detalle permite consultar los datos capturados y guardar estado Pendiente/Aprobada/Rechazada y observaciones. El servidor fija el responsable desde la identidad Entra, sin confiar en el nombre enviado por el navegador. Las revisiones anteriores a esta integración pueden contener nombres declarados. Cada cambio conserva fecha y versión en la tabla revisiones (migración 002), sin modificar el riesgo original ni autorizar créditos reales. No equivale a una auditoría operativa completa.

Azure OpenAI genera automáticamente una explicación después de guardar un escenario, usando la guía DEM-02 de Azure AI Search. No envía RFC ni modifica el riesgo; cada nueva evaluación puede generar consumo de pago. La explicación permanece solo en memoria de la pantalla. Documentos muestra el catálogo real de 2 guías / 14 secciones y permite búsquedas; no son políticas oficiales de crédito.

Dashboard React implementado: total de evaluaciones, margen promedio, deuda promedio con cobertura de datos y distribución por riesgo demo. Filtros propios por fecha (días inclusivos UTC) y riesgo; el historial inferior permanece independiente. API: GET /api/v1/dashboard?desde=2026-09-01&hasta=2026-09-30&riesgo=Bajo. Resume todos los registros coincidentes en PostgreSQL, no una página. Es independiente del reporte Power BI.

Power BI local comprobado y guardado el 30/09/2026: proyecto PBIP con 11 visuales, actualización desde una vista PostgreSQL de lectura limitada, filtros por riesgo/revisión y 96 comparaciones SQL–DAX sin diferencias. Los datos ausentes no se convierten en cero y los estados de revisión no autorizan créditos. Sin publicación cloud ni gateway. Consultar [operación y pruebas del reporte](analitica/reportes_power_bi/README.md).

El formulario captura también deuda actual total (MXN), suma de pagos mensuales de créditos (MXN) y días de atraso del pago vencido más antiguo aún pendiente. Son obligatorios en la interfaz y admiten cero; los gastos incluyen los pagos de créditos. Se validan y conservan en el JSON de la solicitud en PostgreSQL, sin cambiar las reglas demo. La API admite solicitudes antiguas que omitan estos campos; ausencia no equivale a cero. No se requiere modificar ni borrar la tabla existente.

Prototipo local React + FastAPI con persistencia PostgreSQL. Permite capturar un escenario ficticio, validar entradas, explicar las reglas y consultar evaluaciones guardadas. El estado de las integraciones se detalla en sus módulos y en REQUISITOS_TECNOLOGICOS.md; este prototipo no acredita aptitud predictiva ni una instalación de producción. No utilizar con solicitudes reales ni exponer públicamente.

### Indicadores financieros públicos — actualización del 04/10/2026

«Indicadores financieros» consulta la ruta autenticada `GET /api/v1/datos-financieros/indicadores`. Banxico FIX/tasa y Banco Mundial inflación/PIB aparecen disponibles en la prueba real del 04/10/2026, con sus cuatro observaciones, periodos, unidades y enlaces de procedencia. Esto sustituye el fallo del token documentado el día anterior; no garantiza disponibilidad futura. No son datos en tiempo real, historial crediticio privado ni entradas que cambien el riesgo demo. No se envían evaluaciones a estas fuentes.

`operacion/integraciones/Conectar Banxico.cmd` permite guardar el token de forma privada, encender PostgreSQL si está detenido y recrear únicamente el backend. Para recuperar el arranque sin volver a pegar el token: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\configurar-banxico.ps1 -UsarTokenGuardado`. No borra ni recrea el volumen de datos. Consultar [contrato, límites, configuración y pruebas de las APIs financieras](backend/app/integraciones/datos_financieros/README.md). Esta sección sustituye las menciones anteriores de integración financiera totalmente pendiente; no cambia el estado de otras tecnologías.

## Arranque con Docker

Con Docker Desktop abierto, ejecutar desde la carpeta interior:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

Abrir [http://localhost:8080/](http://localhost:8080/) e iniciar sesión con una cuenta Microsoft autorizada, o con una cuenta local si está habilitada y creada. Ver [creación de cuenta local](docs/manuales/ACCESO_LOCAL_Y_PROVEEDORES.md#crear-la-primera-cuenta-local). La configuración Entra actual requiere exactamente ese origen, no 127.0.0.1 ni otro puerto. Incluye frontend, backend, PostgreSQL y migraciones automáticas. Los datos quedan en un volumen Docker separado de la base local; no se migran registros entre ambos entornos. Para detener conservando datos, cambiar `iniciar` por `detener`. Consultar [operación de Docker](infraestructura/contenedores_docker/README.md).

## PostgreSQL local y arranque sin Docker

Para abrir una instalación Docker ya construida sin volver a descargar ni compilar, usar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 abrir`. Espera los servicios y abre el navegador. Requiere Docker Desktop activo e imágenes existentes; después de modificar código, ejecutar `iniciar` para reconstruir.

Desde la carpeta interior, preparar la base una sola vez tras instalar backend/requirements.txt:

Esta alternativa sirve para desarrollo, no es el flujo autenticado probado en Docker. El acceso Entra publicado por la API está fijado a localhost:8080; usar 5173 u otro origen requiere una configuración de registros y aplicación acorde. No desactivar autenticación para probarla.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\postgresql-local.ps1 preparar
```

Iniciar backend e interfaz en terminales separadas:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar-backend.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar-frontend.ps1
```

El lanzador del backend inicia PostgreSQL si ya está preparado. La base escucha solo en 127.0.0.1:55432; no se instala un servicio de Windows. Los datos quedan en `.local/postgresql/datos` (no borrar) y la configuración privada en `backend/.env.postgresql`. Al evaluar se confirma el guardado y se actualiza el historial. Para detener solo la base: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\postgresql-local.ps1 detener`.

Sin DATABASE_URL el formulario indica que no se guardó; si la base está configurada pero falla, se devuelve un error. Ver backend/app/persistencia_postgresql/README.md.

## Ejecutar en Windows

Desde la carpeta interior `empresa - copia`, que contiene `backend`, `frontend` y `scripts`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 --no-proxy-headers
```

En otra terminal:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Abrir http://127.0.0.1:5173. Documentación de API: http://127.0.0.1:8000/docs.
La interfaz admite VITE_API_URL; consultar frontend/.env.example. Reiniciar Vite tras cambiar variables. CORS_ORIGINS en el backend acepta orígenes separados por comas; por defecto solo localhost y 127.0.0.1 en puerto 5173.

## Verificación

La suite completa aislada se ejecuta con `operacion/pruebas/Probar programacion.cmd`: PostgreSQL temporal sin datos de trabajo y limpieza protegida de su propio contenedor. `operacion/respaldos/Respaldar PostgreSQL.cmd` y `operacion/respaldos/Probar restauracion PostgreSQL.cmd` permiten el respaldo manual privado y un ensayo aislado; el ensayo de tres tablas pasó el 04/10/2026. El dump no está cifrado ni incluye roles globales/ACL. No restaura sobre la base original ni acredita recuperación productiva completa.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
cd frontend
node --test tests/*.test.mjs
npm run build
npm run lint
```

Ejemplo ficticio: AAAA010101AA1, ingreso 30000, gastos 10000, score 700. Resultado esperado: margen 20000, riesgo preliminar Bajo. Es una regla de demostración, no una probabilidad calibrada.

## Entregables

Empezar por [ENTREGA_DEMO.md](docs/entrega/ENTREGA_DEMO.md): alcance comprobado, evidencias, guion de revisión y pendientes. Consultar [plan](docs/planificacion/PLAN_PROYECTO.md), [manual](docs/manuales/OPERACION.md), [QA](docs/calidad/QA.md), [índice de evidencias](docs/evidencias/README.md) y [backlog de cierre](gestion_proyecto/scrum/BACKLOG_CIERRE.md). El cronograma de 500 horas es propuesto, no horas acreditadas; no hay aceptación del asesor ni sprints certificados.

## Organización de carpetas

```text
empresa - copia/                         Raíz del proyecto (carpeta interior)
├── backend/                             Python + FastAPI
│   ├── app/
│   │   ├── main.py                      Entrada de la API
│   │   ├── rutas_api/                   Endpoints HTTP
│   │   ├── validacion_datos/            Validación de solicitudes
│   │   ├── evaluacion_crediticia/       Reglas de riesgo actuales
│   │   ├── persistencia_postgresql/    Guardado, historial y migraciones
│   │   ├── autenticacion_entra_id/     Identidad Entra y acceso delegado
│   │   └── integraciones/              Adaptadores Azure y financieros activos en demo
│   │       ├── explicaciones_azure_openai/
│   │       ├── prediccion_azure_ml/
│   │       ├── prediccion_local/        Inferencia UCI numérica local; no scoring principal
│   │       ├── busqueda_azure_ai_search/
│   │       └── datos_financieros/
│   └── tests/                          Pruebas automatizadas
├── frontend/                           React.js
│   └── src/
│       ├── evaluacion_crediticia/
│       │   ├── componentes/            Formulario y resultado
│       │   └── servicios/              Cliente HTTP
│       └── styles/                     Estilos compartidos
├── inteligencia_artificial/
│   ├── prediccion_azure_ml/             Candidato UCI evaluado; no validado para crédito real
│   └── prediccion_local/                Baseline scikit-learn UCI; separado del formulario MXN
├── analitica/reportes_power_bi/         Dashboard Power BI local verificado
├── infraestructura/contenedores_docker/ Dockerfiles, Compose, Nginx y base persistente
├── gestion_proyecto/scrum/             Backlog de cierre; sprints aún por acreditar
├── docs/                               Índice de documentación
│   ├── producto/                       PRD y MVP separados
│   ├── planificacion/                  Plan del proyecto
│   ├── manuales/                       Operación y soporte
│   ├── calidad/                        QA
│   ├── entrega/                        Guion y alcance de entrega
│   ├── desarrollo/                     Documentación de CI
│   ├── evidencias/                     Registros fechados
│   ├── estadia/                        Información académica
│   └── archivo/                        Originales conservados
├── operacion/                          Accesos .cmd para Windows
│   ├── aplicacion/                     Abrir, actualizar y detener
│   ├── integraciones/                  Conexiones Azure/Banxico y carga documental
│   ├── pruebas/                        Suite aislada
│   └── respaldos/                      Respaldo y ensayo de restauración
├── scripts/                            Implementación Python/PowerShell y pruebas
└── REQUISITOS_TECNOLOGICOS.md           Tecnologías obligatorias y estado
```

El workflow está en `.github/workflows/ci.yml` de la raíz Git exterior, no dentro de esta carpeta. Las carpetas generadas, .local, .venv, .venv-roto y el archivo histórico se ocultan en VS Code; siguen en disco. No se movieron datos, secretos, entornos virtuales o proyectos Power BI privados. Ver el [mapa del espacio de trabajo](../README.md).

## Laboratorio UCI / Azure ML

Formulario académico separado de 19 variables UCI y cliente remoto FastAPI conectados al endpoint Azure existente. La consulta real autenticada del 04/10/2026 devolvió una clase booleana; el aviso distingue espera, éxito y fallo del último intento. No persiste el escenario UCI, no carga el pickle en el backend y no convierte MXN a NTD. El formulario principal sigue usando reglas demo. La etiqueta `modelo_configurado` no verifica la versión remota. Una lectura independiente de metadatos Azure ML Studio comprobó ese día el modelo registrado servido `plurione-uci-voting-candidato:1`, aprovisionamiento correcto y tráfico directo 100 %. La comparación binaria con el artefacto local y la aptitud para población real siguen pendientes. Consultar [contrato, configuración y límites](backend/app/integraciones/prediccion_azure_ml/README.md).
