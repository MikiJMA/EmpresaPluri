"""Análisis Ollama de la misma solicitud almacenada, sin sobrescribir su riesgo."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg import Error as DatabaseError
from backend.app.autenticacion_entra_id.seguridad import usuario_actual
from backend.app.evaluacion_crediticia import valoracion_ia
from backend.app.persistencia_postgresql.repositorio import obtener_repositorio
from backend.app.persistencia_postgresql.explicaciones import obtener_cache_explicaciones

router = APIRouter(dependencies=[Depends(usuario_actual)], tags=['Valoración IA del escenario'])


@router.get('/api/v1/valoracion-ia/estado')
def estado():
    return valoracion_ia.estado()


@router.post('/api/v1/evaluaciones/{identificador}/valoracion-ia')
def valorar(identificador: UUID, response: Response, repositorio=Depends(obtener_repositorio),
            cache=Depends(obtener_cache_explicaciones), user=Depends(usuario_actual)):
    response.headers['Cache-Control'] = 'no-store'
    if repositorio is None or cache is None:
        raise HTTPException(503, 'PostgreSQL todavía no está configurado.')
    try:
        registro = repositorio.obtener(identificador)
        if registro is None:
            raise HTTPException(404, 'Evaluación no encontrada.')
        datos = valoracion_ia.datos_del_registro(registro)
        if not valoracion_ia.estado()['configurado']:
            raise HTTPException(503, valoracion_ia.estado()['motivo'])
        # Cuota independiente: 10 valoraciones/h/cuenta; no consume la cuota de explicaciones.
        resultado = cache.obtener_o_generar(identificador, valoracion_ia.clave(datos),
                                           'valoracion-ia:' + user['id'], lambda: valoracion_ia.generar(datos))
        return {**resultado, 'evaluacion_id': str(identificador),
                'riesgo_por_reglas': registro['nivel_riesgo_preliminar'],
                'version_reglas': registro['version_modelo'], 'reglas_modificadas': False}
    except DatabaseError:
        raise HTTPException(503, 'No se pudo cargar o conservar la valoración IA. La evaluación guardada no cambia; no se reintentó automáticamente.') from None
