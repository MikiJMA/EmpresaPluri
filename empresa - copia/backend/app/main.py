"""Punto de entrada de la API de NexoCredit."""
import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.rutas_api.routes import router
from backend.app.rutas_api.azure_ml import router as azure_ml_router
from backend.app.rutas_api.azure_search import router as azure_search_router
from backend.app.rutas_api.azure_openai import router as azure_openai_router
from backend.app.rutas_api.datos_financieros import router as datos_financieros_router
from backend.app.autenticacion_entra_id.seguridad import CLIENT_ID, TENANT_ID, SCOPE, usuario_actual

app = FastAPI(title="API de Riesgo Crediticio - NexoCredit", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key", "Authorization"],
)
app.include_router(router, dependencies=[Depends(usuario_actual)])
app.include_router(azure_ml_router, dependencies=[Depends(usuario_actual)])
app.include_router(azure_search_router, dependencies=[Depends(usuario_actual)])
app.include_router(azure_openai_router, dependencies=[Depends(usuario_actual)])
app.include_router(datos_financieros_router, dependencies=[Depends(usuario_actual)])


@app.get('/')
def health_check():
    return {'estado': 'API operativa', 'modo': 'demostracion', 'version': '0.1.0'}


@app.get('/api/v1/auth/config')
def auth_config():
    return {'clientId': CLIENT_ID, 'tenantId': TENANT_ID, 'scope': SCOPE,
            'redirectUri': 'http://localhost:8080/'}


@app.get('/api/v1/auth/me')
def auth_me(user=Depends(usuario_actual)):
    return user
