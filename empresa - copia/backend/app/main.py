"""Punto de entrada de la API de PluriOne."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.rutas_api.routes import router

app = FastAPI(title="API de Riesgo Crediticio - PluriOne", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key"],
)
app.include_router(router)
