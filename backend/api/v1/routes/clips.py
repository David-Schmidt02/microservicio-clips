"""
Endpoints relacionados con videos y clips
"""
import os
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.responses import FileResponse
from typing import List

from backend.services.video_service import VideoService
from backend.models.schemas import VideosResponse, ConcatenarRequest
from backend.api.dependencies import get_video_service
from backend.config.settings import settings

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/videos", response_model=VideosResponse)
async def obtener_lista_videos(
    canal: str = Query(..., min_length=1, description="Canal de los videos"),
    timestamp: str = Query(..., min_length=1, description="Timestamp de referencia"),
    rango: int = Query(3, ge=1, le=10, description="Cantidad de videos a cada lado del timestamp"),
    video_service: VideoService = Depends(get_video_service)
):
    """
    Obtiene una lista de videos vecinos a un timestamp específico.
    
    - **canal**: Nombre del canal
    - **timestamp**: Timestamp de referencia en formato ISO 8601
    - **rango**: Cantidad de videos a obtener a cada lado (por defecto 3, máximo 10)
    
    Retorna una lista de nombres de archivos de video ordenados cronológicamente.
    """
    try:
        videos = await video_service.obtener_videos_vecinos(canal, timestamp, rango)
        
        return VideosResponse(videos=videos)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/concatenar")
async def concatenar_videos(
    request: ConcatenarRequest,
    video_service: VideoService = Depends(get_video_service)
):
    """
    Concatena una lista de videos y devuelve el archivo resultante.
    
    - **canal**: Canal de los videos
    - **videos**: Lista de nombres de archivos de video a concatenar
    
    Retorna información sobre el clip generado.
    """
    try:
        clip_filename = await video_service.concatenar_videos(
            request.canal, 
            request.videos
        )
        
        return {
            "message": "Videos concatenados exitosamente",
            "clip_filename": clip_filename,
            "download_url": f"/clips/descargar?clip={clip_filename}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/descargar")
async def descargar_clip(
    clip: str = Query(..., description="Nombre del archivo de clip a descargar")
):
    """
    Descarga un clip previamente generado.
    
    - **clip**: Nombre del archivo de clip (incluye extensión .mp4)
    
    Retorna el archivo de video para descarga directa.
    """
    try:
        output_path = os.path.join(settings.OUTPUT_DIR, clip)
        
        if not os.path.exists(output_path):
            raise HTTPException(
                status_code=404, 
                detail="Archivo de clip no encontrado"
            )
        
        return FileResponse(
            output_path,
            filename=clip,
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={clip}"}
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Error interno del servidor")