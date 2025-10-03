from transcripciones_mock import objetos_transcripciones
import os
from datetime import datetime
from typing import Optional
from elasticsearch import Elasticsearch

from config import ELASTIC_PASSWORD, ELASTIC_URL, ELASTIC_USER

class ElasticSearchController:
    def obtener_transcripciones_por_canal_intervalo(self, canal, timestamp, duracion_segundos=90):
        """
        Consulta ES filtrando por canal y por rango de timestamp.
        """
        from datetime import datetime, timedelta
        try:
            t0 = datetime.fromisoformat(timestamp.replace('Z', '').replace('+00:00', ''))
        except Exception:
            return []
        t1 = t0 + timedelta(seconds=duracion_segundos)
        # Formato ISO para ES
        ts_inicio = t0.isoformat()
        ts_fin = t1.isoformat()
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"slug": canal}},
                        {"range": {"@timestamp": {"gte": ts_inicio, "lt": ts_fin}}}
                    ]
                }
            }
        }
        resultados = self.es.search(index="streaming_tv", body=body)
        return self.mapear_resultados(resultados)
    def __init__(self):
        self.es = Elasticsearch(
            ELASTIC_URL,
            basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
            verify_certs=False
        )
    def obtener_transcripciones(self, palabra: str):
        resultados = self.es.search(index="streaming_tv", body={
            "query": {
                "match": {
                    "text": palabra
                }
            }
        })
        hits = resultados.get("hits", {}).get("hits", [])
        # Mapeo para frontend: solo campos relevantes
        mapeados = self.mapear_resultados(resultados)
        return mapeados
    
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
        from datetime import datetime, timedelta
        t0 = datetime.fromisoformat(timestamp.replace('Z', '').replace('+00:00', ''))
        t1 = t0 + timedelta(seconds=duracion_segundos)
        ts_inicio = t0.isoformat()
        ts_fin = t1.isoformat()
        query = {
            "bool": {
                "must": [
                    {"match": {"slug": canal}},
                    {"range": {"@timestamp": {"gte": ts_inicio, "lt": ts_fin}}}
                ]
            }
        }
        resultados = self.es.search(index="streaming_tv", body={"query": query})
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
        transcripciones = self.elastic_search.obtener_transcripciones_por_canal_intervalo(canal, timestamp, duracion_segundos)
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
        # Si termina con Z, usa el formato original
        if ts.endswith('Z'):
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        else:
            # Elimina microsegundos y zona horaria si existen
            dt = datetime.fromisoformat(ts.replace('Z', '').replace('+00:00', ''))
        return dt.strftime("%Y%m%d_%H%M%S")

    def imprimir_archivos(archivos):
        for archivo in archivos:
            print(archivo)

if __name__ == "__main__":
    handler = TranscripcionesHandler()
    resultados = handler.get_transcripciones("me")
    print(resultados)