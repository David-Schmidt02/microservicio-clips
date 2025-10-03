from transcripciones_mock import objetos_transcripciones
import os
from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch

from config import ELASTIC_PASSWORD, ELASTIC_URL, ELASTIC_USER


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise ValueError("Timestamp vacío")
    normalized = value.replace('Z', '+00:00') if value.endswith('Z') else value
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _format_timestamp_for_query(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat()
    return iso.replace('+00:00', 'Z')

class ElasticSearchController:

    def __init__(self):
        self.es = Elasticsearch(
            ELASTIC_URL,
            basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
            verify_certs=False
        )

    def obtener_transcripciones(self, palabra: str):
        # Usar agregaciones para obtener hasta 10 resultados por canal
        # body = body_buscar
        body = {
            "size": 0,  # No queremos hits directos, solo agregaciones
            "query": {
                "match": {
                    "text": palabra
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
                                    {"@timestamp": {"order": "asc"}}
                                ]
                            }
                        }
                    }
                }
            }
        }
        # Agregar sort por @timestamp ascendente en todas las búsquedas
        if "sort" not in body:
            body["sort"] = [{"@timestamp": {"order": "asc"}}]
        resultados = self.es.search(index="streaming_tv", body=body)
        buckets = resultados.get("aggregations", {}).get("por_canal", {}).get("buckets", [])
        hits_filtrados = []
        for bucket in buckets:
            top_hits = bucket.get("top_transcripciones", {}).get("hits", {}).get("hits", [])
            hits_filtrados.extend(top_hits)
        # Mapeo para frontend: solo campos relevantes
        resultados_filtrados = {"hits": {"hits": hits_filtrados}}
        mapeados = self.mapear_resultados(resultados_filtrados)
        return mapeados
    
    def _agrupar_por_canal(self, hits):
        canales = {}
        hits_filtrados = []
        for hit in hits:
            src = hit.get("_source", {})
            canal = src.get("slug", "")
            if canal not in canales:
                canales[canal] = []
            if len(canales[canal]) < 10:
                canales[canal].append(hit)
        for lista in canales.values():
            hits_filtrados.extend(lista)
        return hits_filtrados

    def mapear_resultados(self, resultados):
        # Mapeo para frontend: solo campos relevantes
        mapeados = []
        for hit in resultados.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            mapeados.append({
                "texto": src.get("text", ""),
                "canal": src.get("slug", ""),
                "timestamp": src.get("@timestamp", ""),
                "video_id": src.get("video_id", ""),
                "service": src.get("service", ""),
                "channel_id": src.get("channel_id", "")
            })
        return mapeados
    
    def obtener_transcripciones_por_clip(self, canal: str, timestamp: str, duracion_segundos: int = 90):
        t0 = _parse_timestamp(timestamp)
        t1 = t0 + timedelta(seconds=duracion_segundos)
        ts_inicio = _format_timestamp_for_query(t0)
        ts_fin = _format_timestamp_for_query(t1)
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
                {"@timestamp": {"order": "asc"}}
            ]
        }
        resultados = self.es.search(index="streaming_tv", body=body)
        return self.mapear_resultados(resultados)
    

class TranscripcionesHandler:
    def __init__(self):
        self.transcripciones = objetos_transcripciones
        self.elastic_search = ElasticSearchController()

    def get_transcripciones(self, palabra: str):
        resultados = self.elastic_search.obtener_transcripciones(palabra)
        return resultados

    def obtener_transcripcion_por_intervalo(self, canal: str, timestamp: str, duracion_segundos: int = 90):
        """
        Devuelve un solo string concatenado con los textos de todas las transcripciones de ES cuyo '@timestamp' esté en el rango [timestamp, timestamp + duracion_segundos] y canal coincida.
        """
        transcripciones = self.elastic_search.obtener_transcripciones_por_clip(canal, timestamp, duracion_segundos)
        texto_concatenado = " ".join([t["texto"] for t in transcripciones if t.get("texto")])
        # Devuelve el formato esperado por el frontend
        return {
            "texto": texto_concatenado,
            "canal": canal,
            "timestamp": timestamp
        }

    def obtener_lista_videos_vecinos(self, carpeta_canal, timestamp, rango=3):
        print(f"Buscando en canal: {carpeta_canal}, timestamp: {timestamp}")
        tm_start = self.formatear_timestamp(timestamp)
        base_dir = "canales"
        archivos = sorted([f for f in os.listdir(f"{base_dir}/{carpeta_canal}") if f.endswith(".ts")])
        # Buscar el archivo que contiene tm_start en su nombre
        archivo_referencia = next((f for f in archivos if tm_start in f), None)
        if not archivo_referencia:
            print(f"No se encontró archivo con timestamp {tm_start} en la carpeta: {carpeta_canal}")
            return []
        idx = archivos.index(archivo_referencia)
        start_idx = max(0, idx - rango)
        end_idx = min(len(archivos), idx + rango + 1)
        return archivos[start_idx:end_idx]

    def formatear_timestamp(self, ts):
        """Convierte un timestamp ISO 8601 (con zona horaria) al formato usado en los nombres de archivo."""
        dt = _parse_timestamp(ts)
        return dt.strftime("%Y%m%d_%H%M%S")

    def imprimir_archivos(archivos):
        for archivo in archivos:
            print(archivo)

if __name__ == "__main__":
    handler = TranscripcionesHandler()
    resultados = handler.get_transcripciones("me")
    print(resultados)
