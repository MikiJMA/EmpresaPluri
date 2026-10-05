from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from psycopg import Error as DatabaseError
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.integraciones.explicaciones_azure_openai.cliente import configurado, explicar

router = APIRouter()


@router.get('/api/v1/azure-openai/estado')
def estado():
    return {'configurado': configurado()}


@router.post('/api/v1/evaluaciones/{identificador}/explicacion')
def explicacion(identificador: UUID, repositorio=Depends(obtener_repositorio)):
    if repositorio is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        registro = repositorio.obtener(identificador)
    except DatabaseError:
        raise HTTPException(503, 'No se pudo cargar la evaluación guardada.') from None
    if registro is None:
        raise HTTPException(404, 'Evaluación no encontrada.')
    return explicar(registro)
