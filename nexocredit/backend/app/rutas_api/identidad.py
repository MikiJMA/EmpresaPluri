"""Ruta autenticada y sin persistencia; nunca refleja identificadores en errores."""
from fastapi import APIRouter, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field

from backend.app.validacion_datos.identidad import revisar_identidad


class RutaIdentidad(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def sin_eco(request):
            try:
                return await original(request)
            except RequestValidationError:
                raise HTTPException(422, 'Revisa el formato de RFC y CURP. No se guardaron estos datos.') from None
        return sin_eco


class SolicitudIdentidad(BaseModel):
    model_config = ConfigDict(extra='forbid', hide_input_in_errors=True)
    rfc: str = Field(min_length=1, max_length=64, repr=False)
    curp: str | None = Field(default=None, max_length=64, repr=False)


router = APIRouter(prefix='/api/v1/identidad', tags=['Revisión local de identidad'], route_class=RutaIdentidad)


@router.post('/revisar')
def revisar(solicitud: SolicitudIdentidad, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    return revisar_identidad(solicitud.rfc, solicitud.curp)
