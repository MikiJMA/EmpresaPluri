"""Ejecutar desde la raíz: python -m backend.app.persistencia_postgresql.migrar."""
from pathlib import Path
from .conexion import conectar, database_url


def migrar():
    if not database_url():
        raise RuntimeError('Configura DATABASE_URL antes de ejecutar las migraciones.')
    with conectar() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(72618401)')
        conn.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, fecha TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)')
        for script in sorted((Path(__file__).parent / 'migraciones').glob('*.sql')):
            if not conn.execute('SELECT 1 FROM schema_migrations WHERE version = %s', (script.name,)).fetchone():
                conn.execute(script.read_text(encoding='utf-8'))
                conn.execute('INSERT INTO schema_migrations(version) VALUES (%s)', (script.name,))


if __name__ == '__main__':
    migrar()
    print('Migraciones PostgreSQL aplicadas correctamente.')
