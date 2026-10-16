"""Modelo asociativo ENIF reproducible; ZIP público fijado por SHA, sin datos de clientes."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score, accuracy_score)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from backend.app.validacion_datos.perfil_enif import COLUMNAS
from backend.app.integraciones.prediccion_mexico.datos import preparar

URL = 'https://www.inegi.org.mx/contenidos/programas/enif/2024/microdatos/enif_2024_bd_csv.zip'
SHA_ZIP = '00e4b0b42775276b2da236a5bba8c64dc5a92c289908a4727dec93dc7684f039'
MODELO_ID = 'nexocredit-enif2024-logistica-v1'
SEMILLA = 20261015
LIMITES = ('Asociación transversal con atrasos autodeclarados entre junio de 2023 y la entrevista de 2024; '
           'no predice impagos futuros, no consulta Buró ni verifica identidad. '
           'Sólo personas con ingreso laboral positivo declarado y al menos un crédito formal. '
           'Muestra de casos completos, sin ponderar por factores de expansión; no estima tasas nacionales. '
           'No validado para decisiones crediticias; no causal ni calibrado prospectivamente.')


def metricas(y, p, umbral):
    pred = p >= umbral
    return {'filas': len(y), 'positivos': int(y.sum()), 'prevalencia_muestral': float(y.mean()),
            'auc_roc': float(roc_auc_score(y, p)), 'average_precision': float(average_precision_score(y, p)),
            'brier': float(brier_score_loss(y, p)), 'exactitud': float(accuracy_score(y, pred)),
            'sensibilidad': float(recall_score(y, pred, zero_division=0)),
            'precision_positiva': float(precision_score(y, pred, zero_division=0)),
            'f1': float(f1_score(y, pred, zero_division=0)),
            'matriz_confusion': confusion_matrix(y, pred, labels=[0, 1]).tolist()}


def entrenar(archivo, salida):
    digest = hashlib.sha256(archivo.read_bytes()).hexdigest()
    if digest != SHA_ZIP:
        raise ValueError('El ZIP no corresponde a la descarga ENIF auditada. No se entrena con otra fuente.')
    if salida.exists():
        raise ValueError('Utiliza una carpeta de salida nueva para conservar las evidencias.')
    with zipfile.ZipFile(archivo) as z:
        frame = pd.read_csv(z.open('TMODULO.csv'), dtype=str, keep_default_na=False, encoding='utf-8-sig')
        csv_sha = hashlib.sha256(z.read('TMODULO.csv')).hexdigest()
    if frame['LLAVEMOD'].duplicated().any() or frame['UPM_DIS'].eq('').any():
        raise ValueError('Identificadores duplicados o unidades de muestreo ausentes.')
    x, y, grupos, rechazos = preparar(frame)
    entrenamiento_validacion, prueba = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=SEMILLA).split(x, y, grupos))
    ti, vi = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEMILLA + 1).split(
        x[entrenamiento_validacion], y[entrenamiento_validacion], grupos[entrenamiento_validacion]))
    train, valid = entrenamiento_validacion[ti], entrenamiento_validacion[vi]
    if any(set(grupos[a]) & set(grupos[b]) for a, b in [(train, valid), (train, prueba), (valid, prueba)]):
        raise ValueError('Solapamiento de unidades de muestreo.')
    candidatos = []
    for c in (.1, 1., 10.):
        pipeline = make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=2000, random_state=SEMILLA))
        pipeline.fit(x[train], y[train])
        p = pipeline.predict_proba(x[valid])[:, 1]
        candidatos.append((float(roc_auc_score(y[valid], p)), c, pipeline, p))
    _, c, pipeline, pvalid = max(candidatos, key=lambda item: item[0])
    umbral = max(np.arange(.05, .801, .01), key=lambda t: f1_score(y[valid], pvalid >= t))
    umbral = round(float(umbral), 2)
    scaler, clf = pipeline.steps[0][1], pipeline.steps[1][1]
    modelo = {'formato': 'nexocredit-enif-logistica-json-v1', 'modelo_id': MODELO_ID,
              'columnas': COLUMNAS, 'media': scaler.mean_.tolist(), 'escala': scaler.scale_.tolist(),
              'coeficientes': clf.coef_[0].tolist(), 'intercepto': float(clf.intercept_[0]),
              'umbral': umbral, 'fuente': URL, 'fuente_sha256': SHA_ZIP, 'limites': LIMITES,
              'objetivo': 'algun_atraso_reportado', 'pais': 'México', 'metricas': {}}
    for nombre, idx in [('entrenamiento', train), ('validacion', valid), ('prueba', prueba)]:
        p = pipeline.predict_proba(x[idx])[:, 1]
        modelo['metricas'][nombre] = metricas(y[idx], p, umbral)
    ptest = pipeline.predict_proba(x[prueba])[:, 1]
    base = np.full(len(prueba), y[train].mean())
    modelo['baseline_prueba'] = metricas(y[prueba], base, umbral)
    # Comparar exactamente la transformación compartida + JSON contra sklearn en todos los casos.
    z = modelo['intercepto'] + ((x - scaler.mean_) / scaler.scale_) @ clf.coef_[0]
    pjson = 1 / (1 + np.exp(-z))
    error = float(np.max(np.abs(pjson - pipeline.predict_proba(x)[:, 1])))
    if error > 1e-12:
        raise ValueError('Exportación diferente de sklearn.')
    payload = (json.dumps(modelo, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    reporte = {'modelo_id': MODELO_ID, 'modelo_sha256': hashlib.sha256(payload).hexdigest(),
               'fuente': URL, 'zip_sha256': digest, 'tmodulo_sha256': csv_sha, 'entrevistas': len(frame),
               'casos_utilizados': len(y), 'excluidos': rechazos, 'sin_upm_compartidas': True,
               'particion': '60/20/20 aproximado por UPM_DIS, aleatoria no temporal', 'semilla': SEMILLA,
               'candidatos': [{'C': item[1], 'auc_validacion': item[0]} for item in candidatos],
               'seleccion': {'C': c, 'umbral': umbral, 'criterio': 'C por AUC y umbral por F1 sólo en validación'},
               'sin_variables_protegidas': True,
               'excluidos_del_modelo': ['RFC', 'CURP', 'nombre', 'edad', 'sexo', 'origen_etnico', 'discapacidad',
                                       'P6_3_* (objetivo)', 'P6_4_*', 'P4_4_7', 'P4_6_2', 'P6_7',
                                       'score_buro_actual', 'dias_atraso_actual'],
               'error_maximo_exportacion': error, 'filas_contrastadas': len(y),
               'versiones': {'python': platform.python_version(), 'sklearn': sklearn.__version__,
                             'pandas': pd.__version__, 'numpy': np.__version__},
               'metricas': modelo['metricas'], 'baseline_prueba': modelo['baseline_prueba'], 'limites': LIMITES}
    salida.mkdir(parents=True)
    (salida / 'modelo.json').write_bytes(payload)
    (salida / 'entrenamiento.json').write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(reporte, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    entrenar(args.zip.resolve(), args.salida.resolve())
