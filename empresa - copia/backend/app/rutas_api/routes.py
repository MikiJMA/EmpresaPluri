"""Endpoints FastAPI; delegan las reglas al módulo de evaluación crediticia."""
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from psycopg import Error as DatabaseError

from backend.app.validacion_datos.credito import SolicitudCredito
from backend.app.evaluacion_crediticia.scoring import evaluar_credito
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio, ConflictoSolicitud

router = APIRouter()


@router.get("/")
def health_check():
    return {"estado": "API operativa", "modo": "demostracion", "version": "0.1.0"}


@router.post("/api/v1/evaluar")
def evaluar(solicitud: SolicitudCredito, repositorio=Depends(obtener_repositorio), idempotency_key: UUID | None = Header(default=None)):
    resultado = evaluar_credito(solicitud)
    if repositorio is None:
        return {**resultado, 'guardado': False}
    try:
        return repositorio.guardar(idempotency_key or uuid4(), solicitud.model_dump(), resultado)
    except ConflictoSolicitud:
        raise HTTPException(409, 'La clave de reintento ya pertenece a otra solicitud.') from None
    except DatabaseError:
        raise HTTPException(503, 'No se pudo guardar la evaluación. Verifica PostgreSQL e intenta nuevamente.') from None


@router.get('/api/v1/evaluaciones')
def historial(limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), repositorio=Depends(obtener_repositorio)):
    if repositorio is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        return repositorio.listar(limite, offset)
    except DatabaseError:
        raise HTTPException(503, 'El historial no está disponible. Verifica PostgreSQL.') from None


@router.get('/api/v1/evaluaciones/{identificador}')
def detalle(identificador: UUID, repositorio=Depends(obtener_repositorio)):
    if repositorio is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        resultado = repositorio.obtener(identificador)
    except DatabaseError:
        raise HTTPException(503, 'La evaluación no está disponible. Verifica PostgreSQL.') from None
    if resultado is None:
        raise HTTPException(404, 'Evaluación no encontrada.')
    return resultado
