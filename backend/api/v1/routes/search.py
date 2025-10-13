"""
Endpoints relacionados con búsqueda de transcripciones
"""
from fastapi import APIRouter, Depends, Query

from backend.controllers.search_controller import SearchController
from backend.models.schemas import BusquedaResponse, TranscripcionClipResponse
from backend.api.dependencies import get_search_controller

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/buscar", response_model=BusquedaResponse)
async def buscar_palabra(
    palabra: str = Query(..., min_length=1, max_length=200, description="Palabra a buscar en las transcripciones"),
    search_controller: SearchController = Depends(get_search_controller)
):
    """
    Busca transcripciones que contengan la palabra especificada.

    - **palabra**: Palabra o frase a buscar en las transcripciones (máximo 200 caracteres)

    Retorna hasta 10 resultados por canal, ordenados cronológicamente.
    """
    return await search_controller.buscar_palabra(palabra)


@router.get("/transcripcionClip", response_model=TranscripcionClipResponse)
async def obtener_transcripcion(
    canal: str = Query(..., min_length=1, max_length=100, description="Canal del video"),
    timestamp: str = Query(..., min_length=1, description="Timestamp del clip"),
    duracion_segundos: int = Query(90, ge=1, le=300, description="Duración del clip en segundos"),
    search_controller: SearchController = Depends(get_search_controller)
):
    """
    Obtiene la transcripción concatenada de un clip específico.

    - **canal**: Nombre del canal (máximo 100 caracteres)
    - **timestamp**: Timestamp de inicio del clip en formato ISO 8601
    - **duracion_segundos**: Duración del clip (por defecto 90 segundos, máximo 300)

    Retorna el texto concatenado de todas las transcripciones en el rango de tiempo.
    """
    return await search_controller.obtener_transcripcion_clip(canal, timestamp, duracion_segundos)
