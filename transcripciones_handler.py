from transcripciones_mock import objetos_transcripciones
import os
from datetime import datetime
from typing import Optional

class TranscripcionesHandler:
    def __init__(self):
        global transcripciones
        self.transcripciones = objetos_transcripciones

    def get_transcripciones(self, palabra: str):
        resultados = []
        for t in self.transcripciones:
            if t.tiene_palabra(palabra):
                resultados.append(t)
        return resultados
    
    # Ejemplo de nombre de clip: "a24_20250905_234106_20250905_234236.ts"
    # Timestamp inicial, timestamp final
    # Canal: a24

    def obtener_transcripcion_por_intervalo(self, canal: str, timestamp_start: str, timestamp_end: Optional[str] = None):
        for transcripcion in self.transcripciones:
            if transcripcion.canal != canal:
                continue
            if transcripcion.start_timestamp != timestamp_start:
                continue
            if timestamp_end and transcripcion.end_timestamp != timestamp_end:
                continue
            return {
                "canal": transcripcion.canal,
                "texto": transcripcion.texto,
                "start_timestamp": transcripcion.start_timestamp,
                "end_timestamp": transcripcion.end_timestamp,
            }
        return None

    def obtener_lista_videos_vecinos(self, carpeta_canal, timestamp_start_format, timestamp_end_format, rango=3):
        print(f"Buscando en canal: {carpeta_canal}, timestamp_start: {timestamp_start_format}, timestamp_end: {timestamp_end_format}")
        tm_start= self.formatear_timestamp(timestamp_start_format)
        tm_end= self.formatear_timestamp(timestamp_end_format)
        archivo_referencia = f"{carpeta_canal}_{tm_start}_{tm_end}.ts"
        base_dir = "canales"
        archivos = sorted([f for f in os.listdir(f"{base_dir}/{carpeta_canal}") if f.endswith(".ts")])
        if archivo_referencia not in archivos:
            print(f"El archivo de referencia no está en la carpeta: {carpeta_canal}")
            return []
        
        idx = archivos.index(archivo_referencia)
        start_idx = max(0, idx - rango)
        end_idx = min(len(archivos), idx + rango + 1)
        return archivos[start_idx:end_idx]

    def formatear_timestamp(self, ts):
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y%m%d_%H%M%S")

    def imprimir_archivos(archivos):
        for archivo in archivos:
            print(archivo)