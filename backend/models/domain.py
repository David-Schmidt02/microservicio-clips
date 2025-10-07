"""
Modelos de dominio para la aplicación
"""
from datetime import datetime
from typing import Optional


class Transcripcion:
    """Entidad de dominio para una transcripción"""
    
    def __init__(
        self,
        texto: str,
        canal: str,
        name: str,
        timestamp: str,
        service: Optional[str] = None,
        channel_id: Optional[str] = None
    ):
        self.texto = texto
        self.canal = canal
        self.name = name
        self.timestamp = timestamp
        self.service = service
        self.channel_id = channel_id

    def to_dict(self) -> dict:
        return {
            "texto": self.texto,
            "canal": self.canal,
            "name": self.name,
            "timestamp": self.timestamp,
            "service": self.service,
            "channel_id": self.channel_id
        }


class Video:
    """Entidad de dominio para un video"""
    
    def __init__(
        self,
        nombre: str,
        canal: str,
        timestamp: str,
        ruta: Optional[str] = None
    ):
        self.nombre = nombre
        self.canal = canal
        self.timestamp = timestamp
        self.ruta = ruta

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "canal": self.canal,
            "timestamp": self.timestamp,
            "ruta": self.ruta
        }