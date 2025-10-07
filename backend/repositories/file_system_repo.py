"""
Repositorio para manejo del sistema de archivos y videos
"""
import os
import uuid
import subprocess
from typing import List

from backend.repositories.base import VideoRepositoryInterface
from backend.config.settings import settings
from backend.utils.time_utils import parse_timestamp


class FileSystemRepository(VideoRepositoryInterface):
    """Implementación concreta del repositorio de sistema de archivos"""
    
    def __init__(self):
        self.video_dir = settings.VIDEO_DIR
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def obtener_videos_vecinos(
        self, 
        canal: str, 
        timestamp: str, 
        rango: int = 3
    ) -> List[str]:
        """Obtiene videos vecinos a un timestamp"""
        
        tm_start = self._formatear_timestamp(timestamp)
        canal_path = os.path.join(self.video_dir, canal)
        
        if not os.path.exists(canal_path):
            return []
            
        archivos = sorted([
            f for f in os.listdir(canal_path) 
            if f.endswith(".ts")
        ])
        
        # Buscar el archivo que contiene tm_start en su nombre
        archivo_referencia = next(
            (f for f in archivos if tm_start in f), 
            None
        )
        
        if not archivo_referencia:
            return []
            
        idx = archivos.index(archivo_referencia)
        start_idx = max(0, idx - rango)
        end_idx = min(len(archivos), idx + rango + 1)
        
        return archivos[start_idx:end_idx]
    
    async def concatenar_videos(self, canal: str, videos: List[str]) -> str:
        """Concatena una lista de videos y retorna la ruta del resultado"""
        
        if not videos:
            raise ValueError("La lista de videos está vacía")
            
        # Generar nombre único para el clip
        clip_id = str(uuid.uuid4())
        clip_filename = f"clip_{clip_id}.mp4"
        output_path = os.path.join(self.output_dir, clip_filename)
        
        # Construir rutas completas de los videos de entrada
        input_paths = []
        for video in videos:
            video_path = os.path.join(self.video_dir, canal, video)
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video no encontrado: {video_path}")
            input_paths.append(video_path)
        
        # Crear archivo de lista temporal para ffmpeg
        list_file = os.path.join(self.output_dir, f"list_{clip_id}.txt")
        try:
            with open(list_file, 'w') as f:
                for path in input_paths:
                    f.write(f"file '{path}'\\n")
            
            # Ejecutar ffmpeg para concatenar
            cmd = [
                settings.FFMPEG_BIN,
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return clip_filename
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error en concatenación: {e.stderr}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(list_file):
                os.remove(list_file)
    
    def _formatear_timestamp(self, timestamp: str) -> str:
        """Convierte un timestamp ISO 8601 al formato usado en nombres de archivo"""
        dt = parse_timestamp(timestamp)
        return dt.strftime("%Y%m%d_%H%M%S")