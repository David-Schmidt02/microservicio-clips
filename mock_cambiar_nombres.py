import os
import shutil
from datetime import datetime, timedelta

# Configuración
carpeta_origen = "videos"   # donde están video_1, video_2...
carpeta_destino = "ln+"       # donde vamos a guardar con nombres nuevos
canal = "ln+"               # nombre del canal mock
duracion_segundos = 90           # cada video dura 90 segundos
timestamp_inicial = datetime(2025, 9, 12, 12, 0, 0)  # mock inicio

# Crear carpeta de salida
os.makedirs(carpeta_destino, exist_ok=True)

# Obtener archivos ordenados (video_1, video_2, etc.)
archivos = sorted([f for f in os.listdir(carpeta_origen) if f.startswith("video_")])

# Iterar y renombrar
ts_inicio = timestamp_inicial
for archivo in archivos:
    ts_fin = ts_inicio + timedelta(seconds=duracion_segundos)

    nombre_nuevo = (
        f"{canal}_{ts_inicio.strftime('%Y%m%d_%H%M%S')}_{ts_fin.strftime('%Y%m%d_%H%M%S')}.ts"
    )

    ruta_origen = os.path.join(carpeta_origen, archivo)
    ruta_destino = os.path.join(carpeta_destino, nombre_nuevo)

    shutil.copy(ruta_origen, ruta_destino)  # o shutil.move si querés mover 

    print(f"{archivo} -> {nombre_nuevo}")

    # El próximo empieza justo donde terminó este
    ts_inicio = ts_fin
