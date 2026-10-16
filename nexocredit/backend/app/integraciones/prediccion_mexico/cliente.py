"""Sólo parámetros numéricos verificados: no carga pickle, no llama IA generativa ni red."""
import hashlib
import json
import math
from pathlib import Path

from fastapi import HTTPException
from backend.app.validacion_datos.perfil_enif import COLUMNAS, vectorizar
from .piloto import estado_piloto

CARPETA = Path(__file__).parent / 'artefactos'
MODELO_ID = 'nexocredit-enif2024-logistica-v1'
MODELO_SHA256 = '1f6238b217583d0f5c00320d9caf3c331e422452104776b9b99b57a75440e621'


def cargar_modelo():
    try:
        raw = (CARPETA / 'modelo.json').read_bytes()
        if len(raw) > 100_000 or hashlib.sha256(raw).hexdigest() != MODELO_SHA256:
            raise ValueError('Huella no válida')
        modelo = json.loads(raw)
        if modelo['modelo_id'] != MODELO_ID or modelo['columnas'] != COLUMNAS:
            raise ValueError('Contrato no válido')
        for key in ('media', 'escala', 'coeficientes'):
            if len(modelo[key]) != len(COLUMNAS) or not all(type(v) in (int, float) and math.isfinite(v) for v in modelo[key]):
                raise ValueError('Parámetros no válidos')
        if min(modelo['escala']) <= 0 or not 0 < modelo['umbral'] < 1:
            raise ValueError('Escala o umbral no válido')
        return modelo
    except (OSError, ValueError, KeyError, TypeError):
        raise HTTPException(503, 'Modelo mexicano no disponible o artefacto no íntegro. No se inventó un resultado.') from None


def metadatos():
    modelo = cargar_modelo()
    return {**estado_piloto(), 'modelo_id': MODELO_ID, 'modelo_sha256': MODELO_SHA256, 'pais': 'México',
            'fuente': modelo['fuente'], 'objetivo': modelo['objetivo'], 'umbral': modelo['umbral'],
            'metricas_prueba': modelo['metricas']['prueba'], 'baseline_prueba': modelo['baseline_prueba'],
            'exactitud_siempre_sin_atraso': 1 - modelo['metricas']['prueba']['prevalencia_muestral'],
            'limites': modelo['limites'], 'requiere_azure': False, 'requiere_ollama': False}


def evaluar_perfil(perfil):
    modelo = cargar_modelo()
    x = vectorizar(perfil)
    z = modelo['intercepto'] + math.fsum(
        coef * ((valor - media) / escala)
        for valor, media, escala, coef in zip(x, modelo['media'], modelo['escala'], modelo['coeficientes']))
    estimacion = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
    positiva = estimacion >= modelo['umbral']
    return {**metadatos(), 'clase': 'perfil_asociado_a_atraso' if positiva else 'perfil_no_asociado_a_atraso',
            'estimacion_asociativa': round(estimacion, 6), 'atraso_reportado_estimado': positiva,
            'tipo': 'modelo_estadistico_entrenado', 'reglas_score_utilizadas': False,
            'probabilidad_impago_futuro': None}
