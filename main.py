from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import uuid
import ffmpeg  # Biblioteca ffmpeg instalada con pip

app = FastAPI()

# === Configuración ===
VIDEO_DIR = "videos"
OUTPUT_DIR = "clips"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Datos simulados como si vinieran de Elasticsearch
transcripciones = [
    {
        "texto": "En este fragmento hablamos de microservicios y elasticsearch",
        "timestamp": "2025-09-13T10:00:00",
        "video": "video_1.mp4",
        "segundo_inicio": 75
    },
    {
        "texto": "Aquí aparece la palabra python en una transcripción de prueba",
        "timestamp": "2025-09-13T10:01:30",
        "video": "video_2.mp4",
        "segundo_inicio": 120
    },
    {
        "texto": "Este es otro ejemplo donde mencionamos microservicios y bases de datos",
        "timestamp": "2025-09-13T10:03:00",
        "video": "video_3.mp4",
        "segundo_inicio": 200
    }
]

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir ruta del ejecutable FFmpeg
# Usamos directamente 'ffmpeg' ya que está en el PATH del sistema
FFMPEG_BIN = "ffmpeg"

# === Endpoints ===
@app.get("/buscar")
def buscar_palabra(palabra: str = Query(..., min_length=1)):
    """
    Busca transcripciones que contengan la palabra. -> Tengo que ver cómo se hace en Elasticsearch
    """
    # Acá iria una lógica para pegarle al Elasticsearch
    
    resultados = [
        t for t in transcripciones if palabra.lower() in t["texto"].lower()
    ]
    return {"resultados": resultados}


@app.get("/videos")
def listar_videos():
    """
    Lista todos los videos disponibles en la carpeta.
    """
    if not os.path.exists(VIDEO_DIR):
        return {"videos": []}
    
    # Versión simplificada que solo lista archivos en el directorio principal
    # sin tener en cuenta la estructura de carpetas
    archivos = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".ts"))]
    
    # Ordenar videos numéricamente por número en lugar de alfabéticamente
    import re
    def extraer_numero(nombre_archivo):
        match = re.search(r'(\d+)', nombre_archivo)
        if match:
            return int(match.group(1))
        return float('inf')  # Si no hay número, lo ponemos al final
    
    archivos = sorted(archivos, key=extraer_numero)
    
    # Código comentado para la versión que maneja subcarpetas (para uso futuro)
    """
    videos = []
    # Recorrer el directorio de videos y sus subcarpetas
    for root, dirs, files in os.walk(VIDEO_DIR):
        for file in files:
            # Incluir archivos .mp4 y .ts
            if file.lower().endswith((".mp4", ".ts")):
                # Obtener la ruta relativa desde VIDEO_DIR
                ruta_relativa = os.path.relpath(os.path.join(root, file), VIDEO_DIR)
                # Convertir backslashes a forward slashes si estamos en Windows 
                ruta_relativa = ruta_relativa.replace("\\", "/")
                videos.append(ruta_relativa)
    
    return {"videos": sorted(videos)}
    """
    
    return {"videos": archivos}


@app.post("/concatenar")
def concatenar_videos(videos: list[str] = Body(..., embed=True)):
    """
    Concatena una lista de videos usando FFmpeg y devuelve el archivo resultante.
    
    Args:
        videos (list): Lista de rutas de videos a concatenar
        
    Returns:
        FileResponse: Archivo de video concatenado para descarga
        o
        JSONResponse: Error en caso de problemas
    """
    if not videos:
        return JSONResponse(content={"error": "No se enviaron videos"}, status_code=400)

    # Crear archivo temporal con lista de inputs
    # Primero, asegurarnos de que estamos en el directorio correcto
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # ffmpeg necesita leer de una lista de archivos, por lo que guardamos los nombres en un archivo temporal
    list_file = os.path.join(OUTPUT_DIR, f"list_{uuid.uuid4().hex}.txt")
    
    # Verificar que los videos (su dirección en memoria) existan antes de crear el archivo
    for v in videos:
        video_path = os.path.join(VIDEO_DIR, v)
        if not os.path.exists(video_path):
            return JSONResponse(
                content={"error": f"El archivo {v} no existe. Ruta buscada: {os.path.abspath(video_path)}"}, 
                status_code=400
            )
    
    # Obtener paths absolutos para evitar problemas de rutas relativas
    current_dir = os.path.abspath(os.getcwd())
    
    # Crear el archivo con las rutas absolutas
    with open(list_file, "w", encoding="utf-8") as f:
        for v in videos:
            # Usamos normpath para manejar correctamente las barras según el sistema operativo
            video_path = os.path.normpath(os.path.join(current_dir, VIDEO_DIR, v))
            f.write(f"file '{video_path}'\n")
            print(f"Añadiendo video: {video_path}")

    # Nombre de salida
    output_file = os.path.join(OUTPUT_DIR, f"clip_{uuid.uuid4().hex}.mp4")

    # Ejecutar FFmpeg usando la biblioteca ffmpeg de Python
    try:
        print("Concatenando videos con ffmpeg...")
        
        # Usamos el comando ffmpeg directamente desde el PATH con rutas absolutas
        output_path = os.path.abspath(output_file)

        list_path = os.path.abspath(list_file)
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_path,
            "-c", "copy", output_path
        ]
        print(f"Ejecutando comando: {' '.join(cmd)}")
        
        # Ejecutar el comando desde el directorio raíz para evitar problemas con rutas
        proceso = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        print("FFmpeg ejecutado correctamente")
        
        # Verificar que el archivo de salida realmente se haya creado
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            print(f"Error: El archivo de salida no se creó correctamente: {output_file}")
            return JSONResponse(
                content={"error": "El archivo de salida no se generó correctamente"}, 
                status_code=500
            )
            
        print(f"Archivo generado exitosamente: {output_file}, tamaño: {os.path.getsize(output_file)} bytes")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar FFmpeg: {e}")
        print(f"Salida de error: {e.stderr}")
        return JSONResponse(content={"error": f"FFmpeg falló: {e.stderr}"}, status_code=500)
    except Exception as e:
        print(f"Error inesperado: {e}")
        return JSONResponse(content={"error": f"Error inesperado: {str(e)}"}, status_code=500)
    finally:
        # Limpiar archivos temporales
        if os.path.exists(list_file):
            print(f"Eliminando archivo temporal: {list_file}")
            os.remove(list_file)

    # Devolver archivo final
    return FileResponse(
        output_file,
        filename="clip_concatenado.mp4",
        media_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=clip_concatenado.mp4"}
    )
