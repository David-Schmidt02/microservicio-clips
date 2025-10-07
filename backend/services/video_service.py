"""
Servicio de manejo de videos y clips
"""
from typing import List

from backend.repositories.base import VideoRepositoryInterface


class VideoService:
    """Servicio para manejar operaciones con videos"""
    
    def __init__(self, video_repo: VideoRepositoryInterface):
        self.video_repo = video_repo
    
    async def obtener_videos_vecinos(
        self, 
        canal: str, 
        timestamp: str, 
        rango: int = 3
    ) -> List[str]:
        """
        Obtiene videos vecinos a un timestamp específico
        
        Args:
            canal: Canal de los videos
            timestamp: Timestamp de referencia
            rango: Cantidad de videos a cada lado
            
        Returns:
            Lista de nombres de archivos de video
        """
        if not canal or not timestamp:
            raise ValueError("Canal y timestamp son requeridos")
        
        if rango < 1:
            raise ValueError("El rango debe ser mayor a 0")
        
        return await self.video_repo.obtener_videos_vecinos(canal, timestamp, rango)
    
    async def concatenar_videos(self, canal: str, videos: List[str]) -> str:
        """
        Concatena una lista de videos
        
        Args:
            canal: Canal de los videos
            videos: Lista de nombres de archivos de video
            
        Returns:
            Nombre del archivo de clip generado
        """
        if not canal:
            raise ValueError("Canal es requerido")
        
        if not videos or len(videos) == 0:
            raise ValueError("Debe proporcionar al menos un video para concatenar")
        
        # Validar que los nombres de video no estén vacíos
        videos_validos = [v.strip() for v in videos if v.strip()]
        if len(videos_validos) != len(videos):
            raise ValueError("Todos los nombres de video deben ser válidos")
        
        return await self.video_repo.concatenar_videos(canal, videos_validos)