# NexoCredit — Sistema Inteligente de Análisis de Riesgo Crediticio

Alcance vigente: **piloto empresarial en sombra**, con pruebas controladas, no motor crediticio productivo. Se compararon tres modelos mediante validación anidada; no se demostró una mejora consistente y no se promocionó ningún candidato. Aún falta un historial autorizado de la empresa y validación temporal/operativa. [Protocolo, resultados, controles y contrato de datos](docs/desarrollo/PILOTO_EMPRESARIAL.md). Los apartados académicos anteriores se conservan como historial fechado en [BITACORA.md](docs/BITACORA.md).

Incremento local: el formulario principal incorpora un [modelo mexicano entrenado con ENIF 2024](inteligencia_artificial/prediccion_mexico/README.md), con resultado persistido, métricas reales y capacidad limitada explícita. No depende de Ollama/Azure, no reemplaza los riesgos históricos por reglas ni constituye un predictor validado de impagos futuros. [Pruebas y límites de este incremento](docs/evidencias/2026-10-15/modelo-mexico-enif.md).

El código se organiza en `nexocredit/`. Esta instalación conserva Compose `plurione-docker` y su volumen para no perder datos; la copia pública de entrega usa `nexocredit-demo` y no comparte su configuración privada. Empezar por el [README de la raíz](../README.md), con operación, recorrido de cuatro pasos, procedencia y declaración de uso de IA. El historial detallado de cambios se encuentra en [BITACORA.md](docs/BITACORA.md).

NexoCredit es una marca demostrativa, no una razón social ni una aprobación empresarial. Se conservan los identificadores de esquema/modelos y los recursos Azure históricos; cambiar el nombre del proyecto Compose no migra su volumen ni su configuración privada.

Accesos de Windows: [operacion](operacion/README.md). Documentación: [índice](docs/README.md), [PRD](docs/producto/PRD_NEXOCREDIT.md) y [MVP](docs/producto/MVP_NEXOCREDIT.md). Para una vista limpia en VS Code, abrir [NexoCredit.code-workspace](../NexoCredit.code-workspace) desde la raíz exterior.

## Tecnologías obligatorias

Python, FastAPI, React.js, Azure OpenAI Service, Azure Machine Learning, Azure AI Search, PostgreSQL, Power BI, Docker, GitHub Actions, Microsoft Entra ID, APIs financieras y Scrum. Consultar [función, ubicación y estado de cada tecnología](REQUISITOS_TECNOLOGICOS.md). El uso técnico de estas herramientas no acredita producción ni ejecución de Scrum por sí solo.

**Azure sí está implementado en la demo**: OpenAI, Machine Learning, AI Search y acceso Microsoft Entra conservan su código y evidencias reales del 04/10/2026. La alternativa local no los elimina. Los campos para sus keys se mantienen en el `.env` privado de Docker y en las plantillas sin secretos. [Implementación Azure y dónde colocar las llaves](docs/manuales/AZURE_IMPLEMENTADO_Y_CONFIGURACION.md). Esto no afirma vigencia de la suscripción o conectividad cloud actual.

Para el historial fechado de incrementos, revisiones y evidencias históricas, consultar [BITACORA.md](docs/BITACORA.md).

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

Desde la carpeta interior `nexocredit`, que contiene `backend`, `frontend` y `scripts`:

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

Las mismas pruebas que ejecuta [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). La suite completa aislada se ejecuta con `operacion/pruebas/Probar programacion.cmd`: PostgreSQL temporal sin datos de trabajo y limpieza protegida de su propio contenedor.

```powershell
# Backend — 247 pruebas esperadas (API, PostgreSQL, integraciones, validación)
python -m unittest discover -s backend/tests -v

# Frontend — 168 pruebas esperadas
cd frontend
npm test

# Lint y compilación
npm run lint
npm run build
```

`operacion/respaldos/Respaldar PostgreSQL.cmd` y `operacion/respaldos/Probar restauracion PostgreSQL.cmd` permiten el respaldo manual privado y un ensayo aislado; el ensayo de doce tablas pasó el 15/10/2026. El dump no está cifrado ni incluye roles globales/ACL. No restaura sobre la base original ni acredita recuperación productiva completa.

Ejemplo ficticio: AAAA010101AA1, ingreso 30000, gastos 10000, score 700. Resultado esperado: margen 20000, riesgo preliminar Bajo. Es una regla de demostración, no una probabilidad calibrada.

## Entregables

Empezar por [ENTREGA_DEMO.md](docs/entrega/ENTREGA_DEMO.md): alcance comprobado, evidencias, guion de revisión y pendientes. Consultar [plan](docs/planificacion/PLAN_PROYECTO.md), [manual](docs/manuales/OPERACION.md), [QA](docs/calidad/QA.md), [índice de evidencias](docs/evidencias/README.md), [BITACORA.md](docs/BITACORA.md) y [backlog de cierre](gestion_proyecto/scrum/BACKLOG_CIERRE.md). El cronograma de 500 horas es propuesto, no horas acreditadas; no hay aceptación del asesor ni sprints certificados.

## Organización de carpetas

```text
nexocredit/                                Raíz del proyecto (carpeta interior)
├── backend/                                Python + FastAPI
│   ├── app/
│   │   ├── main.py                         Entrada de la API
│   │   ├── rutas_api/                      Endpoints HTTP protegidos
│   │   ├── validacion_datos/               Validación de solicitudes y esquemas Pydantic
│   │   ├── evaluacion_crediticia/          Reglas de riesgo actuales (v2)
│   │   ├── seguimiento_crediticio/         Planes, cuotas, pagos y auditoría
│   │   ├── persistencia_postgresql/        Guardado, historial y migraciones
│   │   ├── autenticacion_entra_id/         Identidad Entra y acceso delegado
│   │   ├── autenticacion_local/            Acceso local por usuario y contraseña
│   │   └── integraciones/                 Adaptadores Azure, locales y financieros
│   │       ├── explicaciones_azure_openai/ Explicación automática post-evaluación
│   │       ├── prediccion_azure_ml/        Cliente remoto de inferencia Azure ML
│   │       ├── prediccion_local/           Inferencia UCI numérica local (scikit-learn)
│   │       ├── prediccion_mexico/          Inferencia local ENIF 2024 conectada al flujo principal
│   │       ├── busqueda_azure_ai_search/   Búsqueda documental en Azure
│   │       ├── proveedores_locales/        Ollama y búsqueda documental local
│   │       └── datos_financieros/          Indicadores Banxico y Banco Mundial
│   └── tests/                             Pruebas automatizadas backend (247 pruebas)
├── frontend/                              React.js + Vite
│   └── src/
│       ├── autenticacion/                 MSAL y login local
│       ├── evaluacion_crediticia/         Formulario, modelo mexicano y resultado
│       ├── seguimiento_crediticio/        Planes, pagos y eventos
│       ├── dashboard/                     Métricas agregadas y filtros
│       ├── datos_financieros/             Panel de indicadores macroeconómicos
│       ├── azure_ml/                      Laboratorio de predicción UCI
│       ├── azure_openai/                  Visualización de explicaciones IA
│       ├── azure_search/                  Búsqueda y visualización de guías
│       ├── interfaz/                      Componentes comunes, navegación y diseño
│       └── styles/                        Estilos compartidos
├── inteligencia_artificial/
│   ├── prediccion_azure_ml/                Candidato UCI evaluado en Azure ML
│   ├── prediccion_local/                   Baseline scikit-learn UCI reproducible
│   └── prediccion_mexico/                  Modelo ENIF 2024: código, entrenamiento y métricas
├── analitica/reportes_power_bi/            Dashboard Power BI local verificado (11 visuales)
├── infraestructura/contenedores_docker/    Dockerfiles, Compose, Nginx y base persistente
├── gestion_proyecto/scrum/                Backlog de cierre; sprints aún por acreditar
├── docs/                                  Índice de documentación
│   ├── BITACORA.md                        Historial fechado de incrementos y cambios
│   ├── producto/                          PRD y MVP separados
│   ├── planificacion/                     Plan del proyecto
│   ├── manuales/                          Operación, soporte y reglas de riesgo
│   ├── calidad/                           QA y reportes de pruebas
│   ├── entrega/                           Guion y alcance de entrega
│   ├── desarrollo/                        Arquitectura, datos y CI
│   ├── evidencias/                        Registros fechados de comprobaciones
│   ├── estadia/                           Información académica
│   └── archivo/                           Originales conservados
├── operacion/                             Accesos .cmd para Windows
│   ├── aplicacion/                        Abrir, actualizar y detener
│   ├── integraciones/                     Conexiones Azure/Banxico y carga documental
│   ├── pruebas/                           Suite aislada
│   └── respaldos/                         Respaldo y ensayo de restauración
├── scripts/                               Implementación Python/PowerShell y pruebas
└── REQUISITOS_TECNOLOGICOS.md              Tecnologías obligatorias y estado
```

El workflow está en `.github/workflows/ci.yml` de la raíz Git exterior, no dentro de esta carpeta. Las carpetas generadas, .local, .venv, .venv-roto y el archivo histórico se ocultan en VS Code; siguen en disco. No se movieron datos, secretos, entornos virtuales o proyectos Power BI privados. Ver el [mapa del espacio de trabajo](../README.md).

## Laboratorio UCI / Azure ML

Formulario académico separado de 19 variables UCI y cliente remoto FastAPI conectados al endpoint Azure existente. La consulta real autenticada del 04/10/2026 devolvió una clase booleana; el aviso distingue espera, éxito y fallo del último intento. No persiste el escenario UCI, no carga el pickle en el backend y no convierte MXN a NTD. El formulario principal integra el modelo mexicano ENIF 2024 y reglas demo v2 para comparación; este laboratorio permanece como espacio académico separado para el dataset UCI de 19 variables. La etiqueta `modelo_configurado` no verifica la versión remota. Una lectura independiente de metadatos Azure ML Studio comprobó ese día el modelo registrado servido `plurione-uci-voting-candidato:1`, aprovisionamiento correcto y tráfico directo 100 %. La comparación binaria con el artefacto local y la aptitud para población real siguen pendientes. Consultar [contrato, configuración y límites](backend/app/integraciones/prediccion_azure_ml/README.md).
