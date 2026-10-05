"""Búsqueda textual en documentos demo; no genera respuestas ni decisiones."""
import os
import re

import httpx
from fastapi import HTTPException

ENDPOINT = 'https://search-plurione-demo-julian.search.windows.net'
INDEX = 'plurione-documentos-demo'
VERSION = '2025-09-01'
FIELDS = ('id', 'fuente', 'titulo', 'seccion', 'contenido', 'version', 'aviso')


def configurado():
    return (os.getenv('AZURE_SEARCH_ENDPOINT', '').rstrip('/') == ENDPOINT
            and os.getenv('AZURE_SEARCH_INDEX_NAME') == INDEX
            and bool(os.getenv('AZURE_SEARCH_QUERY_KEY', '').strip()))


def buscar(consulta):
    # Palabras literales: el usuario no controla filtros, sintaxis Lucene ni URLs.
    palabras = re.findall(r'[^\W_]+', consulta, flags=re.UNICODE)
    if not palabras:
        raise HTTPException(422, 'Escribe palabras para buscar.')
    return _consultar(' '.join(palabras), limite=5)


def listar_documentos():
    """Catálogo demo autenticado; no acepta filtros ni consultas del cliente."""
    data = _consultar('*', limite=50, catalogo=True)
    data['resultados'].sort(key=lambda item: (item['fuente'], item['version'], item['seccion'], item['id']))
    return data


def _consultar(texto, limite, catalogo=False):
    if not configurado():
        raise HTTPException(503, 'Falta la configuración local de Azure AI Search.')
    try:
        with httpx.Client(timeout=8, follow_redirects=False) as client:
            response = client.post(f'{ENDPOINT}/indexes/{INDEX}/docs/search',
                params={'api-version': VERSION},
                headers={'api-key': os.environ['AZURE_SEARCH_QUERY_KEY']},
                json={'search': texto, 'queryType': 'simple',
                      'searchMode': 'all', 'searchFields': 'titulo,seccion,contenido',
                      'select': ','.join(FIELDS), 'top': limite,
                      **({'count': True} if catalogo else {})})
        if response.status_code == 404:
            raise HTTPException(503, 'Todavía falta crear el índice y cargar los documentos.')
        if response.status_code in (401, 403):
            raise HTTPException(503, 'Azure rechazó la clave de consulta. Revisa la configuración local.')
        if response.status_code == 429:
            raise HTTPException(503, 'Azure está limitando las consultas. Intenta más tarde.')
        if response.status_code != 200:
            raise HTTPException(502, 'Azure no pudo completar la búsqueda.')
        data = response.json()
        values = data['value']
        if not isinstance(values, list) or len(values) > limite:
            raise ValueError('Formato inesperado')
        if catalogo and (type(data.get('@odata.count')) is not int or data['@odata.count'] != len(values)):
            raise HTTPException(502, 'No se pudo recuperar el catálogo completo. Usa el buscador o intenta más tarde.')
        results = []
        for item in values:
            if not all(isinstance(item.get(field), str) for field in FIELDS):
                raise ValueError('Campos incompletos')
            results.append({field: item[field][:16000] for field in FIELDS})
        return {'origen': 'Azure AI Search', 'resultados': results}
    except httpx.TimeoutException:
        raise HTTPException(504, 'Azure tardó demasiado. Intenta nuevamente.') from None
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(502, 'No se pudo leer una respuesta válida de Azure AI Search.') from None
