"""
Configuración centralizada de la aplicación usando Pydantic Settings
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import pytz

# Cargar variables de entorno desde el archivo .env en la carpeta config
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / "config" / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    
    Las variables se pueden definir en:
    1. Variables de entorno del sistema
    2. Archivo .env en backend/config/
    3. Valores por defecto definidos aquí
    """
    
    # === INFORMACIÓN DEL PROYECTO ===
    PROJECT_NAME: str = Field(default="Microservicio de Clips", description="Nombre del proyecto")
    VERSION: str = Field(default="1.0.0", description="Versión de la API")
    DESCRIPTION: str = Field(
        default="API para búsqueda y concatenación de clips de video basados en transcripciones",
        description="Descripción del proyecto"
    )
    
    # === CONFIGURACIÓN DE LA API ===
    API_V1_PREFIX: str = Field(default="/api/v1", description="Prefijo para la API v1")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"], 
        description="Orígenes permitidos para CORS"
    )
    
    # === CONFIGURACIÓN DE ELASTICSEARCH ===
    ELASTIC_URL: str = Field(
        default="https://172.20.100.40:9200",
        description="URL de conexión a Elasticsearch"
    )
    ELASTIC_USER: str = Field(
        default="elastic",
        description="Usuario de Elasticsearch"
    )
    ELASTIC_PASSWORD: str = Field(
        default="password",
        description="Contraseña de Elasticsearch"
    )
    ELASTICSEARCH_INDEX: str = Field(
        default="streaming_tv",
        description="Índice de Elasticsearch para las transcripciones"
    )

    #ELASTICSEARCH_INDEX: str = Field(
    #    default="streaming_tv_test",  # ← CAMBIO AQUÍ
    #    description="Índice de Elasticsearch para las transcripciones (DESARROLLO)"
    #)
        
    # Directorios
    VIDEO_DIR: str = "canales"
    OUTPUT_DIR: str = "clips"
    
    # FFmpeg
    FFMPEG_BIN: str = "ffmpeg"
    
    # Timezone
    
    # === CONFIGURACIÓN DE ARCHIVOS Y DIRECTORIOS ===
    VIDEO_DIR: str = Field(
        default=str(BASE_DIR.parent / "canales"),
        description="Directorio donde se almacenan los videos por canal"
    )
    OUTPUT_DIR: str = Field(
        default=str(BASE_DIR.parent / "clips"),
        description="Directorio donde se guardan los clips generados"
    )
    
    # === CONFIGURACIÓN DE FFMPEG ===
    FFMPEG_BIN: str = Field(
        default="ffmpeg",
        description="Ruta al ejecutable de FFmpeg"
    )
    
    # === CONFIGURACIÓN DE ZONA HORARIA ===
    TIMEZONE_NAME: str = Field(
        default="America/Argentina/Buenos_Aires",
        description="Zona horaria para cálculos de tiempo"
    )
    
    @property
    def TIMEZONE(self):
        """Retorna el objeto de zona horaria pytz"""
        return pytz.timezone(self.TIMEZONE_NAME)
    
    # === CONFIGURACIÓN DE BÚSQUEDAS ===
    MAX_RESULTS_PER_CHANNEL: int = Field(
        default=10,
        description="Máximo número de resultados por canal en búsquedas"
    )
    DEFAULT_CLIP_DURATION: int = Field(
        default=90,
        description="Duración por defecto de los clips en segundos"
    )
    MAX_CLIP_DURATION: int = Field(
        default=300,
        description="Duración máxima permitida para clips en segundos"
    )
    DEFAULT_VIDEO_RANGE: int = Field(
        default=3,
        description="Cantidad por defecto de videos vecinos a obtener"
    )
    MAX_VIDEO_RANGE: int = Field(
        default=10,
        description="Cantidad máxima de videos vecinos permitida"
    )
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """
    Función para obtener la configuración.
    Útil para inyección de dependencias en FastAPI.
    """
    return settings