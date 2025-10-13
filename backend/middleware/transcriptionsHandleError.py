"""
Middleware para manejo de errores relacionados con transcripciones
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import traceback


async def transcriptions_error_handler(request: Request, call_next):
    """
    Middleware para capturar y manejar errores relacionados con transcripciones.

    Maneja:
    - Errores de Elasticsearch
    - Errores de validacion (ValueError)
    - Errores HTTP ya formateados
    - Errores genericos
    """
    try:
        response = await call_next(request)
        return response

    except HTTPException:
        # Re-lanzar HTTPException para que FastAPI lo maneje
        raise

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

    except Exception as e:
        # Capturar errores de Elasticsearch primero
        if 'elasticsearch' in str(type(e).__module__).lower():
            print(f"[ERROR ELASTICSEARCH] {str(e)}")
            print(traceback.format_exc())
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Error de conexion con el sistema de busqueda",
                    "error_type": "elasticsearch_error"
                }
            )

        # Errores genericos no capturados
        print(f"[ERROR INTERNO] {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor al procesar transcripciones",
                "error_type": "internal_error"
            }
        )
