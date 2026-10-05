# NexoCredit — demostración de análisis de riesgo crediticio

NexoCredit es una marca demostrativa, no una razón social ni una aprobación empresarial. Los identificadores técnicos existentes se conservan para mantener las conexiones; la documentación histórica del proyecto no se altera retrospectivamente.

## Tecnologías obligatorias

Python, FastAPI, React.js, Azure OpenAI Service, Azure Machine Learning, Azure AI Search, PostgreSQL, Power BI, Docker, GitHub Actions, Microsoft Entra ID, APIs financieras y Scrum. Consultar [función, ubicación y estado de cada tecnología](REQUISITOS_TECNOLOGICOS.md). El uso técnico de estas herramientas no acredita producción ni ejecución de Scrum por sí solo.

## Estado real

Actualizado el 04/10/2026. Demo local autenticada comprobada de extremo a extremo. Tras el cierre técnico y cambio de marca: 69 pruebas backend/PostgreSQL y 48 frontend aprobadas, sin omisiones; lint, build y tres archivos de pruebas PowerShell aprobados. Las pruebas automáticas usan respuestas externas simuladas; las consultas Azure y financieras reales tienen evidencia separada. Ver [cierre técnico local](docs/evidencias/2026-10-04/cierre-tecnico.md), [entrega de demostración](docs/ENTREGA_DEMO.md) y [QA](docs/QA.md). La nueva ejecución GitHub Actions se documentará por commit al finalizar.

Microsoft Entra ID: acceso mediante MSAL y protección de las rutas de negocio en FastAPI. Se comprueban firma, audiencia, emisor, tenant, cliente, ámbito y rol. Analista y Administrador tienen actualmente acceso al mismo conjunto de rutas; no hay funciones administrativas diferenciadas. La sesión real se probó y las rutas de negocio rechazan solicitudes sin token.

Detalle y revisión manual demo: desde el historial, Ver detalle permite consultar los datos capturados y guardar estado Pendiente/Aprobada/Rechazada y observaciones. El servidor fija el responsable desde la identidad Entra, sin confiar en el nombre enviado por el navegador. Las revisiones anteriores a esta integración pueden contener nombres declarados. Cada cambio conserva fecha y versión en la tabla revisiones (migración 002), sin modificar el riesgo original ni autorizar créditos reales. No equivale a una auditoría operativa completa.

Azure OpenAI genera automáticamente una explicación después de guardar un escenario, usando la guía DEM-02 de Azure AI Search. No envía RFC ni modifica el riesgo; cada nueva evaluación puede generar consumo de pago. La explicación permanece solo en memoria de la pantalla. Documentos muestra el catálogo real de 2 guías / 14 secciones y permite búsquedas; no son políticas oficiales de crédito.

Dashboard React implementado: total de evaluaciones, margen promedio, deuda promedio con cobertura de datos y distribución por riesgo demo. Filtros propios por fecha (días inclusivos UTC) y riesgo; el historial inferior permanece independiente. API: GET /api/v1/dashboard?desde=2026-09-01&hasta=2026-09-30&riesgo=Bajo. Resume todos los registros coincidentes en PostgreSQL, no una página. Es independiente del reporte Power BI.

Power BI local comprobado y guardado el 30/09/2026: proyecto PBIP con 11 visuales, actualización desde una vista PostgreSQL de lectura limitada, filtros por riesgo/revisión y 96 comparaciones SQL–DAX sin diferencias. Los datos ausentes no se convierten en cero y los estados de revisión no autorizan créditos. Sin publicación cloud ni gateway. Consultar [operación y pruebas del reporte](analitica/reportes_power_bi/README.md).

El formulario captura también deuda actual total (MXN), suma de pagos mensuales de créditos (MXN) y días de atraso del pago vencido más antiguo aún pendiente. Son obligatorios en la interfaz y admiten cero; los gastos incluyen los pagos de créditos. Se validan y conservan en el JSON de la solicitud en PostgreSQL, sin cambiar las reglas demo. La API admite solicitudes antiguas que omitan estos campos; ausencia no equivale a cero. No se requiere modificar ni borrar la tabla existente.

Prototipo local React + FastAPI con persistencia PostgreSQL. Permite capturar un escenario ficticio, validar entradas, explicar las reglas y consultar evaluaciones guardadas. El estado de las integraciones se detalla en sus módulos y en REQUISITOS_TECNOLOGICOS.md; este prototipo no acredita aptitud predictiva ni una instalación de producción. No utilizar con solicitudes reales ni exponer públicamente.

### Indicadores financieros públicos — actualización del 04/10/2026

«Indicadores financieros» consulta la ruta autenticada `GET /api/v1/datos-financieros/indicadores`. Banxico FIX/tasa y Banco Mundial inflación/PIB aparecen disponibles en la prueba real del 04/10/2026, con sus cuatro observaciones, periodos, unidades y enlaces de procedencia. Esto sustituye el fallo del token documentado el día anterior; no garantiza disponibilidad futura. No son datos en tiempo real, historial crediticio privado ni entradas que cambien el riesgo demo. No se envían evaluaciones a estas fuentes.

`Conectar Banxico.cmd` permite guardar el token de forma privada, encender PostgreSQL si está detenido y recrear únicamente el backend. Para recuperar el arranque sin volver a pegar el token: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\configurar-banxico.ps1 -UsarTokenGuardado`. No borra ni recrea el volumen de datos. Consultar [contrato, límites, configuración y pruebas de las APIs financieras](backend/app/integraciones/datos_financieros/README.md). Esta sección sustituye las menciones anteriores de integración financiera totalmente pendiente; no cambia el estado de otras tecnologías.

## Arranque con Docker

Con Docker Desktop abierto, ejecutar desde la carpeta interior:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

Abrir [http://localhost:8080/](http://localhost:8080/) e iniciar sesión con una cuenta Microsoft autorizada. La configuración Entra actual requiere exactamente ese origen, no 127.0.0.1 ni otro puerto. Incluye frontend, backend, PostgreSQL y migraciones automáticas. Los datos quedan en un volumen Docker separado de la base local; no se migran registros entre ambos entornos. Para detener conservando datos, cambiar `iniciar` por `detener`. Consultar [operación de Docker](infraestructura/contenedores_docker/README.md).

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
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
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

La suite completa aislada se ejecuta con `Probar programacion.cmd`: PostgreSQL temporal sin datos de trabajo y limpieza protegida de su propio contenedor. `Respaldar PostgreSQL.cmd` y `Probar restauracion PostgreSQL.cmd` permiten el respaldo manual privado y un ensayo aislado; el ensayo de tres tablas pasó el 04/10/2026. El dump no está cifrado ni incluye roles globales/ACL. No restaura sobre la base original ni acredita recuperación productiva completa.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
cd frontend
node --test tests/*.test.mjs
npm run build
npm run lint
```

Ejemplo ficticio: AAAA010101AA1, ingreso 30000, gastos 10000, score 700. Resultado esperado: margen 20000, riesgo preliminar Bajo. Es una regla de demostración, no una probabilidad calibrada.

## Entregables

Empezar por [ENTREGA_DEMO.md](docs/ENTREGA_DEMO.md): alcance comprobado, evidencias, guion de revisión y pendientes. Consultar [plan](docs/PLAN_PROYECTO.md), [manual](docs/OPERACION.md), [QA](docs/QA.md), [índice de evidencias](docs/evidencias/README.md) y [backlog de cierre](gestion_proyecto/scrum/BACKLOG_CIERRE.md). El cronograma de 500 horas es propuesto, no horas acreditadas; no hay aceptación del asesor ni sprints certificados.

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
│   └── prediccion_azure_ml/             Candidato UCI evaluado; no validado para crédito real
├── analitica/reportes_power_bi/         Dashboard Power BI local verificado
├── infraestructura/contenedores_docker/ Dockerfiles, Compose, Nginx y base persistente
├── gestion_proyecto/scrum/             Backlog de cierre; sprints aún por acreditar
├── docs/                               Plan, manuales, QA y archivo histórico
├── scripts/                            Inicio de backend y frontend
└── REQUISITOS_TECNOLOGICOS.md           Tecnologías obligatorias y estado
```

El workflow está en `.github/workflows/ci.yml` de la raíz Git exterior, no dentro de esta carpeta. Las carpetas generadas y el archivo histórico pueden estar ocultos en VS Code; siguen en disco.

## Laboratorio UCI / Azure ML

Formulario académico separado de 19 variables UCI y cliente remoto FastAPI conectados al endpoint Azure existente. La consulta real autenticada del 04/10/2026 devolvió una clase booleana; el aviso distingue espera, éxito y fallo del último intento. No persiste el escenario UCI, no carga el pickle en el backend y no convierte MXN a NTD. El formulario principal sigue usando reglas demo. La etiqueta `modelo_configurado` no verifica la versión remota. Una lectura independiente de metadatos Azure ML Studio comprobó ese día el modelo registrado servido `plurione-uci-voting-candidato:1`, aprovisionamiento correcto y tráfico directo 100 %. La comparación binaria con el artefacto local y la aptitud para población real siguen pendientes. Consultar [contrato, configuración y límites](backend/app/integraciones/prediccion_azure_ml/README.md).
