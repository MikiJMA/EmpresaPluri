"""Segunda opinión del modelo académico local para la evaluación principal.

El modelo fue entrenado con 19 variables UCI (importes en NTD, enteros, Taiwán 2005).
El formulario principal captura: ingresos, gastos, deuda, pagos mensuales, días de
atraso y score en MXN y escala propia. El mapeo es aproximado; se documenta cada
decisión para que el revisor sepa exactamente qué se hizo.

Este resultado nunca sustituye las reglas demo ni autoriza créditos.
"""
import logging

logger = logging.getLogger(__name__)

# Variables fijas neutrales para las que no hay equivalente en el formulario principal
_SEXO_NEUTRO = 1          # 1=Masculino, 2=Femenino; neutro = 1
_EDUCACION_NEUTRA = 2     # 2=Universidad; valor más frecuente en UCI
_MATRIMONIO_NEUTRO = 1    # 1=Casado; valor más frecuente en UCI
_EDAD_NEUTRA = 35         # edad promedio razonable


def _atraso_a_codigo_uci(dias: float) -> int:
    """Convierte días de atraso del formulario al código PAY de UCI (-1 a 9).

    UCI usa: -2=no aplica, -1=pagado puntual, 1-9=meses de retraso.
    Aproximamos con días: 0 días → -1 (puntual), resto → meses completos saturado en 9.
    """
    dias = int(dias)
    if dias == 0:
        return -1
    meses = max(1, min(9, dias // 30 + 1))
    return meses


def mapear_a_uci(solicitud) -> dict:
    """Construye el diccionario de 19 variables UCI a partir de los campos del formulario.

    Decisiones de mapeo (documentadas para transparencia):
    - LIMIT_BAL  → max(1, deuda_actual): límite de crédito aproximado a partir de la deuda.
                   Si deuda=0, se usa 1 (el modelo exige positivo).
    - PAY_0      → mapeo de días de atraso actual al código PAY (-1..9).
    - PAY_2..6   → mismo código PAY_0 para todos los periodos previos (historial homogéneo).
    - BILL_AMT1  → deuda_actual (saldo pendiente). Resto (2-6) → 0.
    - PAY_AMT1   → pagos_mensuales_creditos. Resto (2-6) → 0.
    - SEX, EDUCATION, MARRIAGE, AGE → valores neutros/modales del dataset UCI.

    Todas las variables se truncan a int para cumplir el contrato de cliente_local.py.
    """
    deuda = int(max(1, solicitud.deuda_actual))
    pagos = int(max(0, solicitud.pagos_mensuales_creditos))
    codigo_pago = _atraso_a_codigo_uci(solicitud.dias_atraso_actual)

    return {
        'LIMIT_BAL': deuda,
        'PAY_0': codigo_pago,
        'PAY_2': codigo_pago,
        'PAY_3': codigo_pago,
        'PAY_4': codigo_pago,
        'PAY_5': codigo_pago,
        'PAY_6': codigo_pago,
        'BILL_AMT1': deuda,
        'BILL_AMT2': 0,
        'BILL_AMT3': 0,
        'BILL_AMT4': 0,
        'BILL_AMT5': 0,
        'BILL_AMT6': 0,
        'PAY_AMT1': pagos,
        'PAY_AMT2': 0,
        'PAY_AMT3': 0,
        'PAY_AMT4': 0,
        'PAY_AMT5': 0,
        'PAY_AMT6': 0,
    }


AVISO_MAPEO = (
    'Segunda opinión: modelo logístico académico UCI (Taiwán 2005, importes NTD). '
    'Las variables del formulario se mapearon de forma aproximada: deuda→LIMIT_BAL/BILL_AMT1, '
    'días de atraso→códigos PAY, pagos mensuales→PAY_AMT1; sexo/educación/estado civil/edad '
    'son valores neutros del dataset. El resultado no es una probabilidad real de incumplimiento '
    'ni equivale al score de Buró. No modifica la evaluación principal.'
)


def obtener_segunda_opinion(solicitud) -> dict:
    """Llama al modelo local con el mapeo aproximado y devuelve el resultado o None si falla.

    Nunca lanza excepción: si el modelo no está disponible, retorna None y registra el motivo.
    La evaluación principal no debe depender de este resultado.
    """
    try:
        from backend.app.integraciones.prediccion_local.cliente_local import predecir
        valores = mapear_a_uci(solicitud)
        resultado = predecir(valores)
        return {
            **resultado,
            'advertencia': AVISO_MAPEO,
            'mapeo': 'aproximado',
        }
    except Exception as exc:  # noqa: BLE001
        logger.debug('Modelo local no disponible para segunda opinión: %s', exc)
        return None
