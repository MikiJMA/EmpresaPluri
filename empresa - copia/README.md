# Sistema Inteligente de Análisis de Riesgo Crediticio

Proyecto de estadía para PluriOne S.A. de C.V. / Develop Talent & Technology.

## Tecnologías obligatorias

Python, FastAPI, React.js, Azure OpenAI Service, Azure Machine Learning, Azure AI Search, PostgreSQL, Power BI, Docker, GitHub Actions, Microsoft Entra ID, APIs financieras y Scrum. Consultar [función, ubicación y estado de cada tecnología](REQUISITOS_TECNOLOGICOS.md). Las carpetas de integraciones pendientes contienen guías, no implementaciones activas.

## Estado real

Prototipo local React + FastAPI con persistencia PostgreSQL. Permite capturar un escenario ficticio, validar entradas, explicar las reglas y consultar evaluaciones guardadas. No incluye todavía autenticación, modelo predictivo, servicios Azure ni integración financiera. No utilizar con solicitudes reales ni exponer públicamente.

## Arranque con Docker

Con Docker Desktop abierto, ejecutar desde la carpeta interior:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

Abrir http://127.0.0.1:8080/. Incluye frontend, backend, PostgreSQL y migraciones automáticas. Los datos quedan en un volumen Docker separado de la base local; no se migran registros entre ambos entornos. Para detener conservando datos, cambiar `iniciar` por `detener`. Consultar [operación de Docker](infraestructura/contenedores_docker/README.md).

## PostgreSQL local y arranque sin Docker

Desde la carpeta interior, preparar la base una sola vez tras instalar backend/requirements.txt:

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

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
cd frontend
npm run build
npm run lint
```

Ejemplo ficticio: AAAA010101AA1, ingreso 30000, gastos 10000, score 700. Resultado esperado: margen 20000, riesgo preliminar Bajo. Es una regla de demostración, no una probabilidad calibrada.

## Entregables

Consultar docs/PLAN_PROYECTO.md para alcance, cronograma de 500 horas, arquitectura propuesta, backlog y criterios de cierre. docs/OPERACION.md contiene el manual del prototipo y borradores de soporte/capacitación. docs/QA.md distingue comprobaciones realizadas de validaciones pendientes.

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
│   │   ├── autenticacion_entra_id/     Identidad y permisos (pendiente)
│   │   └── integraciones/              Adaptadores externos (pendientes)
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
│   └── prediccion_azure_ml/             Entrenamiento y validación (pendiente)
├── analitica/reportes_power_bi/         Reportes (pendiente)
├── infraestructura/contenedores_docker/ Dockerfiles, Compose, Nginx y base persistente
├── .github/workflows/                  GitHub Actions (pendiente)
├── gestion_proyecto/scrum/             Seguimiento de sprints
├── docs/                               Plan, manuales, QA y archivo histórico
├── scripts/                            Inicio de backend y frontend
└── REQUISITOS_TECNOLOGICOS.md           Tecnologías obligatorias y estado
```

Para iniciar, ejecutar .\scripts\iniciar-backend.ps1 y .\scripts\iniciar-frontend.ps1 en terminales separadas desde empresa. Las carpetas generadas y el archivo histórico se ocultan en el explorador de VS Code para facilitar la navegación; siguen en disco.
