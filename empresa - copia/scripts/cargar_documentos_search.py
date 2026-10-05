"""Carga acotada de dos documentos demo. La clave admin solo vive en memoria."""
import getpass
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

ENDPOINT = 'https://search-plurione-demo-julian.search.windows.net'
INDEX = 'plurione-documentos-demo'
VERSION = '2025-09-01'
DESCRIPTION = 'PluriOne demo: alcance-proyecto-v1 y guia-demostracion-v1; esquema 1'
CONTENT = Path(__file__).resolve().parents[1] / 'backend/app/integraciones/busqueda_azure_ai_search/contenidos_demo'
FILES = ('01_alcance_proyecto.md', '02_guia_demostracion.md')


def documentos():
    result = []
    for filename in FILES:
        text = (CONTENT / filename).read_text(encoding='utf-8-sig')
        title = text.splitlines()[0].removeprefix('# ')
        source = re.search(r'^Identificador: (.+)$', text, re.M).group(1)
        version = re.search(r'^Versión: (.+)$', text, re.M).group(1)
        sections = re.split(r'^## ', text, flags=re.M)[1:]
        for section in sections:
            heading, body = section.split('\n', 1)
            ident = heading.split('.')[0]
            if not re.fullmatch(r'(ALC|DEM)-0[1-7]', ident) or len(body) > 16000:
                raise ValueError('Documento fuera del formato esperado')
            result.append({'@search.action': 'mergeOrUpload', 'id': f'{source}-{ident}',
                'fuente': source, 'titulo': title, 'seccion': heading.strip(),
                'contenido': body.strip(), 'version': version,
                'aviso': 'Material académico de demostración. No es una política oficial ni autoriza créditos.'})
    if len(result) != 14 or len({doc['id'] for doc in result}) != 14:
        raise ValueError('Se esperaban exactamente 14 secciones únicas')
    return result


def esquema():
    return {'name': INDEX, 'description': DESCRIPTION, 'fields': [
        {'name': name, 'type': 'Edm.String', 'key': name == 'id',
         'searchable': name in ('titulo', 'seccion', 'contenido'), 'retrievable': True,
         **({'analyzer': 'es.lucene'} if name in ('titulo', 'seccion', 'contenido') else {})}
        for name in ('id', 'fuente', 'titulo', 'seccion', 'contenido', 'version', 'aviso')]}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def cargar(docs, key):
    opener = urllib.request.build_opener(NoRedirect())

    def request(method, path, body=None):
        data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
        req = urllib.request.Request(f'{ENDPOINT}{path}?api-version={VERSION}', data=data,
            headers={'api-key': key, 'Content-Type': 'application/json'}, method=method)
        with opener.open(req, timeout=20) as response:
            return json.load(response)

    try:
        existing = request('GET', f'/indexes/{INDEX}')
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        request('POST', '/indexes', esquema())
    else:
        # No alterar un índice creado por otra herramienta ni cambiar su esquema.
        if existing.get('description') != DESCRIPTION:
            raise ValueError('Existe un índice ajeno a este cargador; no se modificó')
        fields = {field['name']: field for field in existing['fields']}
        for expected in esquema()['fields']:
            if any(fields.get(expected['name'], {}).get(k) != v for k, v in expected.items()):
                raise ValueError('El esquema existente difiere; no se modificó')
    result = request('POST', f'/indexes/{INDEX}/docs/index', {'value': docs})
    statuses = result.get('value', [])
    if (len(statuses) != len(docs) or any(item.get('status') is not True for item in statuses)
            or {item.get('key') for item in statuses} != {doc['id'] for doc in docs}):
        raise ValueError('Carga incompleta; puede repetirse sin duplicar secciones')


def main():
    docs = documentos()
    if '--validar' in sys.argv:
        print('Validación local correcta: 2 documentos, 14 secciones únicas. Sin conexión a Azure.')
        return 0
    if not sys.stdin.isatty():
        print('Abre el archivo CMD con doble clic: se necesita una consola con entrada oculta.')
        return 1
    print(f'Destino: {ENDPOINT} / {INDEX}')
    print('Se cargarán SOLO alcance y guía demo (14 secciones), nunca expedientes ni claves.')
    print('Al repetir, se actualizan esas mismas secciones. No se eliminan índices ni documentos.')
    if input('Escribe CARGAR para continuar: ').strip() != 'CARGAR':
        print('Cancelado sin cambios.'); return 1
    key = getpass.getpass('Pega la clave de administrador principal de Search (oculta): ').strip()
    try:
        if not re.fullmatch(r'[A-Za-z0-9_+/=-]{16,512}', key):
            print('Formato de clave no válido.'); return 1
        cargar(docs, key)
        print('Azure confirmó la carga de las 14 secciones. La clave de administrador no se guardó.')
        print('La disponibilidad en búsquedas puede tardar unos segundos.')
        return 0
    except urllib.error.HTTPError as error:
        print(f'Azure rechazó la operación (HTTP {error.code}). No compartas la clave.')
        return 1
    except Exception:
        print('No se completó la carga. Revisa conexión, permisos y esquema. Puede haber una carga parcial; repetir es seguro para estas secciones.')
        return 1
    finally:
        key = None


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print('\nCancelado.'); sys.exit(1)
