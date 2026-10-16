"""Segunda opinión UCI temporal junto a una evaluación, sin alterar sus reglas."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg import Error as DatabaseError
from starlette.concurrency import run_in_threadpool

from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.integraciones.proveedores import predecir
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.rutas_api.azure_ml import EscenarioUCI

router = APIRouter(tags=['Segunda opinión académica'], dependencies=[Depends(usuario_actual)])

ADVERTENCIA = (
    'Segunda opinión académica sobre un escenario UCI adicional (Taiwán, importes NTD), '
    'no sobre la identidad o los importes MXN del solicitante. No convierte monedas ni '
    'recalcula o sustituye el riesgo por reglas guardado. No validada para México; '
    'no autoriza créditos. El escenario y esta comparación son temporales, no se guardan.'
)


@router.post('/api/v1/evaluaciones/{identificador}/segunda-opinion')
async def segunda_opinion(identificador: UUID, escenario: EscenarioUCI, response: Response,
                          repositorio=Depends(obtener_repositorio)):
    response.headers['Cache-Control'] = 'no-store'
    if repositorio is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        registro = await run_in_threadpool(repositorio.obtener, identificador)
    except DatabaseError:
        raise HTTPException(503, 'No se pudo cargar la evaluación guardada.') from None
    if registro is None:
        raise HTTPException(404, 'Evaluación no encontrada.')

    # El proveedor es explícito (local o Azure); sus errores no generan un resultado ficticio.
    modelo = await predecir(escenario.valores)
    return {
        'evaluacion_id': str(identificador),
        'riesgo_por_reglas': registro['nivel_riesgo_preliminar'],
        'version_reglas': registro['version_modelo'],
        'modelo': modelo,
        'guardada': False,
        'advertencia': ADVERTENCIA,
    }
