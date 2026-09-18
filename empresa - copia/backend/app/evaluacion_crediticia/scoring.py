"""Reglas ilustrativas de riesgo; no es un modelo entrenado."""
from backend.app.validacion_datos.credito import SolicitudCredito


def evaluar_credito(solicitud: SolicitudCredito):
    margen = round(solicitud.ingresos_mensuales - solicitud.gastos_mensuales, 2)
    # Reglas heredadas del prototipo. No representan una política de crédito validada.
    nivel = "Alto"
    if margen > 15000 and solicitud.score_buro_actual >= 680:
        nivel = "Bajo"
    elif margen > 7000:
        nivel = "Medio"
    return {
        "rfc": solicitud.rfc,
        "margen_libre": margen,
        "nivel_riesgo_preliminar": nivel,
        "version_modelo": "reglas-demo-v1",
        "modo": "demostracion",
        "factores": [
            f"Margen mensual: ingresos menos gastos = {margen:.2f} MXN.",
            f"Puntaje capturado: {solicitud.score_buro_actual}; fuente no verificada.",
            "Regla demo: Bajo si margen > 15000 y score >= 680; Medio si margen > 7000; Alto en otro caso.",
        ],
        "mensaje": "Simulación educativa. No calcula probabilidad de incumplimiento ni autoriza créditos. Requiere revisión humana.",
    }
