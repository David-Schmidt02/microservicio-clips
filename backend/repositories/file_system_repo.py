"""
Repositorio para manejo del sistema de archivos y videos
"""
import os
import uuid
import subprocess
from typing import List
from datetime import datetime

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
        
        # Buscar el archivo cuyo rango de tiempo contenga el timestamp buscado
        timestamp_dt = parse_timestamp(timestamp)
        archivo_referencia = None
        for archivo in archivos:
            if self._timestamp_esta_en_archivo(archivo, timestamp_dt):
                archivo_referencia = archivo
                break
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
            
        # Generar nombre descriptivo para el clip basado en el primer y último video
        primer_video = videos[0]
        ultimo_video = videos[-1]
        
        # Extraer información temporal del primer y último archivo
        # Formato: canal_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.ts
        def extraer_info_temporal(nombre_archivo):
            partes = nombre_archivo.replace('.ts', '').split('_')
            if len(partes) >= 3:
                return partes[1], partes[2]  # fecha_inicio, hora_inicio
            return None, None
        
        fecha_inicio, hora_inicio = extraer_info_temporal(primer_video)
        _, hora_fin = extraer_info_temporal(ultimo_video)
        
        # Generar un ID único para los archivos temporales
        temp_id = str(uuid.uuid4())[:8]  # Solo los primeros 8 caracteres
        
        if fecha_inicio and hora_inicio and hora_fin:
            # Formato: canal-YYYYMMDD_HHMMSS_HHMMSS.mp4
            clip_filename = f"{canal}-{fecha_inicio}_{hora_inicio}_{hora_fin}.mp4"
        else:
            # Fallback al método anterior si no se puede parsear
            clip_filename = f"clip_{temp_id}.mp4"
        
        output_path = os.path.join(self.output_dir, clip_filename)
        
        # Construir rutas completas de los videos de entrada
        input_paths = []
        for video in videos:
            video_path = os.path.join(self.video_dir, canal, video)
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video no encontrado: {video_path}")
            input_paths.append(video_path)
        
        # Crear archivo de lista temporal para ffmpeg
        list_file = os.path.join(self.output_dir, f"list_{temp_id}.txt")
        try:
            with open(list_file, 'w') as f:
                for path in input_paths:
                    f.write(f"file '{path}'\n")
            
            print(f"📝 Archivo de lista creado: {list_file}")
            # Verificar contenido del archivo para debugging
            with open(list_file, 'r') as f:
                content = f.read()
                print(f"📝 Contenido del archivo de lista:\n{content}")
            
            # Ejecutar ffmpeg para concatenar
            cmd = [
                settings.FFMPEG_BIN,
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path
            ]
            
            print(f"Ejecutando FFmpeg: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"Concatenación exitosa: {clip_filename}")
            return clip_filename
            
        except subprocess.CalledProcessError as e:
            print(f"Error de FFmpeg: {e.stderr}")
            print(f"Comando ejecutado: {' '.join(cmd)}")
            print(f"Return code: {e.returncode}")
            raise RuntimeError(f"Error en concatenación: {e.stderr}")
        except Exception as e:
            print(f"Error general en concatenación: {str(e)}")
            raise RuntimeError(f"Error en concatenación: {str(e)}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(list_file):
                os.remove(list_file)
    
    def _formatear_timestamp(self, timestamp: str) -> str:
        """Convierte un timestamp ISO 8601 al formato usado en nombres de archivo"""
        dt = parse_timestamp(timestamp)
        return dt.strftime("%Y%m%d_%H%M%S")
    
    def _timestamp_esta_en_archivo(self, nombre_archivo: str, timestamp_dt: datetime) -> bool:
        """
        Verifica si un timestamp está dentro del rango de tiempo de un archivo de video.
        
        Formato esperado: canal_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.ts
        """
        try:
            # Extraer las partes del nombre: canal_inicio_fin.ts
            partes = nombre_archivo.replace('.ts', '').split('_')
            if len(partes) < 5:
                return False
                
            # Las partes son: [canal, fecha_inicio, hora_inicio, fecha_fin, hora_fin]
            fecha_inicio = partes[1]  # YYYYMMDD
            hora_inicio = partes[2]   # HHMMSS
            fecha_fin = partes[3]     # YYYYMMDD  
            hora_fin = partes[4]      # HHMMSS
            
            # Construir datetimes de inicio y fin EN ZONA HORARIA ARGENTINA
            from zoneinfo import ZoneInfo
            argentina_tz = ZoneInfo("America/Argentina/Buenos_Aires")
            
            inicio_str = f"{fecha_inicio}_{hora_inicio}"
            fin_str = f"{fecha_fin}_{hora_fin}"
            
            # Los timestamps en los archivos están en hora Argentina
            inicio_dt = datetime.strptime(inicio_str, "%Y%m%d_%H%M%S")
            inicio_dt = inicio_dt.replace(tzinfo=argentina_tz)
            
            fin_dt = datetime.strptime(fin_str, "%Y%m%d_%H%M%S")
            fin_dt = fin_dt.replace(tzinfo=argentina_tz)
            
            # Convertir timestamp buscado a Argentina si tiene timezone
            if timestamp_dt.tzinfo is not None:
                timestamp_argentina = timestamp_dt.astimezone(argentina_tz)
            else:
                # Si no tiene timezone, asumir que ya está en Argentina
                timestamp_argentina = timestamp_dt.replace(tzinfo=argentina_tz)
                
            # Verificar si está dentro del rango (comparar con timezone)
            esta_en_rango = inicio_dt <= timestamp_argentina <= fin_dt
            
            return esta_en_rango
            
        except Exception as e:
            print(f"Error parseando archivo {nombre_archivo}: {e}")
            return False