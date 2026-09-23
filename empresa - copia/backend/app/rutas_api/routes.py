"""Endpoints FastAPI; delegan las reglas al módulo de evaluación crediticia."""
from uuid import UUID, uuid4
from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from psycopg import Error as DatabaseError

from backend.app.validacion_datos.credito import SolicitudCredito
from backend.app.validacion_datos.revision import RevisionManual
from backend.app.evaluacion_crediticia.scoring import evaluar_credito
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio, ConflictoSolicitud

router = APIRouter()


@router.post('/api/v1/evaluaciones/{identificador}/revisiones')
def revisar(identificador: UUID, revision: RevisionManual, repositorio=Depends(obtener_repositorio)):
    if repositorio is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        result = repositorio.revisar(identificador, revision)
    except ConflictoSolicitud:
        raise HTTPException(409, 'La revisión cambió o la clave ya fue utilizada. Cierra y vuelve a abrir el detalle antes de revisar.') from None
    except DatabaseError:
        raise HTTPException(503, 'No se pudo guardar la revisión. Puedes reintentar sin cambiar los campos.') from None
    if result is None:
        raise HTTPException(404, 'Evaluación no encontrada.')
    return result


@router.get('/api/v1/dashboard')
def dashboard(desde: date | None = None, hasta: date | None = None,
              riesgo: Literal['Bajo', 'Medio', 'Alto'] | None = None,
              repositorio=Depends(obtener_repositorio)):
    if desde and hasta and desde > hasta:
        raise HTTPException(422, 'La fecha inicial no puede ser posterior a la final.')
    if repositorio is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        return repositorio.resumen(desde, hasta, riesgo)
    except DatabaseError:
        raise HTTPException(503, 'No se pudo cargar el dashboard. Verifica PostgreSQL.') from None


@router.get("/")
def health_check():
    return {"estado": "API operativa", "modo": "demostracion", "version": "0.1.0"}


@router.post("/api/v1/evaluar")
def evaluar(solicitud: SolicitudCredito, repositorio=Depends(obtener_repositorio), idempotency_key: UUID | None = Header(default=None)):
    resultado = evaluar_credito(solicitud)
    if repositorio is None:
        return {**resultado, 'guardado': False}
    try:
        return repositorio.guardar(idempotency_key or uuid4(), solicitud.model_dump(exclude_none=True), resultado)
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
