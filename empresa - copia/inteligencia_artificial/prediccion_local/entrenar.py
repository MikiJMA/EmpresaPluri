"""Baseline UCI local: parámetros fijados antes de evaluar, sin descargas ni pickle."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ['LIMIT_BAL', 'PAY_0', *[f'PAY_{i}' for i in range(2, 7)],
            *[f'BILL_AMT{i}' for i in range(1, 7)], *[f'PAY_AMT{i}' for i in range(1, 7)]]
TARGET = 'incumplimiento_mes_siguiente'
PARTICIONES = {
    'entrenamiento': ('carga_azure/entrenamiento_reducido/entrenamiento_reducido.csv', 17909,
                      'd3f2caae94533112d2c0a58241fdb9e1641d6d2ad9cef10635c727ccde6f5b79'),
    'validacion': ('carga_azure/validacion/validacion.csv', 6136,
                   '212b599be2da5989d2762d2b7bc7516bfbb8f56990d988b6f80a7afd49684891'),
    'prueba': ('datos_uci/prueba.csv', 5955,
               'd7cf431db3eb63400d72a5cfca20d679396013ccc18ff5c902ff71215b01fb72'),
}


def clasificar_exportado(modelo, fila):
    z = modelo['intercepto'] + math.fsum(
        coef * ((float(value) - mean) / scale)
        for value, mean, scale, coef in zip(fila, modelo['media'], modelo['escala'], modelo['coeficientes']))
    return int(z > 0)


def metricas(y, probabilidades):
    pred = probabilidades > .5
    return {'filas': len(y), 'matriz_confusion': confusion_matrix(y, pred, labels=[0, 1]).tolist(),
            'auc': float(roc_auc_score(y, probabilidades)), 'exactitud': float(accuracy_score(y, pred)),
            'sensibilidad': float(recall_score(y, pred, zero_division=0)),
            'precision': float(precision_score(y, pred, zero_division=0)),
            'f1': float(f1_score(y, pred, zero_division=0)),
            'baseline_exactitud': float(accuracy_score(y, np.zeros(len(y), dtype=int)))}


def entrenar(datos, salida):
    # No se buscan hiperparámetros ni umbrales usando validación/prueba.
    frames = {}
    grupos = {}
    for nombre, (relativo, filas, sha) in PARTICIONES.items():
        archivo = datos / relativo
        if hashlib.sha256(archivo.read_bytes()).hexdigest() != sha:
            raise ValueError(f'La huella de {nombre} no coincide con los datos auditados.')
        frame = pd.read_csv(archivo)
        if list(frame.columns) != FEATURES + [TARGET] or len(frame) != filas:
            raise ValueError(f'Contrato inesperado en {nombre}.')
        if frame.isna().any().any() or not np.isfinite(frame.to_numpy()).all():
            raise ValueError('No se admiten datos faltantes o no finitos.')
        if set(frame[TARGET].unique()) != {0, 1}:
            raise ValueError('Se requieren ambas clases originales.')
        frames[nombre] = frame
        grupos[nombre] = set(map(tuple, frame[FEATURES].to_numpy()))
    if any(grupos[a] & grupos[b] for a, b in
           [('entrenamiento', 'validacion'), ('entrenamiento', 'prueba'), ('validacion', 'prueba')]):
        raise ValueError('Hay fuga de predictores entre particiones.')
    pipeline = make_pipeline(StandardScaler(), LogisticRegression(
        C=1.0, class_weight='balanced', solver='lbfgs', max_iter=1500, tol=1e-7, random_state=20261012))
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        pipeline.fit(frames['entrenamiento'][FEATURES], frames['entrenamiento'][TARGET])
    scaler, clasificador = pipeline.steps[0][1], pipeline.steps[1][1]
    if clasificador.classes_.tolist() != [0, 1]:
        raise ValueError('Orden inesperado de clases.')
    modelo = {'formato': 'nexocredit-logistica-json-v1', 'modelo_id': 'nexocredit-uci-logistica-v1',
              'algoritmo': 'StandardScaler + LogisticRegression (scikit-learn)', 'columnas': FEATURES,
              'clases': [0, 1], 'umbral': .5, 'media': scaler.mean_.tolist(), 'escala': scaler.scale_.tolist(),
              'coeficientes': clasificador.coef_[0].tolist(), 'intercepto': float(clasificador.intercept_[0]),
              'rangos_entrenamiento': [[int(frames['entrenamiento'][c].min()),
                                        int(frames['entrenamiento'][c].max())] for c in FEATURES], 'metricas': {}}
    for nombre in ('validacion', 'prueba'):
        frame = frames[nombre]
        probabilidades = pipeline.predict_proba(frame[FEATURES])[:, 1]
        modelo['metricas'][nombre] = metricas(frame[TARGET], probabilidades)
    # Contraste de todas las filas: JSON numérico == pipeline sklearn; no se ejecutan objetos serializados.
    for nombre, frame in frames.items():
        esperado = pipeline.predict(frame[FEATURES])
        obtenido = np.asarray([clasificar_exportado(modelo, fila) for fila in frame[FEATURES].to_numpy()])
        if not np.array_equal(esperado, obtenido):
            raise ValueError(f'La exportación no reproduce todas las clases de {nombre}.')
    payload = (json.dumps(modelo, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    digest = hashlib.sha256(payload).hexdigest()
    reporte = {'modelo_sha256': digest, 'modelo_id': modelo['modelo_id'], 'filas_entrenamiento': 17909,
               'filas_contrastadas': 30000, 'discrepancias_exportacion': 0, 'solapamiento_predictores': 0,
               'parametros': {'C': 1.0, 'class_weight': 'balanced', 'solver': 'lbfgs', 'tol': 1e-7,
                              'max_iter': 1500, 'random_state': 20261012, 'umbral': .5},
               'versiones': {'python': platform.python_version(), 'sklearn': sklearn.__version__,
                             'numpy': np.__version__, 'pandas': pd.__version__},
               'fuentes_sha256': {nombre: sha for nombre, (_, _, sha) in PARTICIONES.items()},
               'fuente': 'https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients',
               'licencia': 'CC BY 4.0', 'metricas': modelo['metricas'],
               'limites': 'UCI Taiwán 2005, NTD, partición agrupada aleatoria no temporal. No validado para México. '
                         'No calibrado prospectivamente; clase ponderada, no probabilidad de crédito real. '
                         'No son las entradas ni el scoring del formulario principal.'}
    salida.mkdir(parents=True, exist_ok=True)
    for filename in ('modelo.json', 'entrenamiento.json'):
        if (salida / filename).exists():
            raise ValueError('La salida ya existe. Utiliza otra carpeta para no sobrescribir evidencias.')
    (salida / 'modelo.json').write_bytes(payload)
    (salida / 'entrenamiento.json').write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(reporte, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--datos', type=Path, required=True, help='Carpeta de datos Azure ML auditados, sólo lectura.')
    parser.add_argument('--salida', type=Path, required=True, help='Carpeta nueva de artefactos JSON.')
    args = parser.parse_args()
    entrenar(args.datos.resolve(), args.salida.resolve())
