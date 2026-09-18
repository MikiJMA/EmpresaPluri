# Operación y soporte — versión inicial

## Manual de usuario del prototipo

1. Iniciar backend e interfaz siguiendo README.md.
2. Abrir la interfaz y usar exclusivamente escenarios ficticios.
3. Capturar RFC o identificador de formato libre (campo obligatorio), ingresos mayores a cero, gastos no negativos y score entero entre 0 y 1000 (escala ilustrativa pendiente de proveedor).
4. Pulsar Evaluar escenario. Consultar margen y factores. El nivel mostrado depende exclusivamente de las reglas demo.
5. Con PostgreSQL configurado, cada evaluación guarda entradas, resultado, fecha y versión; el historial permanece al recargar. Cambiar un dato limpia el resultado del formulario, pero conserva lo guardado. Sin base configurada se indica expresamente que no se guardó.
6. Si PostgreSQL no está disponible, se muestra un error de guardado. Iniciar scripts/postgresql-local.ps1 iniciar y reintentar. Reenviar el mismo formulario conserva la clave de reintento durante la sesión para evitar duplicados; editar un campo inicia otra solicitud.

El campo RFC acepta texto libre; no valida estructura, identidad ni registro fiscal. Si aparece un error de conexión, verificar proceso FastAPI, puerto 8000 y VITE_API_URL. Si aparece error de validación, revisar datos. Si Vite usa otro puerto, agregar su origen exacto a CORS_ORIGINS y reiniciar backend.

## Manual técnico

Alternativa Docker: abrir Docker Desktop y ejecutar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar` desde la carpeta interior. Abrir http://127.0.0.1:8080/; no requiere iniciar Vite ni FastAPI por separado. Las acciones `estado`, `logs` y `pruebas` permiten diagnóstico. `detener` conserva el volumen de datos. Esta base es independiente de la local; ver ../infraestructura/contenedores_docker/README.md. En este entorno, ante un fallo de base, revisar los servicios Docker en vez de iniciar postgresql-local.ps1.

frontend/src/App.jsx coordina la pantalla; frontend/src/evaluacion_crediticia/componentes contiene formulario y resultado; frontend/src/evaluacion_crediticia/servicios/creditApi.js realiza las peticiones; frontend/src/main.jsx inicia React. backend/app/main.py configura la API; rutas_api/routes.py define rutas, validacion_datos/credito.py valida entradas y evaluacion_crediticia/scoring.py evalúa las reglas. Configuración: frontend/.env.example y variable CORS_ORIGINS. GET / comprueba disponibilidad; POST /api/v1/evaluar ejecuta reglas; /docs permite inspeccionar el contrato. backend/requirements.txt declara dependencias Python; frontend/package-lock.json fija las dependencias JavaScript. Aún falta fijar dependencias Python exactas para despliegue reproducible.

## Plan de mantenimiento propuesto

Nivel 1: asistencia de captura, conectividad y registro de incidentes sin información sensible. Nivel 2: diagnóstico de API, base de datos e integraciones. Nivel 3: correcciones de código/modelo, seguridad y escalamiento a proveedores. Personas y tiempos de atención pendientes de asignación con PluriOne.

Antes de producción: definir respaldos, retención, objetivos de recuperación y ejercicios de restauración; monitorear disponibilidad, errores, latencia y deriva del modelo; documentar rollback; revisar dependencias y permisos periódicamente. Ninguno de estos mecanismos está implementado en la demo.

Plantilla de incidente: ID, fecha, entorno, impacto, pasos de reproducción con datos ficticios, responsable, diagnóstico, solución, validación y cierre.

## Capacitación propuesta y acta pendiente

Agenda: alcance/limitaciones, captura, interpretación, revisión humana, acceso y reporte de incidentes. Práctica: tres escenarios ficticios y un caso inválido. Evidencia: asistencia, ejercicios y dudas resueltas.

Acta por completar tras la sesión: fecha, instructor, asistentes, versión utilizada, ejercicios, resultados, observaciones y conformidad. Capacitación aún no realizada.

