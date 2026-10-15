"""Configuración privada del servidor, nunca enviada al navegador."""
import os
from dataclasses import dataclass


class ConfiguracionLocalInvalida(ValueError):
    pass


@dataclass(frozen=True)
class ConfiguracionLocal:
    secreto: str
    duracion: int


def habilitado():
    return os.getenv('LOCAL_AUTH_ENABLED', '').strip().lower() == 'true'


def configuracion():
    if not habilitado():
        raise ConfiguracionLocalInvalida('El acceso local no está habilitado.')
    secreto = os.getenv('LOCAL_AUTH_SECRET', '')
    if (len(secreto) < 48 or len(secreto) > 512 or len(set(secreto)) < 12
            or any(ord(c) < 33 or ord(c) > 126 for c in secreto)
            or any(word in secreto.lower() for word in ('cambiar', 'ejemplo', 'replace', 'change-me'))):
        raise ConfiguracionLocalInvalida('Configura una clave local privada y aleatoria de al menos 48 caracteres.')
    try:
        duracion = int(os.getenv('LOCAL_AUTH_TOKEN_SECONDS', '1800'))
    except ValueError:
        raise ConfiguracionLocalInvalida('La duración de sesión local no es válida.') from None
    if not 900 <= duracion <= 3600:
        raise ConfiguracionLocalInvalida('La duración de sesión local debe ser de 900 a 3600 segundos.')
    return ConfiguracionLocal(secreto=secreto, duracion=duracion)
