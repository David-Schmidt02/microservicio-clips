"""
Endpoints relacionados con búsqueda de transcripciones
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List

from backend.services.search_service import SearchService
from backend.models.schemas import BusquedaResponse, TranscripcionResponse, TranscripcionClipResponse
from backend.api.dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/buscar", response_model=BusquedaResponse)
async def buscar_palabra(
    palabra: str = Query(..., min_length=1, description="Palabra a buscar en las transcripciones"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Busca transcripciones que contengan la palabra especificada.
    
    - **palabra**: Palabra o frase a buscar en las transcripciones
    
    Retorna hasta 10 resultados por canal, ordenados cronológicamente.
    """
    try:
        transcripciones = await search_service.buscar_transcripciones(palabra)
        
        # Convertir entidades de dominio a schemas de respuesta
        resultados = [
            TranscripcionResponse(
                texto=t.texto,
                canal=t.canal,
                name=t.name,
                timestamp=t.timestamp,
                service=t.service,
                channel_id=t.channel_id
            )
            for t in transcripciones
        ]
        
        return BusquedaResponse(resultados=resultados)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/transcripcionClip", response_model=TranscripcionClipResponse)
async def obtener_transcripcion(
    canal: str = Query(..., min_length=1, description="Canal del video"),
    timestamp: str = Query(..., min_length=1, description="Timestamp del clip"),
    duracion_segundos: int = Query(90, ge=1, le=300, description="Duración del clip en segundos"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Obtiene la transcripción concatenada de un clip específico.
    
    - **canal**: Nombre del canal
    - **timestamp**: Timestamp de inicio del clip en formato ISO 8601
    - **duracion_segundos**: Duración del clip (por defecto 90 segundos, máximo 300)
    
    Retorna el texto concatenado de todas las transcripciones en el rango de tiempo.
    """
    try:
        texto_concatenado = await search_service.obtener_transcripcion_clip(
            canal, timestamp, duracion_segundos
        )
        
        if not texto_concatenado:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron transcripciones para el clip especificado"
            )
        
        return TranscripcionClipResponse(
            texto=texto_concatenado,
            canal=canal,
            timestamp=timestamp
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")