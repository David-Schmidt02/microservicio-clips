"""
Repositorio para acceso a Elasticsearch
"""
from typing import List
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

from backend.repositories.base import TranscripcionRepositoryInterface
from backend.models.domain import Transcripcion
from backend.config.settings import settings
from backend.utils.time_utils import parse_timestamp, format_timestamp_for_query


class ElasticsearchRepository(TranscripcionRepositoryInterface):
    """Implementación concreta del repositorio de Elasticsearch"""
    
    def __init__(self):
        self.es = Elasticsearch(
            settings.ELASTIC_URL,
            basic_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
            verify_certs=False
        )
        
    async def buscar_transcripciones(self, palabra: str) -> List[Transcripcion]:
        """Busca transcripciones que contengan una palabra"""
        
        # Calcular timestamp de 24 horas atrás
        ahora = datetime.now(settings.TIMEZONE)
        hace_24hs = ahora - timedelta(hours=24)
        ts_24hs = hace_24hs.isoformat()
        
        body = {
            "size": 0,  # No queremos hits directos, solo agregaciones
            "query": {
                "bool": {
                    "must": [
                        {"match": {"text": palabra}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gte": ts_24hs}}}
                    ]
                }
            },
            "aggs": {
                "por_canal": {
                    "terms": {"field": "slug.keyword", "size": 50},
                    "aggs": {
                        "top_transcripciones": {
                            "top_hits": {
                                "size": 10,
                                "sort": [
                                    {"@timestamp": {"order": "desc"}}
                                ]
                            }
                        }
                    }
                }
            }
        }
        
        if "sort" not in body:
            body["sort"] = [{"@timestamp": {"order": "desc"}}]
            
        resultados = self.es.search(index=settings.ELASTICSEARCH_INDEX, body=body)
        buckets = resultados.get("aggregations", {}).get("por_canal", {}).get("buckets", [])
        
        transcripciones = []
        for bucket in buckets:
            top_hits = bucket.get("top_transcripciones", {}).get("hits", {}).get("hits", [])
            for hit in top_hits:
                src = hit.get("_source", {})
                transcripcion = Transcripcion(
                    texto=src.get("text", ""),
                    canal=src.get("slug", ""),
                    name=src.get("name", ""),
                    timestamp=src.get("@timestamp", ""),
                    service=src.get("service", ""),
                    channel_id=src.get("channel_id", "")
                )
                transcripciones.append(transcripcion)
                
        return transcripciones
    
    async def obtener_transcripciones_por_clip(
        self, 
        canal: str, 
        timestamp: str, 
        duracion_segundos: int = 90
    ) -> List[Transcripcion]:
        """Obtiene transcripciones en un rango de tiempo, centrado en el timestamp seleccionado"""
        
        t_seleccionado = parse_timestamp(timestamp)
        
        # Crear un rango que incluya la transcripción seleccionada al inicio
        # Tomamos desde 5 segundos antes hasta 85 segundos después para un total de 90 segundos
        t_inicio = t_seleccionado - timedelta(seconds=5)
        t_fin = t_seleccionado + timedelta(seconds=duracion_segundos - 5)
        
        ts_inicio = format_timestamp_for_query(t_inicio)
        ts_fin = format_timestamp_for_query(t_fin)
        
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"slug": canal}},
                        {"range": {"@timestamp": {"gte": ts_inicio, "lt": ts_fin}}}
                    ]
                }
            },
            "sort": [
                {"@timestamp": {"order": "asc"}}  # ASC para mantener orden cronológico del clip
            ],
            "size": 100  # Asegurar que obtenemos suficientes resultados
        }
        
        resultados = self.es.search(index=settings.ELASTICSEARCH_INDEX, body=body)
        
        transcripciones = []
        for hit in resultados.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            transcripcion = Transcripcion(
                texto=src.get("text", ""),
                canal=src.get("slug", ""),
                name=src.get("name", ""),
                timestamp=src.get("@timestamp", ""),
                service=src.get("service", ""),
                channel_id=src.get("channel_id", "")
            )
            transcripciones.append(transcripcion)
            
        return transcripciones