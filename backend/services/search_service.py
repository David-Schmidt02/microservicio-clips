"""
Servicio de búsqueda de transcripciones
"""
from typing import List

from backend.repositories.base import TranscripcionRepositoryInterface
from backend.models.domain import Transcripcion


class SearchService:
    """Servicio para manejar búsquedas de transcripciones"""
    
    def __init__(self, transcripcion_repo: TranscripcionRepositoryInterface):
        self.transcripcion_repo = transcripcion_repo
    
    async def buscar_transcripciones(self, palabra: str) -> List[Transcripcion]:
        """
        Busca transcripciones que contengan una palabra
        
        Args:
            palabra: Palabra a buscar
            
        Returns:
            Lista de transcripciones encontradas
        """
        if not palabra or len(palabra.strip()) < 1:
            raise ValueError("La palabra de búsqueda debe tener al menos 1 caracter")
        
        return await self.transcripcion_repo.buscar_transcripciones(palabra.strip())
    
    async def obtener_transcripcion_clip(
        self, 
        canal: str, 
        timestamp: str, 
        duracion_segundos: int = 90
    ) -> str:
        """
        Obtiene el texto concatenado de transcripciones en un clip
        
        Args:
            canal: Canal del video
            timestamp: Timestamp del clip
            duracion_segundos: Duración del clip en segundos
            
        Returns:
            Texto concatenado de las transcripciones
        """
        if not canal or not timestamp:
            raise ValueError("Canal y timestamp son requeridos")
        
        transcripciones = await self.transcripcion_repo.obtener_transcripciones_por_clip(
            canal, timestamp, duracion_segundos
        )
        
        # Concatenar todos los textos
        texto_concatenado = " ".join([t.texto for t in transcripciones if t.texto])
        
        return texto_concatenado