from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from psycopg import Error as DatabaseError
from psycopg.errors import UniqueViolation
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.seguimiento_crediticio.modelos import NuevoCredito, NuevoPago, AtenderAlerta
from backend.app.seguimiento_crediticio.repositorio import obtener_seguimiento

router = APIRouter(prefix='/api/v1/seguimiento', dependencies=[Depends(usuario_actual)])


def ejecutar(repo, response, accion):
    response.headers['Cache-Control'] = 'no-store'
    if repo is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        return accion()
    except UniqueViolation:
        raise HTTPException(409, 'La clave o el registro ya existe. Actualiza el detalle; no se duplicó la operación.') from None
    except DatabaseError:
        raise HTTPException(503, 'No se pudo completar el seguimiento. Reintenta sin cambiar los datos ni la clave de operación.') from None
    except (ValueError, ArithmeticError):
        raise HTTPException(502, 'Los datos guardados de seguimiento no cumplen el contrato. No se calcularon cifras sustitutas.') from None


@router.get('/creditos')
def listar(response: Response, limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=1000000), repo=Depends(obtener_seguimiento)):
    return ejecutar(repo, response, lambda: repo.listar(limite, offset))


@router.post('/creditos')
def crear(payload: NuevoCredito, response: Response, repo=Depends(obtener_seguimiento), user=Depends(usuario_actual)):
    return ejecutar(repo, response, lambda: repo.crear(payload, user))


@router.get('/creditos/{ident}')
def detalle(ident: UUID, response: Response, repo=Depends(obtener_seguimiento)):
    return ejecutar(repo, response, lambda: repo.obtener(ident))


@router.post('/creditos/{ident}/pagos')
def pagar(ident: UUID, payload: NuevoPago, response: Response, repo=Depends(obtener_seguimiento), user=Depends(usuario_actual)):
    return ejecutar(repo, response, lambda: repo.pagar(ident, payload, user))


@router.post('/creditos/{ident}/actualizar-alertas')
def actualizar(ident: UUID, response: Response, repo=Depends(obtener_seguimiento), user=Depends(usuario_actual)):
    return ejecutar(repo, response, lambda: repo.actualizar_alertas(ident, user))


@router.post('/alertas/{ident}/atender')
def atender(ident: UUID, payload: AtenderAlerta, response: Response, repo=Depends(obtener_seguimiento), user=Depends(usuario_actual)):
    return ejecutar(repo, response, lambda: repo.atender(ident, payload, user))


@router.get('/auditoria')
def auditoria(response: Response, limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=1000000), repo=Depends(obtener_seguimiento), user=Depends(usuario_actual)):
    # Facultad nueva: no convertir una cuenta Analista en Administrador.
    if 'Administrador' not in user['roles']:
        raise HTTPException(403, 'La auditoría global del seguimiento requiere el rol Administrador.')
    return ejecutar(repo, response, lambda: repo.auditoria(limite, offset))
