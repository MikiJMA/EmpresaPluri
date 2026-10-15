"""Indicadores públicos; mismo control de sesión/roles que el resto de PluriOne."""
from fastapi import APIRouter, Response
from backend.app.integraciones.datos_financieros.servicio import obtener_indicadores

router = APIRouter(prefix='/api/v1/datos-financieros', tags=['Indicadores financieros'])


@router.get('/indicadores')
def indicadores(response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return obtener_indicadores()
