from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg import Error as DatabaseError
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.integraciones.proveedores import estado_explicaciones, explicar
from backend.app.integraciones.cache_explicaciones import clave_explicacion
from backend.app.persistencia_postgresql.explicaciones import obtener_cache_explicaciones
from backend.app.autenticacion_entra_id.seguridad import usuario_actual

router = APIRouter()


@router.get('/api/v1/azure-openai/estado')
def estado():
    return estado_explicaciones()


@router.post('/api/v1/evaluaciones/{identificador}/explicacion')
def explicacion(identificador: UUID, response: Response, repositorio=Depends(obtener_repositorio),
                cache=Depends(obtener_cache_explicaciones), user=Depends(usuario_actual)):
    response.headers['Cache-Control'] = 'no-store'
    if repositorio is None or cache is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        registro = repositorio.obtener(identificador)
    except DatabaseError:
        raise HTTPException(503, 'No se pudo cargar la evaluación guardada.') from None
    if registro is None:
        raise HTTPException(404, 'Evaluación no encontrada.')
    try:
        return cache.obtener_o_generar(identificador, clave_explicacion(registro), user['id'], lambda: explicar(registro))
    except DatabaseError:
        raise HTTPException(503, 'No se pudo completar la caché y cuota de la explicación. No se reintentó automáticamente; si la generación se inició, puede haber consumo.') from None
