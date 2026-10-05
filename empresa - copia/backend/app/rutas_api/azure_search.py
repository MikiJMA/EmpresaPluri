from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.integraciones.busqueda_azure_ai_search.buscador import buscar, configurado, listar_documentos

router = APIRouter(prefix='/api/v1/azure-search', tags=['Documentos demo'])


class Consulta(BaseModel):
    consulta: str = Field(min_length=2, max_length=200)


@router.get('/estado')
def estado():
    return {'configurado': configurado()}


@router.post('/buscar')
def buscar_documentos(body: Consulta):
    return buscar(body.consulta)


@router.get('/documentos')
def documentos_disponibles():
    return listar_documentos()
