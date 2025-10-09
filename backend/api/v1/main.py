"""
Router principal para la API v1
"""
from fastapi import APIRouter

from .routes import search, clips, maintenance

# Router principal para v1
api_router = APIRouter()

# Incluir routers de cada módulo
api_router.include_router(search.router)
api_router.include_router(clips.router)
api_router.include_router(maintenance.router)