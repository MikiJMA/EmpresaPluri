# Persistencia PostgreSQL

Primera etapa funcional: solicitud y resultado juntos, fecha UTC, versión del modelo e identificador UUID. No incluye todavía expediente de pagos o deudas.

## Organización

- conexion.py: lee DATABASE_URL del proceso o de backend/.env.postgresql.
- repositorio.py: transacciones, idempotencia, historial y detalle con parámetros SQL.
- explicaciones.py: caché privada, exclusión de generaciones concurrentes y cuotas por cuenta con PostgreSQL.
- migrar.py y migraciones/: cambios de esquema versionados, ejecutados explícitamente.
- scripts/postgresql_local.py (desde la raíz): prepara y administra la instancia local.

## Preparación y operación

Instalar backend/requirements.txt en .venv. Desde la raíz interior ejecutar `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\postgresql-local.ps1 preparar`. Descarga los binarios oficiales de PostgreSQL 17.11, crea credenciales aleatorias y una cuenta de aplicación sin privilegios de superusuario. Escucha solo en 127.0.0.1:55432. Conserva la configuración existente; no instala un servicio de Windows.

Las acciones iniciar, detener y estado permiten administrar únicamente esta instancia. El lanzador iniciar-backend.ps1 la inicia si está preparada. Los datos quedan en .local/postgresql/datos y las credenciales en .local/postgresql/credenciales.json y backend/.env.postgresql; están excluidos de Git. No borrar ni compartir estas carpetas.

Para una instancia externa, definir DATABASE_URL (backend/.env.example) y ejecutar `.\.venv\Scripts\python.exe -m backend.app.persistencia_postgresql.migrar`. Revisar el destino antes de aplicar migraciones.

## API

- POST /api/v1/evaluar: conserva los campos previos y añade guardado, id y fecha al persistir. Idempotency-Key admite un UUID; repetir clave y datos devuelve el registro anterior; cambiar los datos con la misma clave devuelve 409.
- GET /api/v1/evaluaciones?limite=10&offset=0: items, hay_mas, limite y offset. Máximo 100 por página y offset entre 0 y 1.000.000; orden descendente de fecha e ID.
- GET /api/v1/evaluaciones/{id}: resultado y solicitud original, o 404.
- Sin configuración: POST funciona con guardado=false; historial devuelve 503.
- Con base configurada pero inaccesible o sin esquema: 503, sin exponer credenciales.

La paginación por desplazamiento puede variar si entran registros entre páginas. Actualizar vuelve a la primera página. Las rutas requieren Microsoft Entra ID o una sesión local habilitada. Los roles autorizados comparten los registros de la demo; no hay expedientes privados separados por propietario. Solo escenarios ficticios.

## Pruebas reales

Definir `$env:RUN_POSTGRES_TESTS='1'` y ejecutar `.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v`. Crean un esquema test_UUID, aplican migraciones y verifican persistencia, idempotencia, conflicto, paginación y rollback. Al terminar borran únicamente ese esquema de prueba; no escriben en public.evaluaciones.

Hay respaldo manual y ensayo aislado de restauración; no respaldo programado ni recuperación productiva completa. La migración 004 añade límites de acceso y dos tablas de caché/cuota de explicaciones sin reescribir las evaluaciones. La caché conserva texto privado: su vencimiento limita reutilización, no lo elimina automáticamente. No usar esta demo con expedientes reales.

Desde la segunda corrección del 11/10/2026, el contador de intento se confirma antes de invocar el proveedor; una excepción inesperada o rollback posterior no lo borra. Los locks de sesión mantienen la exclusión por evaluación/clave y por cuenta durante ambos commits. Se usan conexiones dedicadas que se cierran al salir: no cambiar a un pool sin adaptar la liberación de estos locks. Los errores inesperados de generación se convierten en 503 saneado y se cachean un minuto; no hay reintento automático. Una interrupción todavía puede perder el texto generado, pero conserva el intento si su reserva ya se confirmó. Una reserva puede consumirse aunque el proveedor no llegara a cobrar.

## Fuentes técnicas

La migración 005 añade seguimiento ficticio (creditos_demo, cuotas_demo, pagos_demo, alertas_credito_demo, eventos_seguimiento_demo) sin convertir evaluaciones anteriores ni modificar cuentas. Un plan por evaluación, dinero NUMERIC/Decimal, bloqueo por crédito, movimientos/eventos atómicos. [Diccionario de las doce tablas](../../../docs/desarrollo/ARQUITECTURA_Y_DATOS.md), [manual y límites](../../../docs/manuales/SEGUIMIENTO_CREDITICIO.md). La vista Power BI existente no se amplía automáticamente con pagos.

- https://www.postgresql.org/download/windows/
- https://www.psycopg.org/psycopg3/docs/basic/transactions.html
