"""
Endpoints de mantenimiento y administración
"""
from fastapi import APIRouter, Query

from backend.services.cleanup_service import CleanupService
from backend.scheduler.instances import cleanup_scheduler

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/cleanup")
async def limpiar_clips_antiguos(
    max_age_hours: int = Query(1, ge=1, le=24, description="Edad máxima en horas")
):
    """
    Limpia clips generados hace más de X horas.

    - **max_age_hours**: Edad máxima en horas (por defecto 1, máximo 24)

    Retorna cantidad de archivos eliminados.
    """
    cleanup_service = CleanupService()
    cantidad, archivos = cleanup_service.limpiar_clips_antiguos(max_age_hours)

    return {
        "message": f"Limpieza completada: {cantidad} archivo(s) eliminado(s)",
        "cantidad_eliminados": cantidad,
        "archivos_eliminados": archivos
    }


@router.get("/stats")
async def obtener_estadisticas():
    """
    Obtiene estadísticas sobre clips almacenados.

    Retorna información sobre cantidad, tamaño total, etc.
    """
    cleanup_service = CleanupService()
    stats = cleanup_service.obtener_estadisticas_clips()

    return stats


@router.get("/scheduler/status")
async def obtener_estado_scheduler():
    """
    Obtiene el estado del scheduler de limpieza automática.

    Retorna información sobre si está activo, próxima ejecución, etc.
    """
    estado = cleanup_scheduler.obtener_estado()
    return estado
