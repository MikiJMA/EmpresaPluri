"""Única ruta local anónima: login limitado. Sin registro público."""
from fastapi import APIRouter, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field

from backend.app.autenticacion_local.contrasenas import MIN_CARACTERES_PASSWORD, MAX_CARACTERES_PASSWORD
from backend.app.autenticacion_local.servicio import iniciar_sesion
from backend.app.autenticacion_local.origen import origen_cliente

class RutaLogin(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def sin_eco_de_credenciales(request):
            try:
                return await original(request)
            except RequestValidationError:
                # FastAPI puede incluir el input original en errores 422. No devolver
                # el cuerpo de login, ni siquiera si una contraseña no pasa el esquema.
                raise HTTPException(422, 'Usuario o contraseña con formato no válido.') from None
        return sin_eco_de_credenciales


router = APIRouter(prefix='/api/v1/auth/local', tags=['Acceso local'], route_class=RutaLogin)


class SolicitudLogin(BaseModel):
    model_config = ConfigDict(extra='forbid', hide_input_in_errors=True)
    usuario: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=MIN_CARACTERES_PASSWORD, max_length=MAX_CARACTERES_PASSWORD, repr=False)


@router.post('/login')
def login(solicitud: SolicitudLogin, request: Request, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    origen = origen_cliente(request)
    return iniciar_sesion(solicitud.usuario, solicitud.password, origen)
