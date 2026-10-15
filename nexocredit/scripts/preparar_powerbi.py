"""Configura una vista y un lector local sin imprimir ni publicar credenciales."""
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import psycopg

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local' / 'powerbi' / '.env'
docker = shutil.which('docker') or str(Path(os.environ['LOCALAPPDATA']) / 'Programs/DockerDesktop/resources/bin/docker.exe')

def sql(text):
    result = subprocess.run([docker, 'exec', '-i', 'plurione-docker-postgres-1', 'psql', '-U', 'pluri_admin', '-d', 'pluri_credito', '-v', 'ON_ERROR_STOP=1', '-At'], input=text, text=True, capture_output=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('No se pudo configurar Power BI. Verifica PostgreSQL y sus migraciones; no se muestran detalles para proteger credenciales.')
    return result.stdout.strip()

exists = sql("SELECT count(*) FROM pg_roles WHERE rolname='pluri_powerbi';") == '1'
if PRIVATE.exists():
    values = dict(line.split('=', 1) for line in PRIVATE.read_text().splitlines() if '=' in line)
    password = values['PASSWORD']
elif exists:
    raise RuntimeError('El usuario ya existe pero falta su archivo privado. No se cambia su contraseña automáticamente.')
else:
    password = secrets.token_hex(32)
    PRIVATE.parent.mkdir(parents=True, exist_ok=True)
    with PRIVATE.open('x', encoding='utf-8') as file:
        file.write(f'SERVER=127.0.0.1:55433\nDATABASE=pluri_credito\nUSER=pluri_powerbi\nPASSWORD={password}\n')
if len(password) != 64 or any(c not in '0123456789abcdef' for c in password):
    raise RuntimeError('Formato de credencial privada inesperado.')
create = '' if exists else f"CREATE ROLE pluri_powerbi LOGIN PASSWORD '{password}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;"
view = (ROOT / 'analitica/reportes_power_bi/vista_evaluaciones.sql').read_text(encoding='utf-8')
sql('BEGIN;\n' + create + '\n' + view + '\nCOMMIT;')
try:
    with psycopg.connect(host='127.0.0.1', port=55433, dbname='pluri_credito', user='pluri_powerbi', password=password, connect_timeout=10) as conn:
        count = conn.execute('SELECT count(*) FROM reportes.evaluaciones_powerbi').fetchone()[0]
        for query in ['SELECT * FROM public.evaluaciones LIMIT 0', 'SELECT * FROM public.revisiones LIMIT 0', 'EXPLAIN DELETE FROM public.evaluaciones', 'EXPLAIN UPDATE public.revisiones SET estado=estado']:
            try:
                with conn.transaction():
                    conn.execute(query)
            except psycopg.errors.InsufficientPrivilege:
                pass
            else:
                raise RuntimeError('El lector tiene permisos inesperados.')
except Exception as error:
    raise RuntimeError('No se verificó la conexión/permisos de Power BI: ' + str(error).replace(password, '[oculto]')) from None
print(f'Conexión TCP verificada. Vista de reportes: {count} evaluaciones. Sin acceso a tablas originales ni escritura.')
print('Credenciales conservadas en .local/powerbi/.env; no compartir ni publicar.')
