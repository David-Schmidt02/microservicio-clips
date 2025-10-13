"""
Endpoints relacionados con videos y clips
"""
import os
from fastapi import APIRouter, Depends, Query, Body, HTTPException, Path
from fastapi.responses import FileResponse
from typing import List

from backend.services.video_service import VideoService
from backend.models.schemas import VideosResponse, ConcatenarRequest
from backend.api.dependencies import get_video_service
from backend.config.settings import settings

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/videos", response_model=VideosResponse)
async def obtener_lista_videos(
    canal: str = Query(..., min_length=1, max_length=100, description="Canal de los videos"),
    timestamp: str = Query(..., min_length=1, description="Timestamp de referencia"),
    rango: int = Query(3, ge=1, le=10, description="Cantidad de videos a cada lado del timestamp"),
    video_service: VideoService = Depends(get_video_service)
):
    """
    Obtiene una lista de videos vecinos a un timestamp específico.

    - **canal**: Nombre del canal (máximo 100 caracteres)
    - **timestamp**: Timestamp de referencia en formato ISO 8601
    - **rango**: Cantidad de videos a obtener a cada lado (por defecto 3, máximo 10)

    Retorna una lista de nombres de archivos de video ordenados cronológicamente.
    """
    try:
        # VALIDACIÓN: Prevenir path traversal y caracteres inválidos
        if '..' in canal or '/' in canal or '\\' in canal:
            raise HTTPException(status_code=400, detail="Nombre de canal contiene caracteres inválidos")
        print("Parámetros recibidos - canal:", canal, "timestamp:", timestamp, "rango:", rango)

        videos = await video_service.obtener_videos_vecinos(canal.strip(), timestamp, rango)
        print("Videos encontrados:", videos)
        return VideosResponse(videos=videos)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/concatenar")
async def concatenar_videos(
    request: ConcatenarRequest,
    video_service: VideoService = Depends(get_video_service)
):
    """
    Concatena una lista de videos y devuelve el archivo resultante.

    - **canal**: Canal de los videos
    - **videos**: Lista de nombres de archivos de video a concatenar (máximo 20)

    Retorna información sobre el clip generado.
    """
    try:
        # VALIDACIÓN: Limitar cantidad de videos a concatenar
        if len(request.videos) > 20:
            raise HTTPException(status_code=400, detail="Máximo 20 videos por concatenación")

        if len(request.videos) == 0:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un video")

        # VALIDACIÓN: Prevenir path traversal en canal
        if '..' in request.canal or '/' in request.canal or '\\' in request.canal:
            raise HTTPException(status_code=400, detail="Nombre de canal contiene caracteres inválidos")

        clip_filename = await video_service.concatenar_videos(
            request.canal.strip(),
            request.videos
        )
        
        return {
            "message": "Videos concatenados exitosamente",
            "clip_filename": clip_filename,
            "download_url": f"/clips/descargar?clip={clip_filename}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/descargar")
async def descargar_clip(
    clip: str = Query(..., description="Nombre del archivo de clip a descargar")
):
    """
    Descarga un clip previamente generado.

    - **clip**: Nombre del archivo de clip (incluye extensión .mp4)

    Retorna el archivo de video para descarga directa.
    """
    try:
        # VALIDACIÓN: Prevenir path traversal y acceso a archivos fuera de OUTPUT_DIR
        if not clip or not isinstance(clip, str):
            raise HTTPException(status_code=400, detail="Nombre de archivo inválido")

        if '..' in clip or '/' in clip or '\\' in clip:
            raise HTTPException(status_code=400, detail="Nombre de archivo contiene caracteres inválidos")

        if not clip.endswith('.mp4'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos .mp4")

        output_path = os.path.join(settings.OUTPUT_DIR, clip)

        # Verificar que el path resuelto esté dentro de OUTPUT_DIR (prevenir path traversal)
        if not os.path.abspath(output_path).startswith(os.path.abspath(settings.OUTPUT_DIR)):
            raise HTTPException(status_code=400, detail="Ruta de archivo inválida")

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
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/video/{canal}/{archivo}")
async def servir_video(
    canal: str = Path(..., description="Nombre del canal"),
    archivo: str = Path(..., description="Nombre del archivo de video")
):
    """
    Sirve un archivo de video original para reproducción.

    - **canal**: Nombre del canal
    - **archivo**: Nombre del archivo de video (.ts)

    Retorna el archivo de video para streaming.
    """
    try:
        # VALIDACIÓN: Prevenir path traversal
        if not canal or not isinstance(canal, str):
            raise HTTPException(status_code=400, detail="Nombre de canal inválido")

        if '..' in canal or '/' in canal or '\\' in canal:
            raise HTTPException(status_code=400, detail="Nombre de canal contiene caracteres inválidos")

        if not archivo or not isinstance(archivo, str):
            raise HTTPException(status_code=400, detail="Nombre de archivo inválido")

        if '..' in archivo or '/' in archivo or '\\' in archivo:
            raise HTTPException(status_code=400, detail="Nombre de archivo contiene caracteres inválidos")

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
            raise HTTPException(status_code=400, detail="Ruta de archivo inválida")
        
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
                except subprocess.CalledProcessError as e:
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
            media_type="video/mp4",  # Asumir MP4 para otros archivos
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Error interno del servidor")