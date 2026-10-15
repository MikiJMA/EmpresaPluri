"""Sesiones locales de vida corta, separadas criptográficamente de Entra."""
import hashlib
import hmac
import time
from uuid import UUID, uuid4

import jwt
import psycopg
from fastapi import HTTPException

from backend.app.persistencia_postgresql.conexion import database_url
from .configuracion import ConfiguracionLocalInvalida, configuracion, habilitado
from .contrasenas import normalizar_usuario
from .repositorio import LimiteIntentos, RepositorioUsuarios, ROLES

ISSUER = 'urn:nexocredit:auth:local'
AUDIENCE = 'nexocredit-local-api'
TOKEN_TYPE = 'nxc-local+jwt'
KEY_ID = 'local-v1'


def _no_valida():
    return HTTPException(401, 'Sesión no válida o vencida. Inicia sesión nuevamente.',
                         headers={'WWW-Authenticate': 'Bearer'})


def _sin_servicio():
    return HTTPException(503, 'El acceso local no está disponible. Revisa su configuración privada y PostgreSQL.')


def estado_local():
    if not habilitado():
        return {'habilitado': False, 'cuentas_disponibles': False}
    try:
        configuracion()
        if not database_url():
            return {'habilitado': False, 'cuentas_disponibles': False}
        return {'habilitado': True, 'cuentas_disponibles': RepositorioUsuarios().hay_cuentas()}
    except (ConfiguracionLocalInvalida, psycopg.Error):
        return {'habilitado': False, 'cuentas_disponibles': False}


def identidad(user):
    ident = str(UUID(str(user['id'])))
    nombre = user['nombre']
    return {'id': ident, 'nombre': nombre, 'roles': [r for r in user['roles'] if r in ROLES],
            'responsable': f'{nombre} [local:{ident}]', 'proveedor': 'local'}


def iniciar_sesion(usuario, password, origen):
    try:
        config = configuracion()
        if not database_url():
            raise ConfiguracionLocalInvalida()
        usuario = normalizar_usuario(usuario)
        # La IP sale del socket de FastAPI, nunca de un X-Forwarded-For arbitrario.
        origen_hash = hmac.new(config.secreto.encode('utf-8'), origen.encode('utf-8'), hashlib.sha256).hexdigest()
        user = RepositorioUsuarios().intentar(usuario, password, origen_hash)
    except LimiteIntentos as error:
        espera = '15 minutos' if error.retry_after == 900 else 'un minuto'
        raise HTTPException(429, f'Demasiados intentos de acceso. Espera {espera} e intenta nuevamente.',
                            headers={'Retry-After': str(error.retry_after)}) from None
    except (ConfiguracionLocalInvalida, psycopg.Error):
        raise _sin_servicio() from None
    except ValueError:
        raise HTTPException(401, 'Usuario o contraseña incorrectos.') from None
    if user is None:
        raise HTTPException(401, 'Usuario o contraseña incorrectos.')
    now = int(time.time())
    claims = {'iss': ISSUER, 'aud': AUDIENCE, 'sub': str(user['id']), 'iat': now, 'nbf': now,
              'exp': now+config.duracion, 'jti': str(uuid4()), 'version_sesion': user['version_sesion']}
    token = jwt.encode(claims, config.secreto, algorithm='HS256', headers={'typ': TOKEN_TYPE, 'kid': KEY_ID})
    return {'access_token': token, 'token_type': 'bearer', 'expires_in': config.duracion, 'user': identidad(user)}


def es_token_local(token):
    """Solo enruta. La marca NO concede confianza ni reemplaza la validación."""
    try:
        header = jwt.get_unverified_header(token)
        return header.get('typ') == TOKEN_TYPE or header.get('kid') == KEY_ID
    except jwt.PyJWTError:
        return False


def validar_token_local(token):
    try:
        config = configuracion()
        header = jwt.get_unverified_header(token)
        if header.get('alg') != 'HS256' or header.get('typ') != TOKEN_TYPE or header.get('kid') != KEY_ID:
            raise jwt.InvalidTokenError()
        claims = jwt.decode(token, config.secreto, algorithms=['HS256'], audience=AUDIENCE, issuer=ISSUER,
                            options={'require': ['exp', 'iat', 'nbf', 'iss', 'aud', 'sub', 'jti', 'version_sesion']})
        if (claims['aud'] != AUDIENCE or any(type(claims[key]) is not int for key in ('exp', 'iat', 'nbf', 'version_sesion'))
                or claims['version_sesion'] < 1 or claims['exp']-claims['iat'] > config.duracion
                or claims['exp'] <= claims['iat']):
            raise jwt.InvalidTokenError()
        ident = str(UUID(claims['sub']))
        UUID(claims['jti'])
        user = RepositorioUsuarios().obtener(ident)
        if (user is None or not user['activo'] or user['version_sesion'] != claims['version_sesion']
                or not isinstance(user['roles'], list) or not user['roles'] or any(r not in ROLES for r in user['roles'])):
            raise jwt.InvalidTokenError()
        return identidad(user)
    except ConfiguracionLocalInvalida:
        # Desactivar el acceso local revoca inmediatamente estas sesiones.
        raise _no_valida() from None
    except psycopg.Error:
        raise _sin_servicio() from None
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise _no_valida() from None
