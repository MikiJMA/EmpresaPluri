"""Metadatos del proveedor activo; autenticar este router al incluirlo en main."""
from fastapi import APIRouter

from backend.app.integraciones.proveedores import estados

router = APIRouter(prefix='/api/v1/proveedores', tags=['Proveedores de demostración'])


@router.get('/estado')
def estado():
    return estados()
