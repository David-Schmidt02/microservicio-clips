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
    canal: str = Query(..., min_length=1, description="Canal de los videos"),
    timestamp: str = Query(..., min_length=1, description="Timestamp de referencia"),
    rango: int = Query(3, ge=1, le=10, description="Cantidad de videos a cada lado del timestamp"),
    video_service: VideoService = Depends(get_video_service)
):
    """
    Obtiene una lista de videos vecinos a un timestamp específico.
    
    - **canal**: Nombre del canal
    - **timestamp**: Timestamp de referencia en formato ISO 8601
    - **rango**: Cantidad de videos a obtener a cada lado (por defecto 3, máximo 10)
    
    Retorna una lista de nombres de archivos de video ordenados cronológicamente.
    """
    try:
        print(f"Obteniendo videos para canal: {canal}, timestamp: {timestamp}, rango: {rango}")
        videos = await video_service.obtener_videos_vecinos(canal, timestamp, rango)
        print(f"Videos encontrados: {len(videos)} - {videos[:3] if videos else 'Ninguno'}")
        
        return VideosResponse(videos=videos)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error en obtener_lista_videos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/concatenar")
async def concatenar_videos(
    request: ConcatenarRequest,
    video_service: VideoService = Depends(get_video_service)
):
    """
    Concatena una lista de videos y devuelve el archivo resultante.
    
    - **canal**: Canal de los videos
    - **videos**: Lista de nombres de archivos de video a concatenar
    
    Retorna información sobre el clip generado.
    """
    try:
        print(f"🎬 Concatenando videos - Canal: {request.canal}, Videos: {request.videos}")
        clip_filename = await video_service.concatenar_videos(
            request.canal, 
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
        print(f"❌ Error en concatenar_videos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


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
        output_path = os.path.join(settings.OUTPUT_DIR, clip)
        
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
        # Validar que el archivo tenga extensión .ts
        if not archivo.endswith('.ts'):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos .ts"
            )
        
        # Construir ruta del archivo
        video_path = os.path.join(settings.VIDEO_DIR, canal, archivo)
        
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
        print(f"❌ Error sirviendo video {canal}/{archivo}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")