"""Cliente remoto de demostración. Nunca carga pickle ni simula predicciones."""
import os
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException

FEATURES = ['LIMIT_BAL', 'PAY_0', *[f'PAY_{i}' for i in range(2, 7)],
            *[f'BILL_AMT{i}' for i in range(1, 7)], *[f'PAY_AMT{i}' for i in range(1, 7)]]


def configuracion():
    url = os.getenv('AZURE_ML_SCORING_URI', '').strip()
    key = os.getenv('AZURE_ML_API_KEY', '').strip()
    model = os.getenv('AZURE_ML_MODEL_ID', '').strip()
    parsed = urlsplit(url)
    valid = (parsed.scheme == 'https' and
             (parsed.hostname or '').endswith('.inference.ml.azure.com') and
             parsed.path == '/score' and not parsed.query and not parsed.fragment and
             not parsed.username and not parsed.password and parsed.netloc == parsed.hostname)
    return url, key, model, bool(valid and key and model)


async def predecir(valores):
    url, key, model, ready = configuracion()
    if not ready:
        raise HTTPException(503, 'Azure ML no está configurado. No se generó una predicción.')
    payload = {'input_data': {'columns': FEATURES, 'index': [0],
                              'data': [[valores[name] for name in FEATURES]]}}
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.post(url, headers={'Authorization': f'Bearer {key}'}, json=payload)
        response.raise_for_status()
        body = response.json()
        predictions = body.get('predictions') if isinstance(body, dict) else body
        if not isinstance(predictions, list) or len(predictions) != 1 or type(predictions[0]) is not bool:
            raise ValueError('Contrato de salida inesperado')
    except httpx.TimeoutException:
        raise HTTPException(504, 'Azure ML tardó demasiado. Intenta nuevamente.') from None
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'No se pudo validar la respuesta de Azure ML. No hay resultado disponible.') from None
    return {'incumplimiento_predicho': predictions[0], 'origen': 'Azure Machine Learning',
            'modelo_configurado': model, 'modo': 'academico',
            'advertencia': 'Clasificación académica, no probabilidad ni autorización de crédito.'}
