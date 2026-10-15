"""Respaldo de la demo y ensayo aislado; nunca restaura sobre la base original.

pg_dump usa la instantanea exportada de la misma transaccion de lectura que
las huellas. El archivo privado contiene esquema/datos, no roles ni ACL.
Referencia: https://www.postgresql.org/docs/17/app-pgdump.html
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4

import psycopg
from dotenv import dotenv_values

PROJECT = Path(__file__).resolve().parents[1]
BACKUPS = PROJECT / '.local' / 'respaldos_postgresql'
SOURCE = 'plurione-docker-postgres-1'
DATABASE = 'pluri_credito'
TEST_LABEL = 'io.plurione.restore-test'


class BackupError(Exception):
    """Mensajes propios: nunca reutilizar stderr ni errores de conexion."""


def run(arguments, *, stdin=None, stdout=None, timeout=180, allowed=(0,)):
    try:
        result = subprocess.run(arguments, stdin=stdin, stdout=stdout or subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise BackupError('No se pudo completar un comando local dentro del tiempo permitido.') from None
    if result.returncode not in allowed:
        raise BackupError('Un comando local fallo. No se mostraron sus datos privados.')
    return result


def docker_executable():
    candidates = [shutil.which('docker'),
                  str(Path(os.getenv('LOCALAPPDATA', '')) / 'Programs/DockerDesktop/resources/bin/docker.exe'),
                  'C:/Program Files/Docker/Docker/resources/bin/docker.exe']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise BackupError('No se encontro Docker Desktop.')


def inspect_value(docker, container, template):
    return run([docker, 'inspect', '--format', template, container], timeout=15).stdout.decode().strip()


def source_identity(docker):
    project = inspect_value(docker, SOURCE, '{{index .Config.Labels "com.docker.compose.project"}}')
    service = inspect_value(docker, SOURCE, '{{index .Config.Labels "com.docker.compose.service"}}')
    port = inspect_value(docker, SOURCE, '{{json (index .NetworkSettings.Ports "5432/tcp")}}')
    if project != 'plurione-docker' or service != 'postgres':
        raise BackupError('El contenedor no pertenece al PostgreSQL de esta demostracion.')
    if json.loads(port) != [{'HostIp': '127.0.0.1', 'HostPort': '55433'}]:
        raise BackupError('El puerto PostgreSQL no coincide con el destino local esperado.')
    if inspect_value(docker, SOURCE, '{{.State.Running}}') != 'true':
        raise BackupError('PostgreSQL no esta iniciado; no se reiniciara automaticamente.')
    return {'container': inspect_value(docker, SOURCE, '{{.Id}}'),
            'image': inspect_value(docker, SOURCE, '{{.Image}}')}


def private_directory(path):
    if path.resolve() != path.absolute():
        raise BackupError('No se permiten enlaces en los padres del directorio privado.')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
        raise BackupError('No se permiten enlaces en la carpeta de respaldos.')
    if os.name == 'nt':
        account = run(['whoami', '/user', '/fo', 'csv', '/nh'], timeout=10).stdout.decode(errors='replace')
        sid = re.search(r'S-1-5-\d+(?:-\d+)+', account)
        if not sid:
            raise BackupError('No se pudo identificar al propietario del respaldo.')
        run(['icacls', str(path), '/inheritance:r', '/grant:r',
             f'*{sid.group()}:(OI)(CI)F', '*S-1-5-18:(OI)(CI)F'], timeout=15)
    else:
        path.chmod(0o700)


def validate_backup_path(path, base=None):
    base_path = base or BACKUPS
    if base_path.resolve() != base_path.absolute():
        raise BackupError('La carpeta privada no puede redirigir a otro destino.')
    base = base_path.resolve()
    path = Path(path)
    if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
        raise BackupError('El respaldo no puede ser un enlace.')
    resolved = path.resolve()
    if resolved.parent != base or resolved == base:
        raise BackupError('El respaldo debe ser una carpeta directa del directorio privado del proyecto.')
    return resolved


def quote_identifier(value):
    return '"' + value.replace('"', '""') + '"'


def quote_literal(value):
    return "'" + value.replace("'", "''") + "'"


CATALOG_SQL = """
SELECT n.nspname, c.relname FROM pg_catalog.pg_class c
JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
WHERE c.relkind IN ('r','p','m') AND left(n.nspname,3) <> 'pg_'
AND n.nspname <> 'information_schema' ORDER BY n.nspname,c.relname
"""


def fingerprint_query(tables):
    parts = []
    for schema, table in tables:
        target = quote_identifier(schema) + '.' + quote_identifier(table)
        name = quote_literal(schema + '.' + table)
        parts.append(f"""SELECT {name} AS nombre, count(*) AS filas,
          md5(coalesce(string_agg(md5(to_jsonb(t)::text), '' ORDER BY md5(to_jsonb(t)::text)), '')) AS huella
          FROM ONLY {target} t""")
    rows = ' UNION ALL '.join(parts) if parts else "SELECT ''::text nombre, 0::bigint filas, ''::text huella WHERE false"
    return f"""
WITH filas AS ({rows}), tablas AS ({CATALOG_SQL})
SELECT jsonb_build_object(
 'inventario', coalesce((SELECT jsonb_agg(jsonb_build_array(nspname,relname) ORDER BY nspname,relname) FROM tablas),'[]'::jsonb),
 'datos', coalesce((SELECT jsonb_agg(to_jsonb(f) ORDER BY nombre) FROM filas f),'[]'::jsonb),
 'columnas', coalesce((SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,a.attname,
   pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,pg_catalog.pg_get_expr(d.adbin,d.adrelid),a.attidentity,a.attgenerated)
   ORDER BY n.nspname,c.relname,a.attnum)
   FROM pg_catalog.pg_attribute a JOIN pg_catalog.pg_class c ON c.oid=a.attrelid
   JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
   LEFT JOIN pg_catalog.pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum
   WHERE c.relkind IN ('r','p','m','v') AND a.attnum>0 AND NOT a.attisdropped
   AND left(n.nspname,3)<>'pg_' AND n.nspname<>'information_schema'),'[]'::jsonb),
 'restricciones', coalesce((SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,k.conname,
   pg_catalog.pg_get_constraintdef(k.oid,true)) ORDER BY n.nspname,c.relname,k.conname)
   FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid
   JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
   WHERE left(n.nspname,3)<>'pg_' AND n.nspname<>'information_schema'),'[]'::jsonb),
 'vistas', coalesce((SELECT jsonb_agg(jsonb_build_array(n.nspname,c.relname,pg_catalog.pg_get_viewdef(c.oid,true))
   ORDER BY n.nspname,c.relname) FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
   WHERE c.relkind IN ('v','m') AND left(n.nspname,3)<>'pg_' AND n.nspname<>'information_schema'),'[]'::jsonb))
"""


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_new(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    if os.name != 'nt':
        path.chmod(0o600)


def create_backup(docker):
    identity = source_identity(docker)
    env_path = PROJECT / 'infraestructura/contenedores_docker/.env'
    password = dotenv_values(env_path, interpolate=False).get('POSTGRES_ADMIN_PASSWORD')
    if not password:
        raise BackupError('Falta la configuracion privada de PostgreSQL.')
    run(['git', '-C', str(PROJECT), 'check-ignore', '--quiet', '--no-index', str(BACKUPS / 'privado.dump')], timeout=10)
    private_directory(BACKUPS)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    directory = validate_backup_path(BACKUPS / (stamp + '-' + uuid4().hex[:12]))
    private_directory(directory)
    # Conexion exclusivamente loopback; ni password ni errores libpq se imprimen.
    with psycopg.connect(host='127.0.0.1', port=55433, dbname=DATABASE,
                         user='pluri_admin', password=password, connect_timeout=5) as conn:
        conn.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        conn.execute("SET LOCAL statement_timeout='30s'")
        conn.execute("SET LOCAL TIME ZONE 'UTC'")
        conn.execute('SET LOCAL search_path=pg_catalog')
        snapshot = conn.execute('SELECT pg_export_snapshot()').fetchone()[0]
        tables = conn.execute(CATALOG_SQL).fetchall()
        fingerprints = conn.execute(fingerprint_query(tables)).fetchone()[0]
        archive = directory / 'base.dump'
        with archive.open('xb') as stream:
            run([docker, 'exec', SOURCE, 'pg_dump', '-U', 'pluri_admin', '-d', DATABASE,
                 '--format=custom', '--no-owner', '--no-acl', '--lock-wait-timeout=10000',
                 '--snapshot=' + snapshot], stdout=stream)
            stream.flush()
            os.fsync(stream.fileno())
        with archive.open('rb') as stream:
            if archive.stat().st_size < 5 or stream.read(5) != b'PGDMP':
                raise BackupError('El archivo no es un respaldo PostgreSQL completo.')
        if source_identity(docker) != identity:
            raise BackupError('El contenedor original cambio durante el respaldo.')
        conn.rollback()
    manifest = {'format': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'database': DATABASE, 'source': identity, 'archive': 'base.dump',
                'sha256': sha256_file(archive), 'fingerprints': fingerprints,
                'limits': 'Sin cifrado; sin roles globales ni ACL; ensayo solo en destino aislado.'}
    write_json_new(directory / 'manifest.json', manifest)
    return directory, manifest


def read_backup(directory):
    directory = validate_backup_path(directory)
    manifest_path, archive = directory / 'manifest.json', directory / 'base.dump'
    if manifest_path.is_symlink() or archive.is_symlink() or not manifest_path.is_file() or not archive.is_file():
        raise BackupError('Falta el respaldo o el manifiesto; no se permiten enlaces.')
    if manifest_path.stat().st_size > 1024 * 1024:
        raise BackupError('El manifiesto excede el limite esperado.')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if (manifest.get('format') != 1 or manifest.get('database') != DATABASE or manifest.get('archive') != 'base.dump'
            or not re.fullmatch(r'sha256:[0-9a-f]{64}', manifest.get('source', {}).get('image', ''))
            or not re.fullmatch(r'[0-9a-f]{64}', manifest.get('source', {}).get('container', ''))
            or not re.fullmatch(r'[0-9a-f]{64}', manifest.get('sha256', ''))):
        raise BackupError('El manifiesto no tiene el formato esperado.')
    if sha256_file(archive) != manifest['sha256']:
        raise BackupError('La integridad SHA-256 fallo. No se restaurara el archivo.')
    tables = manifest.get('fingerprints', {}).get('inventario')
    if (not isinstance(tables, list) or len(tables) > 1000
            or any(not isinstance(row, list) or len(row) != 2
                   or any(not isinstance(part, str) or not part or '\x00' in part for part in row) for row in tables)):
        raise BackupError('El inventario del respaldo no es valido.')
    return directory, manifest


def cleanup_test_container(docker, container, marker, source):
    if (not re.fullmatch(r'[0-9a-f]{64}', container) or container == source
            or inspect_value(docker, container, '{{index .Config.Labels "' + TEST_LABEL + '"}}') != marker):
        raise BackupError('No se elimino un contenedor cuyo origen no pudo comprobarse.')
    run([docker, 'rm', '--force', '--volumes', container], timeout=30)


def restore_test(docker, directory):
    directory, manifest = read_backup(directory)
    identity_before = source_identity(docker)
    marker = uuid4().hex
    name = 'plurione-restauracion-' + marker
    container = ''
    started = time.monotonic()
    try:
        container = run([docker, 'run', '--detach', '--pull=never', '--network=none', '--name', name,
                         '--label', TEST_LABEL + '=' + marker, '--memory=512m', '--cpus=1',
                         '--security-opt=no-new-privileges:true', '--tmpfs', '/var/lib/postgresql/data:rw,nosuid,noexec,size=256m',
                         '--env', 'POSTGRES_USER=pluri_restore', '--env', 'POSTGRES_DB=pluri_restore',
                         '--env', 'POSTGRES_HOST_AUTH_METHOD=trust', manifest['source']['image']], timeout=30).stdout.decode().strip()
        if not re.fullmatch(r'[0-9a-f]{64}', container) or container == identity_before['container']:
            raise BackupError('El destino temporal no es valido.')
        if (inspect_value(docker, container, '{{.HostConfig.NetworkMode}}') != 'none'
                or inspect_value(docker, container, '{{json .HostConfig.PortBindings}}') not in ('{}', 'null')
                or inspect_value(docker, container, '{{json .HostConfig.Binds}}') not in ('[]', 'null')):
            raise BackupError('El contenedor temporal no esta aislado como se esperaba.')
        for _ in range(60):
            ready = run([docker, 'exec', container, 'pg_isready', '-U', 'pluri_restore', '-d', 'pluri_restore'],
                        timeout=5, allowed=(0, 1, 2))
            if ready.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise BackupError('El PostgreSQL temporal no pudo iniciar.')
        with (directory / 'base.dump').open('rb') as stream:
            run([docker, 'exec', '-i', container, 'pg_restore', '-U', 'pluri_restore', '-d', 'pluri_restore',
                 '--exit-on-error', '--single-transaction', '--no-owner', '--no-acl'], stdin=stream, timeout=300)
        query = "BEGIN READ ONLY; SET LOCAL statement_timeout='30s'; SET LOCAL TIME ZONE 'UTC'; SET LOCAL search_path=pg_catalog; "
        query += fingerprint_query(manifest['fingerprints']['inventario']) + '; ROLLBACK;'
        result = run([docker, 'exec', container, 'psql', '-X', '-q', '-A', '-t', '-v', 'ON_ERROR_STOP=1',
                      '-U', 'pluri_restore', '-d', 'pluri_restore', '-c', query], timeout=90)
        if json.loads(result.stdout) != manifest['fingerprints']:
            raise BackupError('La restauracion no coincide en filas, huellas, columnas, restricciones o vistas.')
        if source_identity(docker) != identity_before:
            raise BackupError('La identidad de la base principal cambio durante la prueba.')
    finally:
        if container:
            cleanup_test_container(docker, container, marker, identity_before['container'])
    report = {'format': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'success': True,
              'archive_sha256': manifest['sha256'], 'seconds': round(time.monotonic() - started, 3),
              'checks': ['datos', 'columnas', 'restricciones', 'vistas', 'origen_conservado', 'temporal_eliminado'],
              'tables': len(manifest['fingerprints']['inventario'])}
    write_json_new(directory / ('restauracion-' + uuid4().hex[:12] + '.json'), report)
    return report


def main():
    parser = argparse.ArgumentParser(description='Respaldo privado y restauracion de prueba aislada. Nunca escribe en la base principal.')
    parser.add_argument('accion', choices=['crear', 'probar'])
    parser.add_argument('--respaldo', type=Path, help='Carpeta de un respaldo anterior; solo para probar.')
    args = parser.parse_args()
    if args.accion == 'crear' and args.respaldo:
        parser.error('--respaldo solo corresponde a probar')
    try:
        print('Respaldo privado sin cifrado: no compartir. Roles y ACL no incluidos.', flush=True)
        docker = docker_executable()
        directory = args.respaldo
        if directory is None:
            directory, _ = create_backup(docker)
            print('Respaldo creado: ' + str(directory), flush=True)
        if args.accion == 'probar':
            report = restore_test(docker, directory)
            print(f"Restauracion aislada aprobada: {report['tables']} tablas; filas, huellas, columnas, restricciones y vistas coincidentes. Temporal eliminado.", flush=True)
        return 0
    except BackupError as error:
        print(str(error), file=sys.stderr)
    except Exception:
        print('No se completo la operacion. No se modifico la base principal ni se expusieron errores privados.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
