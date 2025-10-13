"""
Esquemas Pydantic para requests y responses de la API
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# === REQUEST SCHEMAS ===

class BusquedaRequest(BaseModel):
    palabra: str = Field(..., min_length=1, description="Palabra a buscar en las transcripciones")


class ConcatenarRequest(BaseModel):
    canal: str = Field(..., description="Canal de los videos")
    videos: List[str] = Field(..., description="Lista de nombres de videos a concatenar")


class TranscripcionClipRequest(BaseModel):
    canal: str = Field(..., description="Canal del video")
    timestamp: str = Field(..., description="Timestamp del clip")
    duracion_segundos: int = Field(90, description="Duración del clip en segundos")


# === RESPONSE SCHEMAS ===

class TranscripcionResponse(BaseModel):
    texto: str
    canal: str # Slug del canal (EJ: "olgaenvivo_")
    name: str # Nombre del canal (EJ: "Olga en Vivo")
    timestamp: str
    service: Optional[str] = None # (EJ: "Soflex1")
    channel_id: Optional[str] = None


class BusquedaResponse(BaseModel):
    resultados: List[TranscripcionResponse]


class VideosResponse(BaseModel):
    videos: List[str]


class TranscripcionClipResponse(BaseModel):
    texto: str
    canal: str
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None


# === INTERNAL SCHEMAS ===

class ElasticsearchHit(BaseModel):
    """Modelo para los hits de Elasticsearch"""
    _source: dict
    _id: Optional[str] = None
    _score: Optional[float] = None


class ElasticsearchResponse(BaseModel):
    """Modelo para la respuesta de Elasticsearch"""
    hits: dict
    aggregations: Optional[dict] = None