"""
Controller para manejar operaciones de búsqueda
"""
from typing import List
from fastapi import HTTPException

from backend.services.search_service import SearchService
from backend.models.schemas import BusquedaResponse, TranscripcionResponse, TranscripcionClipResponse


class SearchController:
    """Controller para operaciones de búsqueda de transcripciones"""

    def __init__(self, search_service: SearchService):
        self.search_service = search_service

    async def buscar_palabra(self, palabra: str) -> BusquedaResponse:
        """
        Busca transcripciones que contengan la palabra especificada.

        Args:
            palabra: Palabra a buscar en las transcripciones

        Returns:
            BusquedaResponse con los resultados

        Raises:
            HTTPException: Si la validación falla o hay errores
        """
        # VALIDACIÓN: Sanitizar entrada para prevenir inyección en queries de ElasticSearch
        if not palabra or not palabra.strip():
            raise HTTPException(
                status_code=400,
                detail="La palabra de búsqueda no puede estar vacía"
            )

        # Llamar al servicio (los errores se propagan al middleware)
        transcripciones = await self.search_service.buscar_transcripciones(palabra.strip())

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

    async def obtener_transcripcion_clip(
        self,
        canal: str,
        timestamp: str,
        duracion_segundos: int
    ) -> TranscripcionClipResponse:
        """
        Obtiene la transcripción concatenada de un clip específico.

        Args:
            canal: Nombre del canal
            timestamp: Timestamp de inicio del clip
            duracion_segundos: Duración del clip en segundos

        Returns:
            TranscripcionClipResponse con el texto concatenado

        Raises:
            HTTPException: Si la validación falla o hay errores
        """
        # VALIDACIÓN: Prevenir path traversal y caracteres inválidos
        if '..' in canal or '/' in canal or '\\' in canal:
            raise HTTPException(
                status_code=400,
                detail="Nombre de canal contiene caracteres inválidos"
            )

        # Llamar al servicio (los errores se propagan al middleware)
        texto_concatenado = await self.search_service.obtener_transcripcion_clip(
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
