"""Reglas ilustrativas de riesgo; no es un modelo entrenado."""
from backend.app.validacion_datos.credito import SolicitudCredito


def evaluar_credito(solicitud: SolicitudCredito):
    margen = round(solicitud.ingresos_mensuales - solicitud.gastos_mensuales, 2)
    # Reglas v2 aprobadas para la demo; no política crediticia ni modelo entrenado.
    por_score = "Alto" if solicitud.score_buro_actual < 500 else "Medio" if solicitud.score_buro_actual < 680 else "Bajo"
    por_margen = "Alto" if margen <= 7000 else "Medio" if margen <= 15000 else "Bajo"
    severidad = {"Bajo": 0, "Medio": 1, "Alto": 2}
    nivel = max((por_score, por_margen), key=severidad.get)
    return {
        "rfc": solicitud.rfc,
        "margen_libre": margen,
        "nivel_riesgo_preliminar": nivel,
        "version_modelo": "reglas-demo-v2",
        "modo": "demostracion",
        "factores": [
            f"Margen mensual: ingresos menos gastos = {margen:.2f} MXN. Riesgo mínimo por margen: {por_margen}.",
            f"Puntaje capturado: {solicitud.score_buro_actual}; fuente no verificada. Riesgo por score: {por_score}.",
            "Reglas demo v2: score 0–499 Alto, 500–679 Medio, 680–1000 Bajo; margen <= 7000 Alto, <= 15000 Medio, > 15000 Bajo. Se conserva el mayor riesgo de ambos; el margen nunca mejora un score de riesgo alto.",
        ],
        "mensaje": "Simulación educativa. No calcula probabilidad de incumplimiento ni autoriza créditos. Requiere revisión humana.",
    }
