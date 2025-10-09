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
        """
        Obtiene TODAS las transcripciones del video que contiene el timestamp dado.

        NOTA: Este método ahora es un fallback. Lo ideal es usar
        obtener_transcripciones_por_rango_temporal() con el rango real del video.
        """

        t_seleccionado = parse_timestamp(timestamp)

        # FALLBACK: Calcular el rango asumiendo videos de duración fija
        # Esto solo se usa si no se puede obtener el rango real del video
        inicio_epoch = int(t_seleccionado.timestamp())
        inicio_video_epoch = (inicio_epoch // duracion_segundos) * duracion_segundos

        t_inicio = datetime.fromtimestamp(inicio_video_epoch, tz=t_seleccionado.tzinfo)
        t_fin = t_inicio + timedelta(seconds=duracion_segundos)

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

    async def obtener_transcripciones_por_rango_temporal(
        self,
        canal: str,
        timestamp_inicio: str,
        timestamp_fin: str
    ) -> List[Transcripcion]:
        """
        Obtiene TODAS las transcripciones en un rango temporal específico.

        Args:
            canal: Canal del video
            timestamp_inicio: Timestamp de inicio en formato ISO 8601
            timestamp_fin: Timestamp de fin en formato ISO 8601

        Returns:
            Lista de transcripciones ordenadas cronológicamente
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"slug": canal}},
                        {"range": {"@timestamp": {"gte": timestamp_inicio, "lt": timestamp_fin}}}
                    ]
                }
            },
            "sort": [
                {"@timestamp": {"order": "asc"}}  # ASC para mantener orden cronológico
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