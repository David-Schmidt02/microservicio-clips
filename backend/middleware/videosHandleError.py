"""
Middleware para manejo de errores relacionados con videos y clips
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import traceback


async def videos_error_handler(request: Request, call_next):
    """
    Middleware para capturar y manejar errores relacionados con videos.

    Maneja:
    - Errores de archivos no encontrados (FileNotFoundError)
    - Errores de validacion (ValueError)
    - Errores de FFmpeg (RuntimeError)
    - Errores HTTP ya formateados
    - Errores genericos
    """
    try:
        response = await call_next(request)
        return response

    except HTTPException:
        # Re-lanzar HTTPException para que FastAPI lo maneje
        raise

    except FileNotFoundError as e:
        # Errores de archivos no encontrados
        print(f"[ERROR ARCHIVO NO ENCONTRADO] {str(e)}")
        return JSONResponse(
            status_code=404,
            content={
                "detail": f"Recurso no encontrado: {str(e)}",
                "error_type": "file_not_found"
            }
        )

    except ValueError as e:
        # Errores de validacion desde services/repositories
        print(f"[ERROR VALIDACION] {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(e),
                "error_type": "validation_error"
            }
        )

    except RuntimeError as e:
        # Errores de FFmpeg u operaciones de video
        print(f"[ERROR PROCESAMIENTO VIDEO] {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Error al procesar video: {str(e)}",
                "error_type": "video_processing_error"
            }
        )

    except Exception as e:
        # Errores genericos no capturados
        print(f"[ERROR INTERNO] {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor al procesar videos",
                "error_type": "internal_error"
            }
        )
