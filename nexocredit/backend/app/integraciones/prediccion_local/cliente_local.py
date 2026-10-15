"""Modelo logístico académico exportado a JSON numérico; sin pickle, red ni base de datos."""
import hashlib
import json
import math
from pathlib import Path

from fastapi import HTTPException

from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES

ARCHIVO = Path(__file__).parent / 'artefactos' / 'modelo.json'
MODELO_ID = 'nexocredit-uci-logistica-v1'
MODELO_SHA256 = '259b997587543c3466f665a8b62577465014c2c867ebdbfba61544b2d364b8a4'
ORIGEN = 'scikit-learn local'
AVISO = ('Clasificación académica UCI, Taiwán 2005, importes NTD. No es probabilidad de crédito real, '
         'score de Buró ni autorización. No validado para México; no modifica el formulario principal.')


def numero(value):
    return type(value) in (int, float) and math.isfinite(value)


def validar_modelo(modelo):
    claves = {'formato', 'modelo_id', 'algoritmo', 'columnas', 'clases', 'umbral', 'media', 'escala',
              'coeficientes', 'intercepto', 'rangos_entrenamiento', 'metricas'}
    if (not isinstance(modelo, dict) or set(modelo) != claves
            or modelo['formato'] != 'nexocredit-logistica-json-v1' or modelo['modelo_id'] != MODELO_ID
            or modelo['columnas'] != FEATURES or modelo['clases'] != [0, 1] or modelo['umbral'] != .5
            or modelo['algoritmo'] != 'StandardScaler + LogisticRegression (scikit-learn)'
            or not numero(modelo['intercepto'])):
        raise ValueError('Contrato del modelo no válido.')
    for campo in ('media', 'escala', 'coeficientes'):
        vector = modelo[campo]
        if not isinstance(vector, list) or len(vector) != 19 or not all(numero(n) for n in vector):
            raise ValueError('Vector no válido.')
    if not all(n > 0 for n in modelo['escala']):
        raise ValueError('Escala no válida.')
    rangos = modelo['rangos_entrenamiento']
    if (not isinstance(rangos, list) or len(rangos) != 19 or any(
            not isinstance(r, list) or len(r) != 2 or not all(type(n) is int for n in r) or r[0] > r[1]
            for r in rangos)):
        raise ValueError('Rangos no válidos.')
    metricas = modelo['metricas']
    if not isinstance(metricas, dict) or set(metricas) != {'validacion', 'prueba'}:
        raise ValueError('Falta evaluación independiente.')
    for nombre, filas in (('validacion', 6136), ('prueba', 5955)):
        m = metricas[nombre]
        if not isinstance(m, dict) or m.get('filas') != filas:
            raise ValueError('Métricas no válidas.')
        for campo in ('auc', 'exactitud', 'sensibilidad', 'precision', 'f1', 'baseline_exactitud'):
            if not numero(m.get(campo)) or not 0 <= m[campo] <= 1:
                raise ValueError('Métrica no finita o fuera de rango.')
        matriz = m.get('matriz_confusion')
        if (not isinstance(matriz, list) or len(matriz) != 2 or any(
                not isinstance(r, list) or len(r) != 2 or any(type(n) is not int or n < 0 for n in r)
                for r in matriz) or sum(sum(r) for r in matriz) != filas):
            raise ValueError('Matriz no válida.')
        tn, fp = matriz[0]
        fn, tp = matriz[1]
        if (not math.isclose(m['exactitud'], (tn + tp) / filas, abs_tol=1e-12)
                or not math.isclose(m['sensibilidad'], tp / (tp + fn), abs_tol=1e-12)):
            raise ValueError('Métricas contradictorias.')
    return modelo


def cargar_modelo():
    try:
        if ARCHIVO.is_symlink() or ARCHIVO.stat().st_size > 65536:
            raise ValueError('Artefacto no admitido.')
        contenido = ARCHIVO.read_bytes()
        if hashlib.sha256(contenido).hexdigest() != MODELO_SHA256:
            raise ValueError('La huella del artefacto no coincide.')
        return validar_modelo(json.loads(contenido))
    except (OSError, ValueError, TypeError, KeyError, ZeroDivisionError):
        raise HTTPException(503, 'El modelo local no está disponible o su artefacto no pasó la verificación. '
                            'No se simula una predicción ni se cambia automáticamente a Azure.') from None


def estado():
    base = {'proveedor': 'local', 'origen': ORIGEN, 'columnas': FEATURES,
            'modo': 'academico', 'conexion_verificada': False}
    try:
        modelo = cargar_modelo()
    except HTTPException as error:
        return {**base, 'configurado': False, 'motivo': error.detail}
    return {**base, 'configurado': True, 'modelo_configurado': MODELO_ID, 'modelo_sha256': MODELO_SHA256,
            'algoritmo': modelo['algoritmo'], 'metricas_prueba': modelo['metricas']['prueba'],
            'motivo': 'Artefacto local presente y huella comprobada; ejecución pendiente de una consulta.',
            'advertencia': AVISO}


def predecir(valores):
    if (not isinstance(valores, dict) or set(valores) != set(FEATURES)
            or any(type(v) is not int or not -2147483648 <= v <= 2147483647 for v in valores.values())
            or valores['LIMIT_BAL'] <= 0
            or any(valores[n] < 0 for n in FEATURES if n.startswith('PAY_AMT'))
            or any(not -2 <= valores[n] <= 9 for n in FEATURES if n.startswith('PAY_') and not n.startswith('PAY_AMT'))):
        raise HTTPException(422, 'Se requieren las 19 variables UCI enteras dentro de sus límites.')
    modelo = cargar_modelo()
    fila = [valores[n] for n in FEATURES]
    z = modelo['intercepto'] + math.fsum(coef * ((v - mean) / scale) for v, mean, scale, coef in
                                       zip(fila, modelo['media'], modelo['escala'], modelo['coeficientes']))
    if not math.isfinite(z):
        raise HTTPException(503, 'El modelo local no pudo producir una clase válida.')
    fuera = [n for n, v, (minimo, maximo) in zip(FEATURES, fila, modelo['rangos_entrenamiento'])
             if not minimo <= v <= maximo]
    return {'incumplimiento_predicho': z > 0, 'proveedor': 'local', 'origen': ORIGEN,
            'modelo_configurado': MODELO_ID, 'modelo_sha256': MODELO_SHA256, 'modo': 'academico',
            'algoritmo': modelo['algoritmo'], 'metricas_prueba': modelo['metricas']['prueba'],
            'variables_fuera_rango_entrenamiento': fuera, 'advertencia': AVISO}
