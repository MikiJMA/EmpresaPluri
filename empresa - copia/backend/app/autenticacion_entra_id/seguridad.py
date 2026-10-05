"""Acceso delegado Entra: firma, destinatario, emisor, cliente, ámbito y rol."""
from functools import lru_cache
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

# Identificadores públicos de los registros de esta demostración, nunca secretos.
TENANT_ID = '1dd18182-63b6-4e45-b943-990407510e12'
API_ID = '1b783239-3bdb-48ca-8a9b-0a2a9bcf40e4'
CLIENT_ID = 'b4b812ca-bf1d-451b-b220-63f846718a2d'
ISSUER = f'https://login.microsoftonline.com/{TENANT_ID}/v2.0'
SCOPE = f'api://{API_ID}/access_as_user'
bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def claves_publicas():
    return PyJWKClient(f'https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys',
                       cache_jwk_set=True, lifespan=3600, timeout=10)


def validar_token(token):
    try:
        header = jwt.get_unverified_header(token)
        if header.get('alg') != 'RS256' or not isinstance(header.get('kid'), str):
            raise jwt.InvalidTokenError()
        key = claves_publicas().get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=['RS256'], audience=API_ID, issuer=ISSUER,
                            leeway=30, options={'require': ['exp', 'nbf', 'iat', 'iss', 'aud', 'tid', 'oid', 'sub', 'azp', 'ver']})
        if claims['ver'] != '2.0' or claims['tid'] != TENANT_ID or claims['azp'] != CLIENT_ID:
            raise jwt.InvalidTokenError()
        oid = str(UUID(claims['oid']))
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, 'No se pudo verificar la identidad con Microsoft. Intenta más tarde.') from None
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        raise HTTPException(401, 'Sesión no válida o vencida. Inicia sesión nuevamente.',
                            headers={'WWW-Authenticate': 'Bearer'}) from None
    scopes = claims.get('scp', '')
    roles = claims.get('roles', [])
    if (not isinstance(scopes, str) or 'access_as_user' not in scopes.split()
            or not isinstance(roles, list) or not any(role in roles for role in ('Analista', 'Administrador'))):
        raise HTTPException(403, 'Tu cuenta no tiene el permiso y rol necesarios para NexoCredit.')
    name = claims.get('name')
    name = name.strip()[:70] if isinstance(name, str) and name.strip() else 'Usuario Entra'
    return {'id': oid, 'nombre': name, 'roles': [r for r in roles if r in ('Analista', 'Administrador')],
            'responsable': f'{name} [{oid}]'}


def usuario_actual(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None or credentials.scheme.lower() != 'bearer' or len(credentials.credentials) > 20000:
        raise HTTPException(401, 'Inicia sesión con Microsoft para acceder a NexoCredit.',
                            headers={'WWW-Authenticate': 'Bearer'})
    return validar_token(credentials.credentials)
