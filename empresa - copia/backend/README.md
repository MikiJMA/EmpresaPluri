# Backend

FastAPI y reglas de evaluación. Ejecutar desde la raíz de empresa:

```powershell
.\scripts\iniciar-backend.ps1
```

- app/main.py: crea y configura FastAPI.
- app/rutas_api/routes.py: define los endpoints.
- app/validacion_datos/credito.py: valida las entradas.
- app/evaluacion_crediticia/scoring.py: calcula el resultado demo.
- tests/: pruebas de API y reglas.
- requirements.txt: dependencias de Python.
- app/persistencia_postgresql/: conexión, repositorio y migraciones PostgreSQL.
- .env.postgresql: configuración privada de persistencia cargada automáticamente.
- .env: archivo local conservado de la ubicación anterior; no se carga automáticamente. Las variables actuales se toman del entorno del proceso.

El entorno virtual compartido está en ../.venv. Consultar ../README.md para instalación.
