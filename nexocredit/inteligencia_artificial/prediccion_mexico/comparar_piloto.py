"""Comparación anidada y agrupada; no publica modelos ni promueve un candidato a producción."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import zipfile

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, roc_auc_score, accuracy_score,
                             confusion_matrix, f1_score, precision_score, recall_score)
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from backend.app.integraciones.prediccion_mexico.datos import preparar
from .entrenar import SHA_ZIP, SEMILLA, metricas

PLAN = Path(__file__).with_name('plan_piloto.json')


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


def candidato(nombre, parametros, semilla):
    if nombre == 'logistica':
        return make_pipeline(StandardScaler(), LogisticRegression(
            C=parametros['C'], max_iter=parametros['max_iter'], random_state=semilla))
    if nombre == 'bosque':
        return RandomForestClassifier(**parametros, random_state=semilla)
    if nombre == 'gradient_boosting':
        return GradientBoostingClassifier(**parametros, random_state=semilla)
    raise ValueError('Candidato fuera del protocolo.')


def cortes_agrupados(x, y, grupos, n, semilla):
    cortes = list(StratifiedGroupKFold(n_splits=n, shuffle=True, random_state=semilla).split(x, y, grupos))
    for train, valid in cortes:
        if set(grupos[train]) & set(grupos[valid]) or len(np.unique(y[train])) != 2 or len(np.unique(y[valid])) != 2:
            raise ValueError('Partición inválida o sin ambas clases.')
    return cortes


def bootstrap(y, predicciones, grupos, semilla):
    rng = np.random.default_rng(semilla)
    unicos = np.unique(grupos)
    filas = [np.flatnonzero(grupos == g) for g in unicos]
    muestras = {nombre: {'auc_roc': [], 'average_precision': [], 'brier': [], 'delta_auc_logistica': []}
                for nombre in predicciones}
    for _ in range(300):
        idx = np.concatenate([filas[i] for i in rng.integers(0, len(filas), len(filas))])
        if len(np.unique(y[idx])) < 2:
            continue
        base_auc = roc_auc_score(y[idx], predicciones['logistica'][idx])
        for nombre, p in predicciones.items():
            auc = float(roc_auc_score(y[idx], p[idx]))
            muestras[nombre]['auc_roc'].append(auc)
            muestras[nombre]['average_precision'].append(float(average_precision_score(y[idx], p[idx])))
            muestras[nombre]['brier'].append(float(brier_score_loss(y[idx], p[idx])))
            muestras[nombre]['delta_auc_logistica'].append(auc - base_auc)
    return {nombre: {metrica: np.quantile(valores, [.025, .975]).tolist() for metrica, valores in datos.items()}
            for nombre, datos in muestras.items()}


def comparar(archivo, salida):
    if salida.exists():
        raise ValueError('La salida ya existe; conservar el informe anterior.')
    if hashlib.sha256(archivo.read_bytes()).hexdigest() != SHA_ZIP:
        raise ValueError('ZIP distinto de la fuente auditada.')
    plan_raw = PLAN.read_bytes()
    plan = json.loads(plan_raw)
    if plan['protocolo'] != 'nexocredit-piloto-comparacion-v1' or plan['promocion_automatica'] is not False:
        raise ValueError('Protocolo no reconocido.')
    with zipfile.ZipFile(archivo) as z:
        frame = pd.read_csv(z.open('TMODULO.csv'), dtype=str, keep_default_na=False, encoding='utf-8-sig')
    x, y, grupos, exclusiones = preparar(frame)
    desarrollo, historica = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=SEMILLA).split(x, y, grupos))
    if len(desarrollo) != 3123 or len(historica) != 783:
        raise ValueError('Cambió la partición histórica; no continuar.')
    x, y, grupos = x[desarrollo], y[desarrollo], grupos[desarrollo]
    nombres = list(plan['candidatos'])
    predicciones = {nombre: np.full(len(y), np.nan) for nombre in [*nombres, 'seleccion_anidada']}
    clases = {nombre: np.full(len(y), -1, dtype=int) for nombre in predicciones}
    umbrales = {nombre: [] for nombre in predicciones}
    folds = []
    cortes = cortes_agrupados(x, y, grupos, 5, plan['semilla'])
    for numero, (train, valid) in enumerate(cortes, 1):
        internos = cortes_agrupados(x[train], y[train], grupos[train], 3, plan['semilla'] + numero)
        seleccion = {}
        for nombre in nombres:
            oof = np.full(len(train), np.nan)
            parametros = plan['candidatos'][nombre]
            for ti, vi in internos:
                modelo = candidato(nombre, parametros, plan['semilla'])
                modelo.fit(x[train[ti]], y[train[ti]])
                oof[vi] = modelo.predict_proba(x[train[vi]])[:, 1]
            if not np.isfinite(oof).all():
                raise ValueError('Predicciones internas incompletas.')
            seleccion[nombre] = float(average_precision_score(y[train], oof))
            calibrador = LogisticRegression(C=1_000_000, max_iter=1000).fit(logit(oof), y[train])
            calibradas = calibrador.predict_proba(logit(oof))[:, 1]
            # Elegir umbral únicamente dentro del entrenamiento externo; nunca en valid.
            umbral = max(np.arange(.05, .801, .01), key=lambda t: f1_score(y[train], calibradas >= t, zero_division=0))
            modelo = candidato(nombre, parametros, plan['semilla'])
            modelo.fit(x[train], y[train])
            pred = calibrador.predict_proba(logit(modelo.predict_proba(x[valid])[:, 1]))[:, 1]
            predicciones[nombre][valid] = pred
            clases[nombre][valid] = pred >= umbral
            umbrales[nombre].append(round(float(umbral), 2))
        elegido = max(nombres, key=lambda n: seleccion[n])
        predicciones['seleccion_anidada'][valid] = predicciones[elegido][valid]
        clases['seleccion_anidada'][valid] = clases[elegido][valid]
        umbrales['seleccion_anidada'].append(umbrales[elegido][-1])
        folds.append({'fold': numero, 'entrenamiento': len(train), 'validacion_externa': len(valid),
                      'upm_entrenamiento': len(set(grupos[train])), 'upm_validacion': len(set(grupos[valid])),
                      'upm_compartidas': 0, 'elegido_solo_con_validacion_interna': elegido,
                      'average_precision_interna': seleccion})
        print(json.dumps({'fold_completado': numero, 'de': 5, 'elegido_interno': elegido}), flush=True)
    if any(not np.isfinite(p).all() for p in predicciones.values()):
        raise ValueError('Predicciones externas incompletas.')
    intervalos = bootstrap(y, predicciones, grupos, plan['semilla'])
    resultados = {}
    for nombre, p in predicciones.items():
        datos = metricas(y, p, .5)
        datos.update({'exactitud': float(accuracy_score(y, clases[nombre])),
                      'precision_positiva': float(precision_score(y, clases[nombre], zero_division=0)),
                      'sensibilidad': float(recall_score(y, clases[nombre], zero_division=0)),
                      'f1': float(f1_score(y, clases[nombre], zero_division=0)),
                      'matriz_confusion': confusion_matrix(y, clases[nombre], labels=[0, 1]).tolist()})
        bins = []
        for bajo, alto in zip(np.arange(0, 1, .1), np.arange(.1, 1.01, .1)):
            mask = (p >= bajo) & ((p < alto) if alto < .999 else (p <= 1))
            if mask.any():
                bins.append({'filas': int(mask.sum()), 'estimacion_media': float(p[mask].mean()), 'frecuencia_observada': float(y[mask].mean())})
        resultados[nombre] = {**datos, 'intervalos_95_aproximados_por_upm': intervalos[nombre],
                              'umbrales_por_fold': umbrales[nombre], 'calibracion_bins_oof': bins}
    mejor = max(nombres, key=lambda n: resultados[n]['average_precision'])
    informe = {'formato': plan['protocolo'], 'plan_sha256': hashlib.sha256(plan_raw).hexdigest(),
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'fuente_zip_sha256': SHA_ZIP,
               'versiones': {'python': platform.python_version(), 'sklearn': sklearn.__version__,
                             'numpy': np.__version__, 'pandas': pd.__version__},
               'filas_desarrollo': len(y), 'upm_desarrollo': len(set(grupos)), 'exclusiones': exclusiones,
               'prueba_historica_excluida': 783, 'prueba_historica_evaluada_en_este_incremento': False,
               'metodo': 'Validación cruzada anidada 5x3 por UPM, calibración sigmoide interna, bootstrap agrupado 300',
               'ponderacion_encuesta': False, 'folds': folds, 'resultados': resultados,
               'mejor_ap_descriptiva': mejor, 'promocion_automatica': False, 'modelo_servido_modificado': False,
               'limites': 'Sólo desarrollo ENIF transversal. No validación empresarial prospectiva, temporal, causal o de equidad. '
                          'Los intervalos bootstrap son aproximados y condicionados a esta validación cruzada. '
                          'La comparación descriptiva no sustituye una prueba final independiente. '
                          'Los umbrales maximizan F1 técnico, no costes aprobados de negocio. '
                          'Ningún resultado habilita decisiones crediticias ni uso con clientes reales.'}
    salida.mkdir(parents=True)
    raw = (json.dumps(informe, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    (salida / 'comparacion.json').write_bytes(raw)
    print(json.dumps({'completado': True, 'reporte_sha256': hashlib.sha256(raw).hexdigest(),
                      'resultados': {k: {'auc': v['auc_roc'], 'ap': v['average_precision'], 'brier': v['brier']} for k, v in resultados.items()},
                      'promocion_automatica': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    comparar(args.zip.resolve(), args.salida.resolve())
