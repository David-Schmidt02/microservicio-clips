"""
Servicio para limpieza de archivos temporales
"""
import os
import time
from pathlib import Path
from typing import List, Tuple

from backend.config.settings import settings


class CleanupService:
    """Servicio para limpiar clips temporales antiguos"""

    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR

    def limpiar_clips_antiguos(self, max_age_hours: int = 1) -> Tuple[int, List[str]]:
        """
        Elimina clips generados hace más de max_age_hours.

        Args:
            max_age_hours: Edad máxima en horas (por defecto 1 hora)

        Returns:
            Tupla (cantidad_eliminados, lista_archivos_eliminados)
        """
        if not os.path.exists(self.output_dir):
            return (0, [])

        now = time.time()
        max_age_seconds = max_age_hours * 3600

        archivos_eliminados = []

        for archivo in os.listdir(self.output_dir):
            # Solo procesar archivos .mp4 (clips generados)
            # Ignorar archivos .txt (listas temporales de ffmpeg)
            if not archivo.endswith('.mp4'):
                continue

            filepath = os.path.join(self.output_dir, archivo)

            # Verificar que sea un archivo (no directorio)
            if not os.path.isfile(filepath):
                continue

            # Obtener edad del archivo
            file_age = now - os.path.getmtime(filepath)

            # Eliminar si es más antiguo que max_age
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    archivos_eliminados.append(archivo)
                except Exception as e:
                    print(f"⚠️ Error eliminando {archivo}: {e}")

        return (len(archivos_eliminados), archivos_eliminados)

    def obtener_estadisticas_clips(self) -> dict:
        """
        Obtiene estadísticas sobre clips almacenados.

        Returns:
            Dict con estadísticas (cantidad, tamaño total, etc)
        """
        if not os.path.exists(self.output_dir):
            return {
                "cantidad_clips": 0,
                "tamano_total_mb": 0,
                "clip_mas_antiguo": None,
                "clip_mas_reciente": None
            }

        clips = [f for f in os.listdir(self.output_dir) if f.endswith('.mp4')]

        if not clips:
            return {
                "cantidad_clips": 0,
                "tamano_total_mb": 0,
                "clip_mas_antiguo": None,
                "clip_mas_reciente": None
            }

        tamano_total = 0
        tiempos = []

        for clip in clips:
            filepath = os.path.join(self.output_dir, clip)
            if os.path.isfile(filepath):
                tamano_total += os.path.getsize(filepath)
                tiempos.append(os.path.getmtime(filepath))

        return {
            "cantidad_clips": len(clips),
            "tamano_total_mb": round(tamano_total / (1024 * 1024), 2),
            "clip_mas_antiguo": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(min(tiempos))) if tiempos else None,
            "clip_mas_reciente": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(max(tiempos))) if tiempos else None
        }
