"""Clave no secreta para separar proveedor/modelo/guías y versiones de la caché."""
import json
import os
from hashlib import sha256
from .proveedores import estado_explicaciones, proveedor
from .proveedores_locales.explicaciones import CONTRATO_OLLAMA


def clave_explicacion(registro):
    estado = estado_explicaciones()
    descriptor = {'contrato': 'explicaciones-cache-v1', 'version_modelo': registro.get('version_modelo'),
                  'proveedor': proveedor('explicaciones'), 'documentos': proveedor('documentos'),
                  'implementacion': estado.get('implementacion'), 'configurado': estado['configurado'],
                  'indice': os.getenv('AZURE_SEARCH_INDEX_NAME', '')}
    if descriptor['proveedor'] == 'ollama':
        # Nueva composición servidor/IA: no reutilizar narraciones antiguas.
        # La clave Azure/local no cambia y no se borran filas anteriores.
        descriptor['revision_ollama'] = CONTRATO_OLLAMA
    return sha256(json.dumps(descriptor, sort_keys=True).encode('utf-8')).hexdigest()
