from fastapi import FastAPI, Query, Body
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import uuid
import ffmpeg  # Biblioteca ffmpeg instalada con pip

from transcripciones_handler import TranscripcionesHandler

app = FastAPI()

transcripciones_handler = TranscripcionesHandler()

# === Configuración ===
VIDEO_DIR = "canales"
OUTPUT_DIR = "clips"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Datos simulados como si vinieran de Elasticsearch


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
    resultados = transcripciones_handler.get_transcripciones(palabra)
    return {"resultados": resultados}


@app.get("/videos")
def obtener_lista_videos(canal: str = Query(..., min_length=1), timestamp_start: str = Query(..., min_length=1), timestamp_end: str = Query(..., min_length=1)):
    # Debería probar si le puedo pegar una búsqueda múltiple al elastic search
    videos = transcripciones_handler.obtener_lista_videos_vecinos(canal, timestamp_start, timestamp_end)
    return {"videos": videos}


@app.get("/transcripcion")
def obtener_transcripcion(canal: str = Query(..., min_length=1), timestamp_start: str = Query(..., min_length=1), timestamp_end: Optional[str] = Query(None)):
    transcripcion = transcripciones_handler.obtener_transcripcion_por_intervalo(canal, timestamp_start, timestamp_end)
    if not transcripcion:
        return JSONResponse(content={"error": "Transcripcion no encontrada"}, status_code=404)
    return {"transcripcion": transcripcion}
@app.get("/descargar")
def descargar_clip(clip: str = Query(...)):
    output_path = os.path.join(OUTPUT_DIR, clip)
    if not os.path.exists(output_path):
        return JSONResponse(content={"error": "El archivo no existe"}, status_code=404)
    return FileResponse(
        output_path,
        filename=clip,
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={clip}"}
    )

@app.post("/concatenar")
def concatenar_videos(canal: str = Body(..., embed=True), videos: list[str] = Body(..., embed=True)):
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # ffmpeg necesita leer de una lista de archivos, por lo que guardamos los nombres en un archivo temporal
    list_file = os.path.join(OUTPUT_DIR, f"list_{uuid.uuid4().hex}.txt")
    
    # Verificar que los videos (su dir en memoria) existan
    for v in videos:
        video_path = os.path.join(VIDEO_DIR, canal, v)
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
            video_path = os.path.normpath(os.path.join(current_dir, VIDEO_DIR, canal, v))
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

        print(f"Archivo de lista: {list_path}")
        def leer_archivo(ruta):
            print(f"Leyendo archivo: {ruta}")
            with open(ruta, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
                print(f"Contenido del archivo {ruta}:\n{contenido}")

        leer_archivo(list_path)

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


    return {"archivo": os.path.basename(output_file)}
