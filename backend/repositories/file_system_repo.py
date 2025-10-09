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

        videos_seleccionados = archivos[start_idx:end_idx]

        # Validar si hay gaps (saltos temporales) en los videos seleccionados
        # self._validar_continuidad_temporal(videos_seleccionados)  # Comentado para producción

        return videos_seleccionados
    
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
            raise RuntimeError(f"Error en concatenación de videos: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Error en concatenación: {str(e)}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(list_file):
                os.remove(list_file)
    
    def _formatear_timestamp(self, timestamp: str) -> str:
        """Convierte un timestamp ISO 8601 al formato usado en nombres de archivo"""
        dt = parse_timestamp(timestamp)
        return dt.strftime("%Y%m%d_%H%M%S")
    
    async def obtener_rango_temporal_video(
        self,
        canal: str,
        timestamp: str
    ) -> tuple[str, str] | None:
        """
        Encuentra el video que contiene el timestamp y retorna su rango temporal real.

        Returns:
            Tupla (timestamp_inicio, timestamp_fin) en formato ISO 8601, o None si no se encuentra
        """
        canal_path = os.path.join(self.video_dir, canal)

        if not os.path.exists(canal_path):
            print(f"⚠️ Canal no encontrado: {canal_path}")
            return None

        archivos = sorted([
            f for f in os.listdir(canal_path)
            if f.endswith(".ts")
        ])

        timestamp_dt = parse_timestamp(timestamp)

        for archivo in archivos:
            rango = self._extraer_rango_temporal_archivo(archivo)
            if rango is None:
                continue

            inicio_dt, fin_dt = rango
            timestamp_naive = timestamp_dt.replace(tzinfo=None) if timestamp_dt.tzinfo else timestamp_dt

            # IMPORTANTE: El timestamp de fin es EXCLUSIVO (el siguiente video empieza ahí)
            # Por ejemplo: Video 09:59:14-10:00:44 NO incluye 10:00:44
            #              Video 10:00:44-10:02:14 SÍ incluye 10:00:44
            if inicio_dt <= timestamp_naive < fin_dt:
                # Convertir a ISO 8601 con timezone de Argentina
                from backend.config.settings import settings
                # IMPORTANTE: Usar localize() con pytz, NO replace()
                inicio_aware = settings.TIMEZONE.localize(inicio_dt)
                fin_aware = settings.TIMEZONE.localize(fin_dt)

                inicio_iso = inicio_aware.isoformat()
                fin_iso = fin_aware.isoformat()

                return (inicio_iso, fin_iso)

        return None

    def _extraer_rango_temporal_archivo(self, nombre_archivo: str) -> tuple[datetime, datetime] | None:
        """
        Extrae el rango temporal (inicio, fin) de un nombre de archivo.

        Formato esperado: canal_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.ts

        Returns:
            Tupla (inicio_dt, fin_dt) como datetime naive, o None si no se puede parsear
        """
        try:
            partes = nombre_archivo.replace('.ts', '').split('_')
            if len(partes) < 5:
                return None

            fecha_inicio = partes[1]  # YYYYMMDD
            hora_inicio = partes[2]   # HHMMSS
            fecha_fin = partes[3]     # YYYYMMDD
            hora_fin = partes[4]      # HHMMSS

            inicio_str = f"{fecha_inicio}_{hora_inicio}"
            fin_str = f"{fecha_fin}_{hora_fin}"

            inicio_dt = datetime.strptime(inicio_str, "%Y%m%d_%H%M%S")
            fin_dt = datetime.strptime(fin_str, "%Y%m%d_%H%M%S")

            return (inicio_dt, fin_dt)

        except Exception:
            return None

    def _timestamp_esta_en_archivo(self, nombre_archivo: str, timestamp_dt: datetime) -> bool:
        """
        Verifica si un timestamp está dentro del rango de tiempo de un archivo de video.

        Formato esperado: canal_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.ts

        IMPORTANTE: El timestamp de fin es EXCLUSIVO.
        """
        rango = self._extraer_rango_temporal_archivo(nombre_archivo)
        if rango is None:
            return False

        inicio_dt, fin_dt = rango

        # Convertir timestamp buscado a naive (sin timezone)
        timestamp_naive = timestamp_dt.replace(tzinfo=None) if timestamp_dt.tzinfo else timestamp_dt

        # Comparar directamente (todo en horario Argentina)
        # El fin es EXCLUSIVO: [inicio, fin)
        return inicio_dt <= timestamp_naive < fin_dt

    def _validar_continuidad_temporal(self, archivos: List[str]) -> None:
        """
        Valida que no haya gaps (saltos temporales) entre videos consecutivos.

        Imprime advertencias si detecta discontinuidades.

        Args:
            archivos: Lista de nombres de archivos a validar
        """
        if len(archivos) < 2:
            return

        print(f"\n🔍 Validando continuidad temporal de {len(archivos)} videos...")

        gaps_detectados = []

        for i in range(len(archivos) - 1):
            video_actual = archivos[i]
            video_siguiente = archivos[i + 1]

            rango_actual = self._extraer_rango_temporal_archivo(video_actual)
            rango_siguiente = self._extraer_rango_temporal_archivo(video_siguiente)

            if not rango_actual or not rango_siguiente:
                continue

            _, fin_actual = rango_actual
            inicio_siguiente, _ = rango_siguiente

            # Calcular diferencia en segundos
            diferencia = (inicio_siguiente - fin_actual).total_seconds()

            # Tolerancia: permitir gaps pequeños (configurables en settings)
            # Solo reportar gaps significativos
            from backend.config.settings import settings
            tolerancia = settings.GAP_TOLERANCE_SECONDS

            if diferencia > tolerancia:
                gap_info = {
                    'video_actual': video_actual,
                    'video_siguiente': video_siguiente,
                    'fin_actual': fin_actual,
                    'inicio_siguiente': inicio_siguiente,
                    'gap_segundos': diferencia
                }
                gaps_detectados.append(gap_info)

                print(f"⚠️ GAP DETECTADO entre videos {i+1} y {i+2}:")
                print(f"   📹 Video {i+1}: {video_actual}")
                print(f"      Termina: {fin_actual.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📹 Video {i+2}: {video_siguiente}")
                print(f"      Empieza: {inicio_siguiente.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   ⏱️  Salto temporal: {diferencia} segundos")

        from backend.config.settings import settings
        tolerancia = settings.GAP_TOLERANCE_SECONDS

        if not gaps_detectados:
            print(f"✅ Todos los videos son continuos (gaps ≤ {tolerancia}s son normales)")
        else:
            print(f"\n⚠️ RESUMEN: Se detectaron {len(gaps_detectados)} gap(s) significativo(s)")
            print(f"   Los clips concatenados tendrán saltos notables en el tiempo.")
            print(f"   Nota: Gaps menores o iguales a {tolerancia}s son considerados normales y no se reportan.")

        print("")  # Línea en blanco para separar