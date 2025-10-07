"""
Utilidades para manejo de tiempo y timestamps
"""
from datetime import datetime, timezone


def parse_timestamp(value: str) -> datetime:
    """
    Convierte un string de timestamp a objeto datetime
    
    Args:
        value: Timestamp en formato ISO 8601
        
    Returns:
        datetime object con timezone
        
    Raises:
        ValueError: Si el timestamp está vacío o es inválido
    """
    if not value:
        raise ValueError("Timestamp vacío")
    
    # Normalizar el timestamp para que sea compatible con isoformat
    normalized = value.replace('Z', '+00:00') if value.endswith('Z') else value
    dt = datetime.fromisoformat(normalized)
    
    # Si no tiene timezone, asumir UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt


def format_timestamp_for_query(dt: datetime) -> str:
    """
    Formatea un datetime para consultas de Elasticsearch
    
    Args:
        dt: datetime object
        
    Returns:
        String en formato ISO 8601 compatible con Elasticsearch
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    iso = dt.isoformat()
    return iso.replace('+00:00', 'Z')