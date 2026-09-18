# Persistencia PostgreSQL

Primera etapa funcional: solicitud y resultado juntos, fecha UTC, versión del modelo e identificador UUID. No incluye todavía expediente de pagos o deudas.

## Organización

- conexion.py: lee DATABASE_URL del proceso o de backend/.env.postgresql.
- repositorio.py: transacciones, idempotencia, historial y detalle con parámetros SQL.
- migrar.py y migraciones/: cambios de esquema versionados, ejecutados explícitamente.
- scripts/postgresql_local.py (desde la raíz): prepara y administra la instancia local.

## Preparación y operación

Instalar backend/requirements.txt en .venv. Desde la raíz interior ejecutar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\postgresql-local.ps1 preparar`. Descarga los binarios oficiales de PostgreSQL 17.11, crea credenciales aleatorias y una cuenta de aplicación sin privilegios de superusuario. Escucha solo en 127.0.0.1:55432. Conserva la configuración existente; no instala un servicio de Windows.

Las acciones iniciar, detener y estado permiten administrar únicamente esta instancia. El lanzador iniciar-backend.ps1 la inicia si está preparada. Los datos quedan en .local/postgresql/datos y las credenciales en .local/postgresql/credenciales.json y backend/.env.postgresql; están excluidos de Git. No borrar ni compartir estas carpetas.

Para una instancia externa, definir DATABASE_URL (backend/.env.example) y ejecutar `.\.venv\Scripts\python.exe -m backend.app.persistencia_postgresql.migrar`. Revisar el destino antes de aplicar migraciones.

## API

- POST /api/v1/evaluar: conserva los campos previos y añade guardado, id y fecha al persistir. Idempotency-Key admite un UUID; repetir clave y datos devuelve el registro anterior; cambiar los datos con la misma clave devuelve 409.
- GET /api/v1/evaluaciones?limite=10&offset=0: items, hay_mas, limite y offset. Máximo 100 por página; orden descendente de fecha e ID.
- GET /api/v1/evaluaciones/{id}: resultado y solicitud original, o 404.
- Sin configuración: POST funciona con guardado=false; historial devuelve 503.
- Con base configurada pero inaccesible o sin esquema: 503, sin exponer credenciales.

La paginación por desplazamiento puede variar si entran registros entre páginas. Actualizar vuelve a la primera página. Todavía no hay autenticación ni separación de usuarios: solo uso local con escenarios ficticios.

## Pruebas reales

Definir `$env:RUN_POSTGRES_TESTS='1'` y ejecutar `.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v`. Crean un esquema test_UUID, aplican migraciones y verifican persistencia, idempotencia, conflicto, paginación y rollback. Al terminar borran únicamente ese esquema de prueba; no escriben en public.evaluaciones.

Respaldos automatizados, recuperación, retención y autorización con Entra ID siguen pendientes.

## Fuentes técnicas

- https://www.postgresql.org/download/windows/
- https://www.psycopg.org/psycopg3/docs/basic/transactions.html
