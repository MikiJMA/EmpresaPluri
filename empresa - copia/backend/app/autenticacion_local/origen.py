"""IP del socket, o encabezado sobrescrito por el único proxy configurado y resuelto."""
import ipaddress
import os
import socket
import time
from functools import lru_cache


@lru_cache(maxsize=4)
def _direcciones_proxy(host, intervalo):
    try:
        return frozenset(str(ipaddress.ip_address(info[4][0]))
                         for info in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM))
    except (OSError, ValueError):
        return frozenset()


def origen_cliente(request):
    peer = request.client.host if request.client else 'sin-origen'
    # Solo el servicio frontend del Compose propio; no CIDR comodín ni trust-all.
    host = os.getenv('LOCAL_AUTH_TRUSTED_PROXY_HOST', '')
    if host != 'frontend' or peer not in _direcciones_proxy(host, int(time.monotonic() // 30)):
        return peer
    forwarded = request.headers.get('x-forwarded-for', '').strip()
    try:
        if ',' in forwarded or '%' in forwarded:
            return peer
        return str(ipaddress.ip_address(forwarded))
    except ValueError:
        return peer
