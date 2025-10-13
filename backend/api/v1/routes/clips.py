"""
Endpoints relacionados con videos y clips
"""
from fastapi import APIRouter, Depends, Query, Path

from backend.controllers.video_controller import VideoController
from backend.models.schemas import VideosResponse, ConcatenarRequest
from backend.api.dependencies import get_video_controller

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/videos", response_model=VideosResponse)
async def obtener_lista_videos(
    canal: str = Query(..., min_length=1, max_length=100, description="Canal de los videos"),
    timestamp: str = Query(..., min_length=1, description="Timestamp de referencia"),
    rango: int = Query(3, ge=1, le=10, description="Cantidad de videos a cada lado del timestamp"),
    video_controller: VideoController = Depends(get_video_controller)
):
    """
    Obtiene una lista de videos vecinos a un timestamp específico.

    - **canal**: Nombre del canal (máximo 100 caracteres)
    - **timestamp**: Timestamp de referencia en formato ISO 8601
    - **rango**: Cantidad de videos a obtener a cada lado (por defecto 3, máximo 10)

    Retorna una lista de nombres de archivos de video ordenados cronológicamente.
    """
    return await video_controller.obtener_lista_videos(canal, timestamp, rango)


@router.post("/concatenar")
async def concatenar_videos(
    request: ConcatenarRequest,
    video_controller: VideoController = Depends(get_video_controller)
):
    """
    Concatena una lista de videos y devuelve el archivo resultante.

    - **canal**: Canal de los videos
    - **videos**: Lista de nombres de archivos de video a concatenar (máximo 20)

    Retorna información sobre el clip generado.
    """
    return await video_controller.concatenar_videos(request)


@router.get("/descargar")
async def descargar_clip(
    clip: str = Query(..., description="Nombre del archivo de clip a descargar"),
    video_controller: VideoController = Depends(get_video_controller)
):
    """
    Descarga un clip previamente generado.

    - **clip**: Nombre del archivo de clip (incluye extensión .mp4)

    Retorna el archivo de video para descarga directa.
    """
    return await video_controller.descargar_clip(clip)


@router.get("/video/{canal}/{archivo}")
async def servir_video(
    canal: str = Path(..., description="Nombre del canal"),
    archivo: str = Path(..., description="Nombre del archivo de video"),
    video_controller: VideoController = Depends(get_video_controller)
):
    """
    Sirve un archivo de video original para reproducción.

    - **canal**: Nombre del canal
    - **archivo**: Nombre del archivo de video (.ts)

    Retorna el archivo de video para streaming.
    """
    return await video_controller.servir_video(canal, archivo)
