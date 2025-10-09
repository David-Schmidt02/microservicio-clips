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
    palabra: str = Query(..., min_length=1, max_length=200, description="Palabra a buscar en las transcripciones"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Busca transcripciones que contengan la palabra especificada.

    - **palabra**: Palabra o frase a buscar en las transcripciones (máximo 200 caracteres)

    Retorna hasta 10 resultados por canal, ordenados cronológicamente.
    """
    try:
        # VALIDACIÓN: Sanitizar entrada para prevenir inyección en queries de ElasticSearch
        if not palabra or not palabra.strip():
            raise HTTPException(status_code=400, detail="La palabra de búsqueda no puede estar vacía")

        transcripciones = await search_service.buscar_transcripciones(palabra.strip())
        
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
    canal: str = Query(..., min_length=1, max_length=100, description="Canal del video"),
    timestamp: str = Query(..., min_length=1, description="Timestamp del clip"),
    duracion_segundos: int = Query(90, ge=1, le=300, description="Duración del clip en segundos"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Obtiene la transcripción concatenada de un clip específico.

    - **canal**: Nombre del canal (máximo 100 caracteres)
    - **timestamp**: Timestamp de inicio del clip en formato ISO 8601
    - **duracion_segundos**: Duración del clip (por defecto 90 segundos, máximo 300)

    Retorna el texto concatenado de todas las transcripciones en el rango de tiempo.
    """
    try:
        # VALIDACIÓN: Prevenir path traversal y caracteres inválidos
        if '..' in canal or '/' in canal or '\\' in canal:
            raise HTTPException(status_code=400, detail="Nombre de canal contiene caracteres inválidos")

        texto_concatenado = await search_service.obtener_transcripcion_clip(
            canal.strip(), timestamp, duracion_segundos
        )
        
        # Si no hay texto, devolver respuesta válida con mensaje informativo
        if not texto_concatenado:
            texto_concatenado = "No hay transcripciones disponibles para este periodo de tiempo"
        
        return TranscripcionClipResponse(
            texto=texto_concatenado,
            canal=canal,
            timestamp=timestamp
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")