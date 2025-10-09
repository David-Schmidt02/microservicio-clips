"""
Punto de entrada principal de la aplicación FastAPI
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.api.v1.main import api_router
from backend.api.dependencies import get_search_service, get_video_service
from backend.scheduler.instances import cleanup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejo del ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # === STARTUP ===
    print("\n" + "="*60)
    print(f">> Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    print("="*60)

    # Iniciar scheduler de limpieza automática si está habilitado
    if settings.CLEANUP_ENABLED:
        cleanup_scheduler.iniciar(
            intervalo_horas=settings.CLEANUP_INTERVAL_HOURS,
            max_age_hours=settings.CLEANUP_MAX_AGE_HOURS
        )
    else:
        print(">> Limpieza automatica deshabilitada (CLEANUP_ENABLED=False)")

    print("="*60 + "\n")

    yield  # La aplicación está corriendo

    # === SHUTDOWN ===
    print("\n" + "="*60)
    print(">> Cerrando aplicacion...")
    cleanup_scheduler.detener()
    print("="*60 + "\n")


# Crear la aplicación FastAPI con lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para búsqueda y concatenación de clips de video basados en transcripciones",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Endpoint de health check
@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Mantener compatibilidad con la API anterior (endpoints sin /api/v1)
@app.get("/buscar")
async def buscar_palabra_legacy(
    palabra: str,
    search_service = Depends(get_search_service)
):
    """Endpoint legacy - redirige a la nueva API"""
    transcripciones = await search_service.buscar_transcripciones(palabra)
    
    # Formato de respuesta legacy
    resultados = [t.to_dict() for t in transcripciones]
    return {"resultados": resultados}


@app.get("/videos")
async def obtener_lista_videos_legacy(
    canal: str, 
    timestamp: str,
    video_service = Depends(get_video_service)
):
    """Endpoint legacy - redirige a la nueva API"""
    videos = await video_service.obtener_videos_vecinos(canal, timestamp)
    return {"videos": videos}


@app.get("/transcripcionClip")
async def obtener_transcripcion_legacy(
    canal: str, 
    timestamp: str,
    search_service = Depends(get_search_service)
):
    """Endpoint legacy - redirige a la nueva API"""
    texto = await search_service.obtener_transcripcion_clip(canal, timestamp)
    
    return {
        "transcripcion": {
            "texto": texto,
            "canal": canal,
            "timestamp": timestamp
        }
    }


@app.post("/concatenar")
async def concatenar_videos_legacy(
    canal: str, 
    videos: list[str],
    video_service = Depends(get_video_service)
):
    """Endpoint legacy - redirige a la nueva API"""
    clip_filename = await video_service.concatenar_videos(canal, videos)
    
    return {
        "message": "Videos concatenados exitosamente",
        "clip_filename": clip_filename
    }


@app.get("/descargar")
async def descargar_clip_legacy(clip: str):
    """Endpoint legacy - redirige a la nueva API"""
    import os
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    
    output_path = os.path.join(settings.OUTPUT_DIR, clip)
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        output_path,
        filename=clip,
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={clip}"}
    )