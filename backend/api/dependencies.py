"""
Dependencias para inyección de dependencias de FastAPI
"""
from fastapi import Depends

from backend.repositories.elasticsearch_repo import ElasticsearchRepository
from backend.repositories.file_system_repo import FileSystemRepository
from backend.services.search_service import SearchService
from backend.services.video_service import VideoService
from backend.controllers.search_controller import SearchController
from backend.controllers.video_controller import VideoController


# === REPOSITORIOS ===

def get_elasticsearch_repo() -> ElasticsearchRepository:
    """Dependencia para obtener el repositorio de Elasticsearch"""
    return ElasticsearchRepository()


def get_filesystem_repo() -> FileSystemRepository:
    """Dependencia para obtener el repositorio del sistema de archivos"""
    return FileSystemRepository()


# === SERVICIOS ===

def get_search_service(
    transcripcion_repo: ElasticsearchRepository = Depends(get_elasticsearch_repo),
    video_repo: FileSystemRepository = Depends(get_filesystem_repo)
) -> SearchService:
    """
    Dependencia para obtener el servicio de búsqueda.

    Ahora también inyecta el video_repo para poder obtener rangos temporales reales.
    """
    return SearchService(transcripcion_repo, video_repo)


def get_video_service(
    video_repo: FileSystemRepository = Depends(get_filesystem_repo)
) -> VideoService:
    """Dependencia para obtener el servicio de videos"""
    return VideoService(video_repo)


# === CONTROLLERS ===

def get_search_controller(
    search_service: SearchService = Depends(get_search_service)
) -> SearchController:
    """Dependencia para obtener el controller de búsqueda"""
    return SearchController(search_service)


def get_video_controller(
    video_service: VideoService = Depends(get_video_service)
) -> VideoController:
    """Dependencia para obtener el controller de videos"""
    return VideoController(video_service)