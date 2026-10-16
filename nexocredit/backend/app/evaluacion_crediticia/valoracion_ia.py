"""Valoración generativa del MISMO escenario MXN; no scoring predictivo entrenado."""
import json
import math
import os
from datetime import datetime, timezone
from hashlib import sha256

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.validacion_datos.credito import SolicitudCredito
from backend.app.integraciones.proveedores_locales.explicaciones import configuracion_ollama, reservar_ollama

CONTRATO = 'valoracion-mismo-escenario-ollama-v1'
CAMPOS = ('ingresos_mensuales', 'gastos_mensuales', 'deuda_actual',
          'pagos_mensuales_creditos', 'dias_atraso_actual', 'score_buro_actual')
FACTORES = {
    'margen_mensual': ('Margen mensual', 'MXN'),
    'pagos_ingreso': ('Pagos de créditos / ingresos', '%'),
    'deuda_ingreso': ('Deuda / ingreso mensual', 'meses'),
    'atraso_dias': ('Atraso pendiente capturado', 'días'),
    'score_capturado': ('Score capturado, no verificado', 'puntos'),
}
RECOMENDACIONES = {
    'confirmar_captura': 'Confirmar que la información capturada sea correcta y completa.',
    'revisar_ingresos_gastos': 'Revisar el soporte de ingresos y gastos declarados.',
    'revisar_deuda_pagos': 'Revisar la deuda y los compromisos mensuales declarados.',
    'revisar_atrasos': 'Revisar el origen y situación de los atrasos declarados.',
    'revision_humana': 'Solicitar revisión humana antes de cualquier decisión.',
}
AVISO = ('Valoración generada por Ollama sobre los mismos datos ficticios capturados. '
         'No es un modelo predictivo entrenado o validado para crédito mexicano, una probabilidad '
         'de incumplimiento ni una consulta de Buró. Puede equivocarse. No autoriza ni rechaza créditos '
         'y no cambia el riesgo por reglas, las revisiones o el historial. Se conserva en caché 24 horas.')
SISTEMA = (
    'Valora este escenario académico ficticio, no una solicitud real. Importes MXN. '
    'Considera juntos ingresos, gastos, deuda, pagos, atraso y score no verificado. '
    'Mayor deuda, carga de pagos o atraso y menor score pueden indicar más cautela. '
    'Un buen margen no garantiza solvencia. Selecciona Bajo, Medio o Alto y los códigos '
    'de factores relevantes y revisiones. Usa los indicadores recibidos sin recalcular. '
    'No conoces las reglas ni su resultado. No inventes datos, identidad o probabilidades; '
    'no autorices ni deniegues créditos. Devuelve sólo JSON. Incluye revision_humana.'
)


def estado():
    elegido = os.getenv('VALORACION_IA_PROVEEDOR', 'ollama').strip().lower()
    _, modelo, configurado = configuracion_ollama()
    valido = elegido in ('ollama', 'deshabilitado')
    return {'proveedor': 'ollama' if elegido == 'ollama' else 'deshabilitado' if valido else 'no_valido',
            'configurado': elegido == 'ollama' and configurado,
            'modelo': modelo if elegido == 'ollama' and configurado else None,
            'conexion_verificada': False, 'tipo': 'valoracion-generativa-no-predictiva',
            'motivo': ('Configuración presente; disponibilidad pendiente de una consulta real.'
                       if elegido == 'ollama' and configurado else
                       'Habilita VALORACION_IA_PROVEEDOR=ollama y configura un modelo local ya instalado. '
                       'No se simula una valoración ni se descarga un modelo.')}


def datos_del_registro(registro):
    """Allowlist numérica: ni RFC/CURP/nombre/comentarios/riesgo por reglas llegan al LLM."""
    try:
        fuente = registro['solicitud']
        if any(fuente.get(campo) is None for campo in CAMPOS):
            raise ValueError('Datos incompletos')
        # RFC ficticio interno: validar números sin reenviar la identidad almacenada.
        solicitud = SolicitudCredito(rfc='VALIDACION-INTERNA', **{k: fuente[k] for k in CAMPOS})
        datos = {k: getattr(solicitud, k) for k in CAMPOS}
        margen = round(datos['ingresos_mensuales'] - datos['gastos_mensuales'], 2)
        resultado = {**datos, 'margen_mensual': margen,
                     'pagos_ingreso': round(100 * datos['pagos_mensuales_creditos'] / datos['ingresos_mensuales'], 2),
                     'deuda_ingreso': round(datos['deuda_actual'] / datos['ingresos_mensuales'], 2)}
        if not all(math.isfinite(v) for v in resultado.values()):
            raise ValueError('Indicadores no finitos')
        return resultado
    except (KeyError, TypeError, ValueError, ValidationError):
        raise HTTPException(409, 'El registro necesita ingresos, gastos, deuda, pagos, atraso y score válidos. '
                            'No se sustituyen datos desconocidos por cero ni se modifica el registro histórico.') from None


def clave(datos):
    _, modelo, _ = configuracion_ollama()
    return sha256(json.dumps({'contrato': CONTRATO, 'modelo': modelo,
                              'proveedor': estado()['proveedor'], 'datos': datos}, sort_keys=True).encode()).hexdigest()


def _codigos_validos(valores, permitidos, minimo=1):
    return (isinstance(valores, list) and minimo <= len(valores) <= len(permitidos)
            and all(type(v) is str and v in permitidos for v in valores)
            and len(valores) == len(set(valores)))


def validar_salida(salida):
    if (not isinstance(salida, dict) or set(salida) != {'nivel_riesgo_ia', 'factores', 'recomendaciones'}
            or type(salida['nivel_riesgo_ia']) is not str or salida['nivel_riesgo_ia'] not in ('Bajo', 'Medio', 'Alto')
            or not _codigos_validos(salida['factores'], FACTORES)
            or not _codigos_validos(salida['recomendaciones'], RECOMENDACIONES)):
        raise ValueError('Salida fuera del contrato')
    return salida


def generar(datos):
    configurado = estado()
    if not configurado['configurado']:
        raise HTTPException(503, configurado['motivo'])
    url, modelo, _ = configuracion_ollama()
    schema = {'type': 'object', 'additionalProperties': False,
              'properties': {'nivel_riesgo_ia': {'type': 'string', 'enum': ['Bajo', 'Medio', 'Alto']},
                             'factores': {'type': 'array', 'minItems': 1, 'maxItems': 5, 'uniqueItems': True,
                                          'items': {'type': 'string', 'enum': list(FACTORES)}},
                             'recomendaciones': {'type': 'array', 'minItems': 1, 'maxItems': 5, 'uniqueItems': True,
                                                 'items': {'type': 'string', 'enum': list(RECOMENDACIONES)}}},
              'required': ['nivel_riesgo_ia', 'factores', 'recomendaciones']}
    payload = {'model': modelo, 'stream': False, 'format': schema,
               'options': {'temperature': 0, 'num_predict': 220},
               'messages': [{'role': 'system', 'content': SISTEMA},
                            {'role': 'user', 'content': json.dumps({'datos_capturados_e_indicadores': datos,
                              'unidades': 'Importes MXN; pagos_ingreso porcentaje; deuda_ingreso meses de ingreso; atraso días; score 0 a 1000.',
                              'factores_permitidos': list(FACTORES),
                              'recomendaciones_permitidas': list(RECOMENDACIONES)}, ensure_ascii=False)}]}
    try:
        with reservar_ollama(), httpx.Client(timeout=180, follow_redirects=False, trust_env=False) as client:
            response = client.post(f'{url}/api/chat', json=payload)
        if response.status_code == 404:
            raise HTTPException(503, 'Ollama no encontró el modelo instalado. No se descargó otro modelo.')
        if response.status_code != 200:
            raise HTTPException(502, 'Ollama no pudo valorar el escenario. No se inventó un resultado.')
        if len(response.content) > 65536:
            raise ValueError('Respuesta excesiva')
        data = response.json()
        modelos = {modelo, modelo + ':latest'} if ':' not in modelo else {modelo}
        if data.get('done') is not True or data.get('model') not in modelos:
            raise ValueError('Modelo distinto o generación incompleta')
        message = data['message']
        if message.get('role') != 'assistant' or message.get('tool_calls'):
            raise ValueError('Mensaje no admitido')
        salida = validar_salida(json.loads(message['content']))
    except httpx.TimeoutException:
        raise HTTPException(504, 'Ollama tardó demasiado en valorar el escenario. No se reintentó ni se cambió de proveedor.') from None
    except (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError):
        raise HTTPException(502, 'Ollama devolvió una valoración fuera del contrato. No se muestra ni se inventa una clasificación.') from None
    valores = {**datos, 'atraso_dias': datos['dias_atraso_actual'], 'score_capturado': datos['score_buro_actual']}
    # Control obligatorio del servidor, no confiar en que el LLM siga esta instrucción.
    revisiones = list(salida['recomendaciones'])
    if 'revision_humana' not in revisiones:
        revisiones.append('revision_humana')
    return {'nivel_riesgo_ia': salida['nivel_riesgo_ia'],
            'factores': [{'codigo': k, 'etiqueta': FACTORES[k][0], 'valor': valores[k], 'unidad': FACTORES[k][1]} for k in salida['factores']],
            'recomendaciones': [{'codigo': k, 'texto': RECOMENDACIONES[k]} for k in revisiones],
            'datos_evaluados': datos, 'proveedor': 'ollama', 'modelo': modelo,
            'tipo': 'valoracion-generativa-no-predictiva', 'generada_por_ia': True,
            'fecha_generacion': datetime.now(timezone.utc).isoformat(), 'aviso': AVISO}
