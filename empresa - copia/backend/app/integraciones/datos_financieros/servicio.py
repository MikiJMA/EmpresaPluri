"""Caché acotada y aislamiento de fallos por fuente. No participa en el riesgo demo."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import os
import re
import threading
import time

from .proveedores import ErrorProveedor, consultar_banxico, consultar_banco_mundial

CACHE_SECONDS = 3600
ERROR_CACHE_SECONDS = 60
_cache = {}
_locks = {key: threading.Lock() for key in ('banxico', 'banco_mundial')}
AVISO = ('Contexto económico público de México. No es historial crediticio ni dato en tiempo real. '
         'No modifica las reglas demo, la predicción de Azure ML ni la explicación de IA.')


def _fuente(provider):
    token = os.getenv('BANXICO_API_TOKEN', '').strip() if provider == 'banxico' else ''
    signature = hashlib.sha256(token.encode()).digest()
    with _locks[provider]:
        cached = _cache.get(provider)
        if cached and cached[0] == signature and time.monotonic() < cached[1]:
            result = deepcopy(cached[2])
            result['en_cache'] = True
            return result
        now = datetime.now(timezone.utc)
        result = {'id': provider, 'nombre': 'Banco de México' if provider == 'banxico' else 'Banco Mundial',
                  'consulta_utc': now.isoformat(), 'en_cache': False, 'indicadores': []}
        ttl = ERROR_CACHE_SECONDS
        if provider == 'banxico' and not re.fullmatch(r'[A-Za-z0-9]{64}', token):
            result.update(estado='sin_configurar', mensaje='Falta un token válido de Banxico en el servidor. Usa «Conectar Banxico.cmd»; no lo pegues en el navegador ni en el chat.')
        else:
            try:
                result['indicadores'] = consultar_banxico(token) if provider == 'banxico' else consultar_banco_mundial()
                partial = any(item['valor'] is None for item in result['indicadores'])
                result.update(estado='parcial' if partial else 'disponible',
                    mensaje='Algunos indicadores no tienen un dato publicado.' if partial else 'Últimos datos disponibles del proveedor.')
                ttl = CACHE_SECONDS
            except ErrorProveedor as error:
                result.update(estado='error', mensaje=str(error))
        # La vigencia comienza al terminar la consulta; no sirve datos vencidos ante un fallo.
        result['proxima_consulta_utc'] = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()
        _cache[provider] = (signature, time.monotonic() + ttl, deepcopy(result))
        return result


def obtener_indicadores():
    # Fuentes independientes en paralelo; un fallo no elimina las observaciones de la otra.
    with ThreadPoolExecutor(max_workers=2) as pool:
        providers = list(pool.map(_fuente, ('banxico', 'banco_mundial')))
    return {'pais': 'MX', 'aviso': AVISO, 'cache_segundos': CACHE_SECONDS, 'proveedores': providers}
