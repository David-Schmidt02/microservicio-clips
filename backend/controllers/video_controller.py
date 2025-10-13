"""
Controller para manejar operaciones de videos y clips
"""
import os
from typing import List
from fastapi import HTTPException
from fastapi.responses import FileResponse

from backend.services.video_service import VideoService
from backend.models.schemas import VideosResponse, ConcatenarRequest
from backend.config.settings import settings


class VideoController:
    """Controller para operaciones de videos y clips"""

    def __init__(self, video_service: VideoService):
        self.video_service = video_service

    async def obtener_lista_videos(
        self,
        canal: str,
        timestamp: str,
        rango: int
    ) -> VideosResponse:
        """
        Obtiene una lista de videos vecinos a un timestamp específico.

        Args:
            canal: Nombre del canal
            timestamp: Timestamp de referencia
            rango: Cantidad de videos a cada lado

        Returns:
            VideosResponse con la lista de videos

        Raises:
            HTTPException: Si la validación falla o hay errores
        """
        # VALIDACIÓN: Prevenir path traversal y caracteres inválidos
        if '..' in canal or '/' in canal or '\\' in canal:
            raise HTTPException(
                status_code=400,
                detail="Nombre de canal contiene caracteres inválidos"
            )

        print("Parámetros recibidos - canal:", canal, "timestamp:", timestamp, "rango:", rango)

        # Llamar al servicio (los errores se propagan al middleware)
        videos = await self.video_service.obtener_videos_vecinos(canal.strip(), timestamp, rango)

        print("Videos encontrados:", videos)
        return VideosResponse(videos=videos)

    async def concatenar_videos(self, request: ConcatenarRequest) -> dict:
        """
        Concatena una lista de videos y devuelve el archivo resultante.

        Args:
            request: Request con canal y lista de videos

        Returns:
            Dict con información del clip generado

        Raises:
            HTTPException: Si la validación falla o hay errores
        """
        # VALIDACIÓN: Limitar cantidad de videos a concatenar
        if len(request.videos) > 20:
            raise HTTPException(
                status_code=400,
                detail="Máximo 20 videos por concatenación"
            )

        if len(request.videos) == 0:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un video"
            )

        # VALIDACIÓN: Prevenir path traversal en canal
        if '..' in request.canal or '/' in request.canal or '\\' in request.canal:
            raise HTTPException(
                status_code=400,
                detail="Nombre de canal contiene caracteres inválidos"
            )

        # Llamar al servicio (los errores se propagan al middleware)
        clip_filename = await self.video_service.concatenar_videos(
            request.canal.strip(),
            request.videos
        )

        return {
            "message": "Videos concatenados exitosamente",
            "clip_filename": clip_filename,
            "download_url": f"/clips/descargar?clip={clip_filename}"
        }

    async def descargar_clip(self, clip: str) -> FileResponse:
        """
        Descarga un clip previamente generado.

        Args:
            clip: Nombre del archivo de clip

        Returns:
            FileResponse con el archivo de video

        Raises:
            HTTPException: Si la validación falla o hay errores
        """
        # VALIDACIÓN: Prevenir path traversal y acceso a archivos fuera de OUTPUT_DIR
        if not clip or not isinstance(clip, str):
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo inválido"
            )

        if '..' in clip or '/' in clip or '\\' in clip:
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo contiene caracteres inválidos"
            )

        if not clip.endswith('.mp4'):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos .mp4"
            )

        output_path = os.path.join(settings.OUTPUT_DIR, clip)

        # Verificar que el path resuelto esté dentro de OUTPUT_DIR (prevenir path traversal)
        if not os.path.abspath(output_path).startswith(os.path.abspath(settings.OUTPUT_DIR)):
            raise HTTPException(
                status_code=400,
                detail="Ruta de archivo inválida"
            )

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

    async def servir_video(self, canal: str, archivo: str) -> FileResponse:
        """
        Sirve un archivo de video original para reproducción.

        Args:
            canal: Nombre del canal
            archivo: Nombre del archivo de video

        Returns:
            FileResponse con el archivo de video

        Raises:
            HTTPException: Si la validación falla o hay errores
        """
        # VALIDACIÓN: Prevenir path traversal
        if not canal or not isinstance(canal, str):
            raise HTTPException(
                status_code=400,
                detail="Nombre de canal inválido"
            )

        if '..' in canal or '/' in canal or '\\' in canal:
            raise HTTPException(
                status_code=400,
                detail="Nombre de canal contiene caracteres inválidos"
            )

        if not archivo or not isinstance(archivo, str):
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo inválido"
            )

        if '..' in archivo or '/' in archivo or '\\' in archivo:
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo contiene caracteres inválidos"
            )

        # Validar que el archivo tenga extensión .ts
        if not archivo.endswith('.ts'):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos .ts"
            )

        # Construir ruta del archivo
        video_path = os.path.join(settings.VIDEO_DIR, canal, archivo)

        # Verificar que el path resuelto esté dentro de VIDEO_DIR (prevenir path traversal)
        if not os.path.abspath(video_path).startswith(os.path.abspath(settings.VIDEO_DIR)):
            raise HTTPException(
                status_code=400,
                detail="Ruta de archivo inválida"
            )

        if not os.path.exists(video_path):
            raise HTTPException(
                status_code=404,
                detail="Archivo de video no encontrado"
            )

        # Para archivos .ts, convertir a mp4 para mejor compatibilidad con navegadores
        if archivo.endswith('.ts'):
            # Crear archivo MP4 temporal
            temp_mp4 = os.path.join(settings.OUTPUT_DIR, f"temp_{archivo.replace('.ts', '.mp4')}")

            # Convertir solo si no existe o es más antiguo que el archivo original
            if not os.path.exists(temp_mp4) or os.path.getmtime(video_path) > os.path.getmtime(temp_mp4):
                import subprocess
                cmd = [
                    settings.FFMPEG_BIN,
                    '-i', video_path,
                    '-c', 'copy',  # Solo remux, no re-encodificar
                    '-f', 'mp4',
                    '-y',  # Sobrescribir si existe
                    temp_mp4
                ]

                try:
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
                except subprocess.CalledProcessError:
                    # Si falla la conversión, servir el archivo original
                    return FileResponse(
                        video_path,
                        media_type="video/mp2t",
                        headers={
                            "Accept-Ranges": "bytes",
                            "Cache-Control": "public, max-age=3600"
                        }
                    )

            return FileResponse(
                temp_mp4,
                media_type="video/mp4",
                headers={
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "public, max-age=3600"
                }
            )

        return FileResponse(
            video_path,
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600"
            }
        )
