"""
Servicio de búsqueda de transcripciones
"""
from typing import List, Optional

from backend.repositories.base import TranscripcionRepositoryInterface, VideoRepositoryInterface
from backend.models.domain import Transcripcion


class SearchService:
    """Servicio para manejar búsquedas de transcripciones"""

    def __init__(
        self,
        transcripcion_repo: TranscripcionRepositoryInterface,
        video_repo: Optional[VideoRepositoryInterface] = None
    ):
        self.transcripcion_repo = transcripcion_repo
        self.video_repo = video_repo
    
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
        Obtiene el texto concatenado de transcripciones en un clip.

        MEJORADO: Ahora usa el rango temporal real del video del file system
        en lugar de asumir múltiplos de 90 segundos.

        Args:
            canal: Canal del video
            timestamp: Timestamp del clip
            duracion_segundos: Duración del clip en segundos (solo se usa como fallback)

        Returns:
            Texto concatenado de las transcripciones
        """
        if not canal or not timestamp:
            raise ValueError("Canal y timestamp son requeridos")

        # Intentar obtener el rango temporal real del video
        transcripciones = []

        if self.video_repo:
            try:
                rango = await self.video_repo.obtener_rango_temporal_video(canal, timestamp)

                if rango:
                    timestamp_inicio, timestamp_fin = rango

                    # Usar el nuevo método con rango específico
                    if hasattr(self.transcripcion_repo, 'obtener_transcripciones_por_rango_temporal'):
                        transcripciones = await self.transcripcion_repo.obtener_transcripciones_por_rango_temporal(
                            canal, timestamp_inicio, timestamp_fin
                        )
                    else:
                        # Fallback si el repo no tiene el método nuevo
                        transcripciones = await self.transcripcion_repo.obtener_transcripciones_por_clip(
                            canal, timestamp, duracion_segundos
                        )
                else:
                    # No se encontró video, usar método de fallback
                    transcripciones = await self.transcripcion_repo.obtener_transcripciones_por_clip(
                        canal, timestamp, duracion_segundos
                    )

            except Exception:
                # Error obteniendo rango temporal, usar método de fallback
                transcripciones = await self.transcripcion_repo.obtener_transcripciones_por_clip(
                    canal, timestamp, duracion_segundos
                )
        else:
            # Si no hay video_repo, usar el método antiguo
            transcripciones = await self.transcripcion_repo.obtener_transcripciones_por_clip(
                canal, timestamp, duracion_segundos
            )

        # Concatenar todos los textos
        texto_concatenado = " ".join([t.texto for t in transcripciones if t.texto])

        return texto_concatenado