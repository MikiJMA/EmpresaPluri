"""Guardado transaccional, reintentos idempotentes e historial paginado."""
from psycopg.types.json import Jsonb
from .conexion import conectar, database_url


class ConflictoSolicitud(Exception):
    pass


def registro(row):
    return {**row['resultado'], 'id': str(row['id']), 'fecha': row['fecha'], 'guardado': True}


class RepositorioEvaluaciones:
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
            return {**registro(row), 'solicitud': row['solicitud']} if row else None


def obtener_repositorio():
    return RepositorioEvaluaciones() if database_url() else None
