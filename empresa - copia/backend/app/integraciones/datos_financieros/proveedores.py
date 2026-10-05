"""Adaptadores de lectura pública; destinos y series cerrados, nunca datos de clientes."""
from datetime import date, datetime, timezone
import json
import math
import re
import ssl
import time

import httpx

BANXICO_URL = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718,SF61745/datos/oportuno'
BANCO_MUNDIAL_URL = 'https://api.worldbank.org/v2/country/MEX/indicator/FP.CPI.TOTL.ZG;NY.GDP.MKTP.KD.ZG'
MAX_BYTES = 131072
BANXICO_SERIES = {
    'SF43718': ('Tipo de cambio FIX', 'MXN por USD', 'Última observación publicada'),
    'SF61745': ('Tasa objetivo de Banxico', '% anual', 'Última observación publicada'),
}
BANCO_MUNDIAL_SERIES = {
    'FP.CPI.TOTL.ZG': ('Inflación de México', '% anual', 'Anual'),
    'NY.GDP.MKTP.KD.ZG': ('Crecimiento del PIB de México', '% anual', 'Anual'),
}


class ErrorProveedor(Exception):
    """Solo mensajes propios y públicos: jamás reenviar errores/URLs del proveedor."""


def _leer_json(url, *, headers=None, params=None, banxico=False):
    context = ssl.create_default_context()
    if banxico:
        context.minimum_version = ssl.TLSVersion.TLSv1_3
    started = time.monotonic()
    try:
        with httpx.Client(timeout=httpx.Timeout(10, connect=8), follow_redirects=False,
                          verify=context) as client:
            with client.stream('GET', url, headers={'Accept': 'application/json', **(headers or {})},
                               params=params) as response:
                if response.status_code in (401, 403):
                    raise ErrorProveedor('El proveedor rechazó el acceso. Revisa la configuración privada del servidor.')
                if response.status_code == 429 or (banxico and response.status_code == 400 and
                                                  'Bmx-secondsToReset' in response.headers):
                    raise ErrorProveedor('El proveedor alcanzó su límite de consultas. Intenta más tarde.')
                if banxico and response.status_code == 400:
                    # SIE también responde 400 al rechazar un token: no confundirlo con una caída.
                    # El cuerpo no se reenvía, ya que puede incluir información privada.
                    raise ErrorProveedor('Banxico rechazó la solicitud. Revisa tu token de consulta y vuelve a guardarlo con «Conectar Banxico.cmd». No lo compartas en el chat.')
                if response.status_code != 200:
                    raise ErrorProveedor('El proveedor no está disponible. Intenta más tarde.')
                if not response.headers.get('Content-Type', '').lower().startswith('application/json'):
                    raise ErrorProveedor('El proveedor devolvió un formato inesperado.')
                body = bytearray()
                for chunk in response.iter_bytes(chunk_size=8192):
                    body.extend(chunk)
                    if len(body) > MAX_BYTES or time.monotonic() - started > 20:
                        raise ErrorProveedor('La respuesta del proveedor superó los límites de lectura.')
                return json.loads(body)
    except httpx.TimeoutException:
        raise ErrorProveedor('El proveedor tardó demasiado. Intenta más tarde.') from None
    except (httpx.HTTPError, ssl.SSLError):
        raise ErrorProveedor('No se pudo conectar de forma segura con el proveedor.') from None
    except (ValueError, UnicodeError):
        raise ErrorProveedor('El proveedor devolvió un formato inesperado.') from None


def _numero(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > 1e9:
        raise ValueError('Número inválido')
    return float(value)


def _indicador(code, spec, value, period, source_url):
    return {'serie': code, 'nombre': spec[0], 'unidad': spec[1], 'frecuencia': spec[2],
            'valor': value, 'periodo': period, 'estado': 'disponible' if value is not None else 'sin_dato',
            'fuente_url': source_url}


def consultar_banxico(token):
    payload = _leer_json(BANXICO_URL, headers={'Bmx-Token': token}, banxico=True)
    try:
        series = payload['bmx']['series']
        if not isinstance(series, list) or len(series) != len(BANXICO_SERIES):
            raise ValueError('Series incompletas')
        indexed = {}
        for row in series:
            code = row['idSerie']
            if code not in BANXICO_SERIES or code in indexed:
                raise ValueError('Serie inesperada')
            records = row.get('datos', [])
            if not isinstance(records, list) or len(records) > 1:
                raise ValueError('Observaciones inesperadas')
            value = period = None
            if records:
                raw = records[0]['dato']
                if not isinstance(raw, str):
                    raise ValueError('Dato inválido')
                period_date = datetime.strptime(records[0]['fecha'], '%d/%m/%Y').date()
                if period_date > datetime.now(timezone.utc).date():
                    raise ValueError('Fecha futura')
                period = period_date.isoformat()
                if raw.strip() not in ('N/E', 'N/D', ''):
                    if not re.fullmatch(r'-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?', raw.strip()):
                        raise ValueError('Formato numérico inválido')
                    value = _numero(float(raw.replace(',', '')))
                    if code == 'SF43718' and value <= 0:
                        raise ValueError('Tipo de cambio inválido')
            indexed[code] = _indicador(code, BANXICO_SERIES[code], value, period,
                'https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp')
        return [indexed[code] for code in BANXICO_SERIES]
    except (KeyError, TypeError, ValueError, OverflowError):
        raise ErrorProveedor('Banxico devolvió datos incompletos o inválidos.') from None


def consultar_banco_mundial():
    payload = _leer_json(BANCO_MUNDIAL_URL,
                         params={'format': 'json', 'mrnev': 1, 'source': 2, 'per_page': 10})
    try:
        if not isinstance(payload, list) or len(payload) != 2:
            raise ValueError('Formato inválido')
        meta, rows = payload
        if not isinstance(meta, dict) or not isinstance(rows, list) or len(rows) != 2:
            raise ValueError('Series incompletas')
        if type(meta.get('pages')) is not int or meta['pages'] != 1 or type(meta.get('total')) is not int or meta['total'] != 2:
            raise ValueError('Respuesta parcial')
        indexed = {}
        for row in rows:
            code = row['indicator']['id']
            if code not in BANCO_MUNDIAL_SERIES or code in indexed or row['countryiso3code'] != 'MEX':
                raise ValueError('Identidad inesperada')
            period = row['date']
            if not isinstance(period, str) or not re.fullmatch(r'\d{4}', period) or not 1900 <= int(period) <= date.today().year:
                raise ValueError('Periodo inválido')
            value = None if row['value'] is None else _numero(row['value'])
            indexed[code] = _indicador(code, BANCO_MUNDIAL_SERIES[code], value, period,
                f'https://data.worldbank.org/indicator/{code}?locations=MX')
        return [indexed[code] for code in BANCO_MUNDIAL_SERIES]
    except (KeyError, TypeError, ValueError, OverflowError):
        raise ErrorProveedor('El Banco Mundial devolvió datos incompletos o inválidos.') from None
