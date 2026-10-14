"""Catálogo offline con guías históricas v1 y reglas nuevas v2, sin sobrescribirlas."""
from pathlib import Path
import re
import unicodedata

from fastapi import HTTPException

CONTENIDOS = Path(__file__).resolve().parents[1] / 'busqueda_azure_ai_search' / 'contenidos_demo'
ARCHIVOS = ('01_alcance_proyecto.md', '02_guia_demostracion.md', '03_reglas_demo_v2.md')
AVISO = 'Material académico de demostración. No es una política oficial ni autoriza créditos.'


def catalogo():
    """Lee únicamente archivos fijos: ninguna ruta puede proceder de una petición."""
    resultado = []
    try:
        for nombre in ARCHIVOS:
            texto = (CONTENIDOS / nombre).read_text(encoding='utf-8-sig')
            titulo = texto.splitlines()[0].removeprefix('# ')
            fuente = re.search(r'^Identificador: (.+)$', texto, re.M).group(1)
            version = re.search(r'^Versión: (.+)$', texto, re.M).group(1)
            for seccion in re.split(r'^## ', texto, flags=re.M)[1:]:
                encabezado, contenido = seccion.split('\n', 1)
                identificador = encabezado.split('.')[0]
                if not re.fullmatch(r'(ALC|DEM)-0[1-7]', identificador) or len(contenido) > 16000:
                    raise ValueError('Formato de guía no válido')
                resultado.append({'id': f'{fuente}-{identificador}', 'fuente': fuente,
                                  'titulo': titulo, 'seccion': encabezado.strip(),
                                  'contenido': contenido.strip(), 'version': version, 'aviso': AVISO})
        if len(resultado) != 15 or len({doc['id'] for doc in resultado}) != 15:
            raise ValueError('Catálogo incompleto')
        if {doc['fuente'] for doc in resultado} != {'alcance-proyecto-v1', 'guia-demostracion-v1', 'guia-demostracion-v2'}:
            raise ValueError('Fuentes inesperadas')
        if any(not doc['contenido'] for doc in resultado):
            raise ValueError('Sección sin contenido')
    except (OSError, UnicodeError, ValueError, AttributeError, IndexError):
        raise HTTPException(503, 'No se pudo leer el catálogo local completo de guías demo.') from None
    return sorted(resultado, key=lambda doc: (doc['fuente'], doc['version'], doc['seccion'], doc['id']))


def configurado():
    try:
        catalogo()
        return True
    except HTTPException:
        return False


def listar_documentos():
    return {'origen': 'Documentos locales', 'proveedor': 'local', 'resultados': catalogo()}


def _palabras(texto):
    normalizado = ''.join(char for char in unicodedata.normalize('NFKD', texto.casefold())
                          if not unicodedata.combining(char))
    return re.findall(r'[^\W_]+', normalizado, flags=re.UNICODE)


def buscar(consulta):
    # Coincidencia literal de todas las palabras, no consultas SQL/Lucene ni búsqueda semántica.
    palabras = set(_palabras(consulta))
    if not palabras:
        raise HTTPException(422, 'Escribe palabras para buscar.')
    coincidencias = []
    for doc in catalogo():
        tokens = _palabras(' '.join(doc[campo] for campo in ('titulo', 'seccion', 'contenido')))
        if palabras.issubset(tokens):
            coincidencias.append((sum(tokens.count(palabra) for palabra in palabras), doc))
    coincidencias.sort(key=lambda item: (-item[0], item[1]['id']))
    return {'origen': 'Documentos locales', 'proveedor': 'local',
            'resultados': [doc for _, doc in coincidencias[:5]]}
