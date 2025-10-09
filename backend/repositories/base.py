"""
Repositorio base para definir interfaces comunes
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from backend.models.domain import Transcripcion


class TranscripcionRepositoryInterface(ABC):
    """Interface para repositorios de transcripciones"""
    
    @abstractmethod
    async def buscar_transcripciones(self, palabra: str) -> List[Transcripcion]:
        """Busca transcripciones que contengan una palabra"""
        pass
    
    @abstractmethod
    async def obtener_transcripciones_por_clip(
        self, 
        canal: str, 
        timestamp: str, 
        duracion_segundos: int = 90
    ) -> List[Transcripcion]:
        """Obtiene transcripciones en un rango de tiempo"""
        pass


class VideoRepositoryInterface(ABC):
    """Interface para repositorios de videos"""

    @abstractmethod
    async def obtener_videos_vecinos(
        self,
        canal: str,
        timestamp: str,
        rango: int = 3
    ) -> List[str]:
        """Obtiene videos vecinos a un timestamp"""
        pass

    @abstractmethod
    async def concatenar_videos(self, canal: str, videos: List[str]) -> str:
        """Concatena una lista de videos y retorna la ruta del resultado"""
        pass

    @abstractmethod
    async def obtener_rango_temporal_video(
        self,
        canal: str,
        timestamp: str
    ) -> Optional[tuple[str, str]]:
        """
        Encuentra el video que contiene el timestamp y retorna su rango temporal.

        Returns:
            Tupla (timestamp_inicio, timestamp_fin) en formato ISO 8601, o None si no se encuentra
        """
        pass