"""Crear una copia ZIP pública y local; no iniciar servicios ni leer configuración privada.

El manifiesto es externo: puede incluir la huella del ZIP sin referencia circular.
Las rutas privadas se excluyen antes de recorrerlas/abrirlas. La allowlist no
certifica que alguien no haya pegado un secreto en un archivo de código público:
la revisión humana del paquete sigue siendo necesaria antes de compartirlo.
"""
import argparse
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile


WRAPPER = 'NexoCredit'
PROJECT_DIR = 'empresa - copia'
EXTENSIONS = frozenset({
    '.py', '.ps1', '.cmd', '.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx',
    '.html', '.css', '.md', '.txt', '.json', '.sql', '.yml', '.yaml',
    '.toml', '.tmdl', '.pbip', '.pbism', '.pbir',
})
SPECIAL_FILES = frozenset({'.env.example', '.gitignore', '.dockerignore', '.gitattributes', 'mltable'})
PRUNED_DIRS = frozenset({
    '.git', '.vscode', '.pbi', '.local', '.tmp', '.venv', '.venv-roto',
    '.cache', '.pytest_cache', '.ruff_cache', '.mypy_cache', '.azure', '.aws',
    '.agents', '.codex', '__pycache__', 'node_modules', 'dist', 'output',
    'privado', 'privados', 'private', 'capturas', 'screenshots',
    'revisiones_visuales', 'estadia', 'dumps', 'backups', 'backup', 'respaldos_postgresql',
})
BACKGROUND = PurePosixPath('frontend/public/images/nexocredit-background-v1.png')
PLAN = PurePosixPath('docs/planificacion/PLAN_PROYECTO.md')
ALUMNO = PurePosixPath('docs/estadia/ALUMNO.md')
MAX_FILE_BYTES = 25 * 1024 * 1024
REPARSE_POINT = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
REQUIRED_PROJECT = frozenset({
    'README.md', 'REQUISITOS_TECNOLOGICOS.md', 'backend/requirements.txt',
    'backend/app/main.py', 'frontend/package.json', 'frontend/package-lock.json',
    'frontend/src/App.jsx', 'frontend/src/main.jsx',
    'infraestructura/contenedores_docker/docker-compose.yml',
    'infraestructura/contenedores_docker/backend.Dockerfile',
    'infraestructura/contenedores_docker/frontend.Dockerfile',
    'infraestructura/contenedores_docker/.env.example',
    'scripts/docker.ps1', 'scripts/modo-local.ps1', 'scripts/crear_usuario_local.py',
    'backend/app/integraciones/prediccion_local/artefactos/modelo.json',
    'backend/app/integraciones/prediccion_local/artefactos/entrenamiento.json',
    str(PLAN), str(BACKGROUND),
})
WINDOWS_RESERVED = frozenset({'con', 'prn', 'aux', 'nul', 'clock$',
                             *('com' + str(i) for i in range(1, 10)),
                             *('lpt' + str(i) for i in range(1, 10))})


class EntregaError(ValueError):
    """Fallo cerrado de estructura, ruta o política del paquete."""


@dataclass(frozen=True)
class ArchivoPublico:
    ruta: str
    contenido: bytes
    origen: str = 'fuente-publica'


def validar_nombre(nombre):
    if (not isinstance(nombre, str)
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', nombre)
            or nombre.lower() in WINDOWS_RESERVED):
        raise EntregaError('Nombre inválido: usa sólo letras, números, guion o guion bajo, sin rutas.')
    return nombre


def _relative(value):
    text = str(value)
    path = PurePosixPath(text)
    if (not text or path.is_absolute() or '..' in path.parts or '\\' in text
            or any(not part or part.rstrip(' .') != part
                   or re.search(r'[<>:"|?*\x00-\x1f]', part)
                   or part.split('.')[0].lower() in WINDOWS_RESERVED for part in path.parts)):
        raise EntregaError('Ruta relativa no admitida para un ZIP portable.')
    return path


def podar_directorio(nombre):
    name = nombre.casefold()
    return (name in PRUNED_DIRS or name.startswith(('.pbi', '.venv', '.local', '.tmp'))
            or (name.startswith('.') and name != '.github'))


def permitir_archivo(ruta):
    """Decisión sólo por la ruta: nunca lee contenido para excluir privados."""
    relative = _relative(ruta)
    if any(podar_directorio(part) for part in relative.parts[:-1]):
        return False
    name = relative.name.casefold()
    if name.startswith('.env'):
        return name == '.env.example'
    if name.startswith('.') and name not in SPECIAL_FILES:
        return False
    if name in SPECIAL_FILES or name.endswith(('.dockerfile', '.dockerfile.dockerignore')):
        return True
    if relative.suffix.casefold() == '.png':
        return relative == BACKGROUND
    if relative.suffix.casefold() == '.svg':
        return relative.parts[0] == 'frontend'
    if relative.suffix.casefold() == '.sql':
        # No empaquetar un dump de texto por tener la misma extensión que SQL fuente.
        return (relative in {PurePosixPath('infraestructura/contenedores_docker/inicializar_postgresql.sql'),
                             PurePosixPath('analitica/reportes_power_bi/vista_evaluaciones.sql')}
                or (relative.parent == PurePosixPath('backend/app/persistencia_postgresql/migraciones')
                    and re.fullmatch(r'[0-9]{3}_[a-z0-9_]+\.sql', name) is not None))
    return relative.suffix.casefold() in EXTENSIONS


def _sin_enlace(path):
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & REPARSE_POINT:
        raise EntregaError('Se rechazó un enlace simbólico o junction; no se leyó su destino.')
    return info


def _cadena_segura(path):
    """Comprobar todos los componentes existentes antes de resolver una ruta."""
    absolute = Path(os.path.abspath(path))
    for component in reversed((absolute, *absolute.parents)):
        if os.path.lexists(component):
            _sin_enlace(component)
    return absolute


def _dentro(path, root):
    candidate = _cadena_segura(path).resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise EntregaError('Una ruta queda fuera de su raíz autorizada.') from error
    return candidate


def _regular(info):
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
            or getattr(info, 'st_file_attributes', 0) & REPARSE_POINT):
        raise EntregaError('Se rechazó un archivo no regular o un enlace físico.')
    if info.st_size > MAX_FILE_BYTES:
        raise EntregaError('Un archivo público excede el límite de tamaño del paquete.')


def leer_publico(path, root):
    """Abrir sólo un archivo seleccionado, sin enlaces y dentro de su raíz."""
    candidate = _dentro(path, root)
    before = _sin_enlace(candidate)
    _regular(before)
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    descriptor = os.open(candidate, flags)
    try:
        opened = os.fstat(descriptor)
        _regular(opened)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise EntregaError('El archivo cambió mientras se preparaba la entrega.')
        _dentro(path, root)
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            data = stream.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES or len(data) != opened.st_size:
            raise EntregaError('El tamaño del archivo cambió durante la lectura.')
        return data
    finally:
        if descriptor is not None:
            os.close(descriptor)


def recorrer_publicos(root):
    """Podar por nombre antes de consultar/recorrer cualquier carpeta privada."""
    root = _cadena_segura(root).resolve(strict=True)

    def walk(directory, relative):
        _dentro(directory, root)
        with os.scandir(directory) as entries:
            ordered = sorted(entries, key=lambda entry: entry.name.casefold())
        for entry in ordered:
            rel = relative / entry.name
            # Ningún stat, resolve, open o scandir de los nombres privados.
            if podar_directorio(entry.name) and entry.name.casefold() not in SPECIAL_FILES:
                continue
            if entry.name.casefold().startswith('.env') and entry.name.casefold() != '.env.example':
                continue
            rel = _relative(rel)
            info = _sin_enlace(entry.path)
            if stat.S_ISDIR(info.st_mode):
                if podar_directorio(entry.name):
                    continue
                yield from walk(Path(entry.path), rel)
            elif permitir_archivo(rel):
                _regular(info)
                yield rel, Path(entry.path)

    yield from walk(root, PurePosixPath())


def redactar_plan(contenido):
    """Redactar la copia, no el original; fallar si cambian los delimitadores."""
    text = contenido.decode('utf-8-sig')
    start = list(re.finditer(r'^## Identificación[ \t]*\r?$', text, re.MULTILINE))
    end = list(re.finditer(r'^## Tecnologías obligatorias[ \t]*\r?$', text, re.MULTILINE))
    if len(start) != 1 or len(end) != 1 or start[0].start() >= end[0].start():
        raise EntregaError('El plan no tiene delimitadores únicos de identificación; no se empaquetó.')
    replacement = ('## Identificación\n\n'
                   'Datos personales e institucionales omitidos en esta copia de entrega.\n'
                   'La fuente local se conserva sin modificar; no se presume autorización externa.\n\n')
    return (text[:start[0].start()] + replacement + text[end[0].start():]).encode('utf-8')


def _alumno_placeholder():
    return ('# Identificación privada omitida\n\n'
            'Este archivo es un marcador generado para conservar los enlaces de la documentación.\n'
            'Los datos del alumno/estadía no se incluyen ni se leen al crear el paquete.\n'
            'No contiene firmas, aprobación, participantes o horas acreditadas.\n').encode('utf-8')


def _leeme():
    return r'''# LEEME PRIMERO — NexoCredit, entrega local

Esta copia contiene código y documentación pública depurada, no una base de datos,
cuentas, secretos, imágenes Docker, dependencias instaladas, datasets UCI o modelos
Ollama. No es un instalador offline/autocontenido ni una aplicación ya publicada.
Los hashes verifican integridad respecto del manifiesto; no son firma digital ni
certifican ausencia de secretos pegados accidentalmente en archivos públicos.

## Estructura y revisión antes de ejecutar

Extrae el ZIP sin aplanar carpetas. Dentro de NexoCredit/ están .github/,
NexoCredit.code-workspace y empresa - copia/, la raíz activa del proyecto. Así se
conservan los working-directory de CI. El JSON del manifiesto se entrega junto
al ZIP e incluye rutas, tamaños y SHA-256 del contenido copiado y del ZIP; el
Git SHA es referencia histórica, no prueba de un árbol limpio o de CI nueva.

Revisa primero empresa - copia/README.md, REQUISITOS_TECNOLOGICOS.md y
docs/entrega/ENTREGA_DEMO.md. Las evidencias están fechadas: no garantizan
conectividad actual, suscripción vigente, crédito real o aceptación formal.
Los datos de identificación del plan se redactaron sólo en la copia; el archivo
docs/estadia/ALUMNO.md es un marcador, no la ficha privada original.

## Instalación inicial en Windows: primero construir con Docker

1. Instala/abre Docker Desktop y espera su motor. Esta secuencia es para un
   equipo sin una instalación NexoCredit existente, con puertos locales libres.
   Una carpeta nueva NO crea por sí sola un proyecto/volumen Docker independiente:
   Compose conserva el nombre plurione-docker. Si ya existe, no ejecutes esta
   copia como instalación nueva ni borres su volumen o .env; conserva el entorno
   original y consulta el manual de operación antes de cambiarlo.
   La primera construcción necesita Internet para imágenes y dependencias.
   No desactives TLS, autenticación o antivirus para corregir descargas.
2. Abre PowerShell en NexoCredit/empresa - copia/ y ejecuta:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\docker.ps1 iniciar
```

El lanzador crea un .env privado con contraseñas aleatorias nuevas y construye
la aplicación. No copies .env.example encima del archivo privado generado.
No se incluyen datos, usuarios, contraseñas o llaves de la computadora original.

3. Después de construir, activa los proveedores y acceso locales:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\modo-local.ps1 -Accion local
```

4. Para explicaciones generativas, instala/abre Ollama y utiliza un modelo que
   quepa en la memoria del equipo. El modo local propone llama3.1:8b: si no está
   instalado, descargarlo es una operación adicional con Internet y espacio.
   No se ejecuta ni descarga nada por extraer este paquete.
   Sin modelo, puedes editar exclusivamente EXPLICACIONES_PROVEEDOR=local en
   infraestructura/contenedores_docker/.env y volver a aplicar el backend con
   operacion/aplicacion/Actualizar NexoCredit.cmd. Esa opción es una **plantilla
   de reglas, NO IA generativa**. DOCUMENTOS_PROVEEDOR=local y ML_PROVEEDOR=local
   mantienen las guías y el modelo numérico scikit-learn incluido.
5. Crea tu cuenta propia; no existe una contraseña predeterminada:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\modo-local.ps1 -Accion usuario
```

La consola pide usuario, nombre y contraseña oculta. No compartas la contraseña.
Abre http://localhost:8080/ y entra con esa cuenta. El laboratorio scikit-learn es
UCI/NTD independiente: no modifica el score capturado o reglas-demo-v2 en MXN.
Ollama explica; no es el modelo predictivo del laboratorio.

## Credenciales y límites de esta copia

Azure OpenAI/ML/Search y Microsoft Entra conservan adaptadores y campos de keys
en .env.example, pero **no incluye credenciales**. Azure requiere recursos,
configuración y suscripción vigentes; no hay fallback cloud automático. La guía
v2 está preparada localmente pero pendiente de carga/verificación en Azure
Search. Banxico/otros proveedores y Entra requieren su configuración e Internet.
Los datos locales no constituyen historial Buró o identidad SAT verificada.

Sólo los nuevos escenarios usan reglas-demo-v2; los registros anteriores no se
recalculan. Los resúmenes monetarios redondean pesos, no borran centavos de los
cálculos. La IA, las revisiones y los pagos ficticios no autorizan crédito real.

Power BI requiere Desktop y una conexión nueva de lectura limitada: no se
incluyen PBIX/ABF, cachés o credenciales. Las definiciones PBIP/TMDL son fuente,
no una garantía de actualización o resultado en un equipo nuevo. Entrenar UCI
requiere obtener los datos autorizados por separado; no incluye sus CSV/pickle.

Revisa la documentación de respaldo/soporte antes de operar datos. No publiques
la aplicación, abras puertos o compartas .env, dumps, tokens y capturas privadas.
No se acredita capacitación, horas, Scrum, aceptación o firma por esta entrega.
'''.encode('utf-8')


def _validar_estructura(archivos):
    by_path = {archivo.ruta: archivo for archivo in archivos}
    prefix = f'{WRAPPER}/{PROJECT_DIR}/'
    required = {prefix + relative for relative in REQUIRED_PROJECT}
    required |= {f'{WRAPPER}/.github/workflows/ci.yml', f'{WRAPPER}/NexoCredit.code-workspace'}
    if required - set(by_path):
        raise EntregaError('Faltan archivos públicos obligatorios para la estructura de entrega.')
    workspace = json.loads(by_path[f'{WRAPPER}/NexoCredit.code-workspace'].contenido)
    folders = {folder.get('path') for folder in workspace.get('folders', [])}
    if not {PROJECT_DIR, '.github'} <= folders:
        raise EntregaError('El workspace no conserva las carpetas relativas del proyecto y CI.')
    ci = by_path[f'{WRAPPER}/.github/workflows/ci.yml'].contenido.decode('utf-8-sig')
    for directory in (PROJECT_DIR, PROJECT_DIR + '/frontend'):
        if not re.search(r'^\s*working-directory:\s*' + re.escape(directory) + r'\s*$', ci, re.MULTILINE):
            raise EntregaError('CI no conserva sus working-directory bajo el wrapper.')
    keys = [archivo.ruta.casefold() for archivo in archivos]
    if len(keys) != len(set(keys)):
        raise EntregaError('Las rutas del ZIP colisionan en sistemas sin distinción de mayúsculas.')


def recopilar_archivos(outer_root, project_root):
    outer = _cadena_segura(outer_root).resolve(strict=True)
    project = _dentro(project_root, outer)
    if project != outer / PROJECT_DIR or not project.is_dir():
        raise EntregaError('La raíz activa debe ser la carpeta interior empresa - copia.')
    records = []
    for rel, path in recorrer_publicos(project):
        data = leer_publico(path, project)
        origin = 'fuente-publica'
        if rel == PLAN:
            data = redactar_plan(data)
            origin = 'copia-redactada'
        records.append(ArchivoPublico(f'{WRAPPER}/{PROJECT_DIR}/{rel}', data, origin))
    github = _dentro(outer / '.github', outer)
    for rel, path in recorrer_publicos(github):
        records.append(ArchivoPublico(f'{WRAPPER}/.github/{rel}', leer_publico(path, github)))
    workspace = outer / 'NexoCredit.code-workspace'
    records.append(ArchivoPublico(f'{WRAPPER}/NexoCredit.code-workspace', leer_publico(workspace, outer)))
    records.extend((
        ArchivoPublico(f'{WRAPPER}/{PROJECT_DIR}/{ALUMNO}', _alumno_placeholder(), 'marcador-generado'),
        ArchivoPublico(f'{WRAPPER}/LEEME_PRIMERO.md', _leeme(), 'guia-generada'),
    ))
    _validar_estructura(records)
    return sorted(records, key=lambda record: record.ruta)


def referencia_git(outer):
    try:
        result = subprocess.run(['git', '-C', str(outer), 'rev-parse', '--verify', 'HEAD'],
                                capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and re.fullmatch(r'[a-fA-F0-9]{40}|[a-fA-F0-9]{64}', sha) else None


def _crear_destino(outer):
    destination = _cadena_segura(outer / 'output' / 'entregas')
    destination.mkdir(parents=True, exist_ok=True)
    destination = _dentro(destination, outer)
    if destination != outer / 'output' / 'entregas':
        raise EntregaError('El destino no está en output/entregas de la raíz exterior.')
    return destination


def crear_paquete(outer_root, project_root, nombre):
    validar_nombre(nombre)
    # Completar selección, redacción y validación antes de crear archivos de salida.
    records = recopilar_archivos(outer_root, project_root)
    outer = _cadena_segura(outer_root).resolve(strict=True)
    git_sha = referencia_git(outer)
    destination = _crear_destino(outer)
    zip_path = destination / (nombre + '.zip')
    manifest_path = destination / (nombre + '.manifest.json')
    if os.path.lexists(zip_path) or os.path.lexists(manifest_path):
        raise EntregaError('Ya existe el ZIP o manifiesto; elige otro nombre. No se sobrescribe.')
    # Crear el manifiesto primero reserva ambos nombres sin reemplazar artefactos.
    # Si surge una carrera, queda sólo el archivo nuevo propio, sin borrar archivos.
    with ExitStack() as stack:
        manifest_stream = stack.enter_context(manifest_path.open('x', encoding='utf-8', newline='\n'))
        zip_stream = stack.enter_context(zip_path.open('x+b'))
        with ZipFile(zip_stream, mode='x', compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for record in records:
                archive.writestr(record.ruta, record.contenido)
        zip_stream.flush()
        zip_sha = hashlib.sha256()
        zip_stream.seek(0)
        for block in iter(lambda: zip_stream.read(1024 * 1024), b''):
            zip_sha.update(block)
        manifest = {
            'version_manifiesto': 1, 'fecha_utc': datetime.now(timezone.utc).isoformat(),
            'archivo_zip': zip_path.name, 'sha256_zip': zip_sha.hexdigest(), 'git_sha': git_sha,
            'nota_git': 'SHA de referencia; los archivos actuales pueden incluir cambios locales. '
                        'No acredita árbol limpio, commit nuevo, CI o despliegue.',
            'numero_archivos': len(records),
            'archivos': [{'ruta': record.ruta, 'sha256': hashlib.sha256(record.contenido).hexdigest(),
                          'tamano_bytes': len(record.contenido), 'origen': record.origen}
                         for record in records],
            'limites': ['Sin credenciales/base/cuentas privadas, datos UCI CSV, PBIX/ABF, capturas privadas '
                        'o modelos Ollama.', 'No es instalador offline ni publicación o aceptación formal.',
                        'Revisión humana necesaria para secretos pegados en archivos de código público.'],
        }
        json.dump(manifest, manifest_stream, ensure_ascii=False, indent=2)
        manifest_stream.write('\n')
    return {'zip': zip_path, 'manifiesto': manifest_path, 'sha256_zip': manifest['sha256_zip'],
            'numero_archivos': len(records), 'git_sha': git_sha}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Preparar copia ZIP pública local sin secretos o datos de trabajo.')
    parser.add_argument('--nombre', required=True, help='Ejemplo: NexoCredit_Entrega_2026-10-14 (sin extensión/rutas).')
    args = parser.parse_args(argv)
    project = Path(__file__).absolute().parents[1]
    try:
        result = crear_paquete(project.parent, project, args.nombre)
    except (EntregaError, OSError, UnicodeError, json.JSONDecodeError) as error:
        message = str(error) if isinstance(error, EntregaError) else 'No se completó la entrega; revisa rutas/permisos/estructura.'
        print(message, file=sys.stderr)
        return 1
    print('ZIP creado: output/entregas/' + result['zip'].name)
    print('Manifiesto: output/entregas/' + result['manifiesto'].name)
    print('Archivos públicos: ' + str(result['numero_archivos']))
    print('SHA-256 ZIP: ' + result['sha256_zip'])
    print('Revisa la copia antes de compartirla; no es un instalador offline ni una publicación.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
