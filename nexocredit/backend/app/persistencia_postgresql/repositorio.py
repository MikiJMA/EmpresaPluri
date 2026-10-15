"""Guardado transaccional, reintentos idempotentes e historial paginado."""
from psycopg.types.json import Jsonb
from .conexion import conectar, database_url


class ConflictoSolicitud(Exception):
    pass


def registro(row):
    return {**row['resultado'], 'id': str(row['id']), 'fecha': row['fecha'], 'guardado': True}


class RepositorioEvaluaciones:
    def revisar(self, identificador, revision):
        with conectar() as conn:
            if not conn.execute('SELECT id FROM evaluaciones WHERE id = %s FOR UPDATE', (identificador,)).fetchone():
                return None
            previous = conn.execute('SELECT * FROM revisiones WHERE id = %s', (revision.id,)).fetchone()
            if previous:
                if (previous['evaluacion_id'] != identificador or previous['version'] != revision.version_anterior + 1
                        or any(previous[k] != getattr(revision, k) for k in ('estado', 'observaciones', 'responsable'))):
                    raise ConflictoSolicitud()
                return previous
            version = conn.execute('SELECT coalesce(max(version), 0) AS version FROM revisiones WHERE evaluacion_id = %s', (identificador,)).fetchone()['version']
            if version != revision.version_anterior:
                raise ConflictoSolicitud()
            return conn.execute('INSERT INTO revisiones(id,evaluacion_id,version,estado,observaciones,responsable) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *',
                (revision.id, identificador, version + 1, revision.estado, revision.observaciones, revision.responsable)).fetchone()

    def resumen(self, desde=None, hasta=None, riesgo=None):
        with conectar() as conn:
            return conn.execute('''
                SELECT count(*) AS total,
                    count(*) FILTER (WHERE resultado->>'nivel_riesgo_preliminar' = 'Bajo') AS bajo,
                    count(*) FILTER (WHERE resultado->>'nivel_riesgo_preliminar' = 'Medio') AS medio,
                    count(*) FILTER (WHERE resultado->>'nivel_riesgo_preliminar' = 'Alto') AS alto,
                    avg((resultado->>'margen_libre')::numeric) AS margen_promedio,
                    avg((solicitud->>'deuda_actual')::numeric) AS deuda_promedio,
                    count(solicitud->>'deuda_actual') AS con_deuda_capturada
                FROM evaluaciones
                WHERE (%s::date IS NULL OR fecha >= (%s::date::timestamp AT TIME ZONE 'UTC'))
                  AND (%s::date IS NULL OR fecha < ((%s::date + 1)::timestamp AT TIME ZONE 'UTC'))
                  AND (%s::text IS NULL OR resultado->>'nivel_riesgo_preliminar' = %s)
            ''', (desde, desde, hasta, hasta, riesgo, riesgo)).fetchone()

    def guardar(self, identificador, solicitud, resultado):
        with conectar() as conn:
            row = conn.execute(
                'INSERT INTO evaluaciones(id, solicitud, resultado) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING RETURNING *',
                (identificador, Jsonb(solicitud), Jsonb(resultado)),
            ).fetchone()
            if row is None:
                row = conn.execute('SELECT * FROM evaluaciones WHERE id = %s', (identificador,)).fetchone()
                if row['solicitud'] != solicitud:
                    raise ConflictoSolicitud()
            return registro(row)

    def listar(self, limite, offset):
        with conectar() as conn:
            rows = conn.execute('SELECT * FROM evaluaciones ORDER BY fecha DESC, id DESC LIMIT %s OFFSET %s', (limite + 1, offset)).fetchall()
            return {'items': [registro(row) for row in rows[:limite]], 'hay_mas': len(rows) > limite, 'limite': limite, 'offset': offset}

    def obtener(self, identificador):
        with conectar() as conn:
            row = conn.execute('SELECT * FROM evaluaciones WHERE id = %s', (identificador,)).fetchone()
            if not row:
                return None
            revisiones = conn.execute('SELECT * FROM revisiones WHERE evaluacion_id = %s ORDER BY version DESC', (identificador,)).fetchall()
            return {**registro(row), 'solicitud': row['solicitud'], 'revisiones': revisiones,
                    'estado_revision': revisiones[0]['estado'] if revisiones else 'Pendiente',
                    'version_revision': revisiones[0]['version'] if revisiones else 0}


def obtener_repositorio():
    return RepositorioEvaluaciones() if database_url() else None
