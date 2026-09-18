"""Instancia PostgreSQL exclusiva del proyecto; no instala servicios de Windows."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local' / 'postgresql'
BIN = LOCAL / 'pgsql' / 'bin'
DATA = LOCAL / 'datos'
CONFIG = ROOT / 'backend' / '.env.postgresql'
SECRETS = LOCAL / 'credenciales.json'
URL = 'https://sbp.enterprisedb.com/getfile.jsp?fileid=1260491'
PORT = '55432'


def run(executable, *args, check=True):
    return subprocess.run([str(BIN / executable), *map(str, args)], check=check,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)


def preparar():
    LOCAL.mkdir(parents=True, exist_ok=True)
    if not (BIN / 'pg_ctl.exe').exists():
        archive = LOCAL / 'postgresql.zip'
        if not archive.exists():
            print('Descargando PostgreSQL desde EDB...')
            urllib.request.urlretrieve(URL, archive)
        with zipfile.ZipFile(archive) as bundle:
            for entry in bundle.infolist():
                if entry.filename.startswith(('pgsql/bin/', 'pgsql/lib/', 'pgsql/share/')):
                    target = (LOCAL / entry.filename).resolve()
                    if not target.is_relative_to(LOCAL.resolve()):
                        raise RuntimeError('Ruta de archivo no válida.')
                    bundle.extract(entry, LOCAL)
    if not SECRETS.exists():
        if DATA.exists():
            raise RuntimeError('Ya hay datos sin credenciales locales. No se modificaron.')
        with SECRETS.open('x', encoding='utf-8') as file:
            json.dump({'admin': secrets.token_urlsafe(32), 'app': secrets.token_urlsafe(32)}, file)
    credentials = json.loads(SECRETS.read_text(encoding='utf-8'))
    if not (DATA / 'PG_VERSION').exists():
        if DATA.exists():
            raise RuntimeError('El directorio de datos ya existe sin PG_VERSION. Revisarlo manualmente.')
        password_file = LOCAL / 'password-init.tmp'
        try:
            password_file.write_text(credentials['admin'], encoding='utf-8')
            run('initdb.exe', '-D', DATA, '-U', 'pluri_admin', '--pwfile', password_file,
                '--auth=scram-sha-256', '--encoding=UTF8', '--locale=C')
        finally:
            password_file.unlink(missing_ok=True)
    iniciar()
    import psycopg
    from psycopg import sql
    with psycopg.connect(host='127.0.0.1', port=PORT, dbname='postgres', user='pluri_admin',
                         password=credentials['admin'], autocommit=True, connect_timeout=5) as conn:
        if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname = 'pluri_app'").fetchone():
            conn.execute(sql.SQL('CREATE ROLE pluri_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD {}').format(sql.Literal(credentials['app'])))
        if not conn.execute("SELECT 1 FROM pg_database WHERE datname = 'pluri_credito'").fetchone():
            conn.execute('CREATE DATABASE pluri_credito OWNER pluri_app')
    if not CONFIG.exists():
        with CONFIG.open('x', encoding='utf-8') as file:
            file.write('DATABASE_URL=postgresql://pluri_app:' + credentials['app'] + '@127.0.0.1:' + PORT + '/pluri_credito\n')
    sys.path.insert(0, str(ROOT))
    from backend.app.persistencia_postgresql.migrar import migrar
    migrar()
    print('PostgreSQL preparado en 127.0.0.1:55432; base pluri_credito. Configuración privada en backend/.env.postgresql.')


def iniciar():
    if not (DATA / 'PG_VERSION').exists():
        raise RuntimeError('Ejecuta primero la acción preparar.')
    if run('pg_ctl.exe', '-D', DATA, 'status', check=False).returncode != 0:
        run('pg_ctl.exe', '-D', DATA, '-l', LOCAL / 'postgresql.log', '-o', '-h 127.0.0.1 -p ' + PORT, '-w', 'start')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=['preparar', 'iniciar', 'detener', 'estado'])
    action = parser.parse_args().accion
    if action == 'preparar': preparar()
    elif action == 'iniciar': iniciar()
    elif action == 'detener': run('pg_ctl.exe', '-D', DATA, '-m', 'fast', '-w', 'stop')
    else: sys.exit(run('pg_ctl.exe', '-D', DATA, 'status', check=False).returncode)
