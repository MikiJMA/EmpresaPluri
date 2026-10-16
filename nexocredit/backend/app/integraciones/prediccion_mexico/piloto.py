"""Controles de un piloto empresarial en sombra; ninguna métrica habilita crédito real."""
import hashlib
import json
from pathlib import Path

REPORTE = Path(__file__).parent / 'piloto' / 'comparacion-v1' / 'comparacion.json'
REPORTE_SHA256 = '50de28cba9113d3751bdfbc66d3857e40bfc3fba293f21c77e1fcb047ce70ea5'
MOTIVOS = [
    'Sin historial empresarial autorizado con desenlaces posteriores al otorgamiento.',
    'Sin validación temporal independiente en la población de la empresa.',
    'Sin costes de errores y umbrales de negocio aprobados.',
    'Sin evaluación empresarial de calibración, sesgos y estabilidad.',
    'Sin aprobación operativa registrada para uso con clientes reales.',
]


def controles_uso():
    return {'modo': 'piloto_sombra', 'decision_automatizada_habilitada': False,
            'uso_con_clientes_reales_habilitado': False, 'validacion_empresarial': 'pendiente',
            'objetivo_empresarial_validado': False, 'motivos_no_promocion': list(MOTIVOS)}


def resumen_comparacion():
    try:
        raw = REPORTE.read_bytes()
        if len(raw) > 200_000 or hashlib.sha256(raw).hexdigest() != REPORTE_SHA256:
            raise ValueError('Informe no íntegro')
        r = json.loads(raw)
        if (r['formato'] != 'nexocredit-piloto-comparacion-v1' or r['promocion_automatica'] is not False
                or r['prueba_historica_evaluada_en_este_incremento'] is not False):
            raise ValueError('Protocolo distinto')
        resultados = {}
        for nombre in ('logistica', 'bosque', 'gradient_boosting', 'seleccion_anidada'):
            m = r['resultados'][nombre]
            resultados[nombre] = {k: m[k] for k in ('auc_roc', 'average_precision', 'brier', 'sensibilidad',
                                                   'precision_positiva', 'f1', 'intervalos_95_aproximados_por_upm')}
            resultados[nombre]['mejora_auc_demostrada_respecto_logistica'] = (
                nombre != 'logistica' and m['intervalos_95_aproximados_por_upm']['delta_auc_logistica'][0] > 0)
        return {'estado': 'completado', 'protocolo': r['formato'], 'reporte_sha256': REPORTE_SHA256,
                'filas_desarrollo': r['filas_desarrollo'], 'prueba_historica_excluida': r['prueba_historica_excluida'],
                'metodo': r['metodo'], 'resultados': resultados, 'modelo_servido_modificado': False,
                'promocion_automatica': False, 'limites': r['limites']}
    except (OSError, ValueError, KeyError, TypeError):
        return {'estado': 'no_disponible', 'promocion_automatica': False,
                'motivo': 'No hay un informe de comparación íntegro disponible; no se inventan mejoras.'}


def estado_piloto():
    return {'control_uso': controles_uso(), 'comparacion_modelos': resumen_comparacion()}
