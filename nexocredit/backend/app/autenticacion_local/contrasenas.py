"""Hash scrypt con sal aleatoria; no se conserva la contraseña en claro."""
import base64
import hashlib
import hmac
import re
import secrets

N, R, P, LONGITUD = 32768, 8, 1, 32
MAXMEM = 64 * 1024 * 1024
MIN_CARACTERES_PASSWORD, MAX_CARACTERES_PASSWORD = 6, 128


def normalizar_usuario(usuario):
    if not isinstance(usuario, str):
        raise ValueError('El usuario debe ser texto.')
    usuario = usuario.strip().lower()
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{2,63}', usuario):
        raise ValueError('Usa un usuario de 3 a 64 caracteres: letras, números, punto, guion o guion bajo.')
    return usuario


def validar_password(password):
    if (not isinstance(password, str) or not MIN_CARACTERES_PASSWORD <= len(password) <= MAX_CARACTERES_PASSWORD
            or len(password.encode('utf-8')) > 512 or not password.strip()):
        raise ValueError(f'La contraseña debe tener de {MIN_CARACTERES_PASSWORD} a {MAX_CARACTERES_PASSWORD} caracteres y no ser solo espacios.')


def _derivar(password, sal):
    return hashlib.scrypt(password.encode('utf-8'), salt=sal, n=N, r=R, p=P,
                          dklen=LONGITUD, maxmem=MAXMEM)


def hash_password(password):
    validar_password(password)
    sal = secrets.token_bytes(16)
    resultado = _derivar(password, sal)
    return '$'.join(['scrypt', str(N), str(R), str(P), base64.b64encode(sal).decode('ascii'),
                     base64.b64encode(resultado).decode('ascii')])


def verificar_password(password, almacenado):
    try:
        validar_password(password)
        partes = almacenado.split('$')
        if partes[:4] != ['scrypt', str(N), str(R), str(P)] or len(partes) != 6:
            return False
        sal = base64.b64decode(partes[4], validate=True)
        esperado = base64.b64decode(partes[5], validate=True)
        if len(sal) != 16 or len(esperado) != LONGITUD:
            return False
        return hmac.compare_digest(_derivar(password, sal), esperado)
    except (ValueError, TypeError, AttributeError, UnicodeError):
        return False


# Solo iguala el coste de una cuenta inexistente; no es una cuenta ni una clave de acceso.
HASH_SENUELO = hash_password(secrets.token_urlsafe(32))
