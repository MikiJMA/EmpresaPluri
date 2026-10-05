"""Contrato separado de las solicitudes crediticias del prototipo."""
from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.integraciones.prediccion_azure_ml.cliente_ml import FEATURES, configuracion, predecir

router = APIRouter(prefix='/api/v1/azure-ml', tags=['Demostración UCI'])


class EscenarioUCI(BaseModel):
    model_config = ConfigDict(extra='forbid')
    valores: dict[str, Annotated[int, Field(strict=True, ge=-2_147_483_648, le=2_147_483_647)]]

    @model_validator(mode='after')
    def comprobar(self):
        if set(self.valores) != set(FEATURES):
            raise ValueError('Se requieren exactamente las 19 columnas UCI.')
        for name, value in self.valores.items():
            if name == 'LIMIT_BAL' and value <= 0:
                raise ValueError('LIMIT_BAL debe ser positivo.')
            if name.startswith('PAY_AMT') and value < 0:
                raise ValueError('Los pagos no pueden ser negativos.')
            if name.startswith('PAY_') and not name.startswith('PAY_AMT') and not -2 <= value <= 9:
                raise ValueError('El estado de pago debe estar entre -2 y 9.')
        return self


@router.get('/estado')
def estado():
    _, _, _, ready = configuracion()
    return {'configurado': ready, 'conexion_verificada': False, 'columnas': FEATURES}


@router.post('/predecir')
async def prediccion(escenario: EscenarioUCI):
    return await predecir(escenario.valores)
