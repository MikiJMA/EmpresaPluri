"""Selección explícita de proveedor por función, preservando Azure como valor predeterminado."""
import os

from fastapi import HTTPException

from backend.app.integraciones.proveedores_locales import documentos, explicaciones

VARIABLES = {
    'explicaciones': ('EXPLICACIONES_PROVEEDOR', {'azure', 'local', 'ollama'}),
    'documentos': ('DOCUMENTOS_PROVEEDOR', {'azure', 'local'}),
    'ml': ('ML_PROVEEDOR', {'azure', 'local', 'deshabilitado'}),
}
MOTIVO_ML_DESHABILITADO = 'El laboratorio está deshabilitado por configuración. No se simulan predicciones.'


def proveedor(funcion):
    variable, valores = VARIABLES[funcion]
    elegido = os.getenv(variable, 'azure').strip().lower()
    if elegido not in valores:
        raise HTTPException(503, f'La selección {variable} no es válida. No se cambió de proveedor automáticamente.')
    return elegido


def estado_documentos():
    elegido = proveedor('documentos')
    if elegido == 'local':
        return {'configurado': documentos.configurado(), 'proveedor': elegido, 'origen': 'Documentos locales'}
    from backend.app.integraciones.busqueda_azure_ai_search import buscador
    return {'configurado': buscador.configurado(), 'proveedor': elegido, 'origen': 'Azure AI Search'}


def buscar_documentos(consulta):
    elegido = proveedor('documentos')
    if elegido == 'local':
        return documentos.buscar(consulta)
    from backend.app.integraciones.busqueda_azure_ai_search import buscador
    return {**buscador.buscar(consulta), 'proveedor': elegido}


def listar_documentos():
    elegido = proveedor('documentos')
    if elegido == 'local':
        return documentos.listar_documentos()
    from backend.app.integraciones.busqueda_azure_ai_search import buscador
    return {**buscador.listar_documentos(), 'proveedor': elegido}


def estado_explicaciones():
    elegido = proveedor('explicaciones')
    if elegido == 'azure':
        from backend.app.integraciones.explicaciones_azure_openai import cliente
        return {'configurado': cliente.configurado(), 'proveedor': elegido, 'origen': 'Azure OpenAI',
                'implementacion': cliente.DEPLOYMENT, 'generada_por_ia': True, 'conexion_verificada': False}
    # Es el motor compatible con ambas versiones; la respuesta identifica la versión guardada.
    _, modelo, listo = explicaciones.configuracion_ollama() if elegido == 'ollama' else ('', 'plantilla-reglas-demo', True)
    return {'configurado': listo and estado_documentos()['configurado'], 'proveedor': elegido,
            'origen': 'Ollama local' if elegido == 'ollama' else 'Plantilla local de reglas demo',
            'implementacion': modelo if listo else None,
            'generada_por_ia': elegido == 'ollama', 'conexion_verificada': False}


def explicar(registro):
    elegido = proveedor('explicaciones')
    if elegido == 'local':
        return explicaciones.explicar_local(registro, buscar_documentos)
    if elegido == 'ollama':
        return explicaciones.explicar_ollama(registro, buscar_documentos)
    from backend.app.integraciones.explicaciones_azure_openai import cliente
    # Conservar el cliente Azure y su buscador por defecto para el modo heredado.
    # La combinación OpenAI Azure + documentos locales requiere selección explícita.
    resultado = (cliente.explicar(registro, buscador=buscar_documentos)
                 if proveedor('documentos') == 'local' else cliente.explicar(registro))
    return {**resultado, 'proveedor': elegido, 'generada_por_ia': True, 'origen': 'Azure OpenAI'}


def estado_ml():
    elegido = proveedor('ml')
    if elegido == 'local':
        from backend.app.integraciones.prediccion_local import cliente_local
        return cliente_local.estado()
    from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES, configuracion
    base = {'proveedor': elegido, 'columnas': FEATURES, 'conexion_verificada': False}
    if elegido != 'azure':
        return {**base, 'configurado': False, 'origen': 'Laboratorio deshabilitado', 'motivo': MOTIVO_ML_DESHABILITADO}
    return {**base, 'configurado': configuracion()[3], 'origen': 'Azure Machine Learning'}


async def predecir(valores):
    elegido = proveedor('ml')
    if elegido == 'local':
        from backend.app.integraciones.prediccion_local import cliente_local
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(cliente_local.predecir, valores)
    if elegido == 'deshabilitado':
        raise HTTPException(503, MOTIVO_ML_DESHABILITADO)
    from backend.app.integraciones.prediccion_azure_ml.cliente_ml import predecir as predecir_azure
    return {**await predecir_azure(valores), 'proveedor': 'azure'}


def estados():
    """Solo metadatos no secretos; no comprueba redes ni genera texto."""
    resultado = {}
    for funcion, obtener in (('explicaciones', estado_explicaciones),
                             ('documentos', estado_documentos), ('ml', estado_ml)):
        try:
            resultado[funcion] = obtener()
        except HTTPException as error:
            resultado[funcion] = {'configurado': False, 'proveedor': 'no_valido', 'motivo': error.detail}
    return resultado
