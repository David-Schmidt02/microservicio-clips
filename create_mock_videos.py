#!/usr/bin/env python3
"""
Script para crear videos mock para testing del microservicio de clips.
Genera videos de prueba con nombres que coinciden con el formato esperado.
"""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def create_test_video(output_path: str, duration_seconds: int = 10, text: str = "Test Video"):
    """
    Crear un video de prueba usando FFmpeg.
    
    Args:
        output_path: Ruta donde guardar el video
        duration_seconds: Duración en segundos
        text: Texto a mostrar en el video
    """
    try:
        cmd = [
            'ffmpeg', '-y',  # -y para sobrescribir archivos existentes
            '-f', 'lavfi',
            '-i', f'testsrc2=size=640x480:duration={duration_seconds}:rate=30',
            '-f', 'lavfi', 
            '-i', f'sine=frequency=1000:duration={duration_seconds}',
            '-vf', f'drawtext=fontfile=arial.ttf:text="{text}":fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-t', str(duration_seconds),
            output_path
        ]
        
        # En Windows, usar comando simplificado si hay problemas con fuentes
        cmd_simple = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'testsrc2=size=640x480:duration={duration_seconds}:rate=30',
            '-f', 'lavfi',
            '-i', f'sine=frequency=1000:duration={duration_seconds}',
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-t', str(duration_seconds),
            output_path
        ]
        
        print(f"Creando video: {output_path}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            print("  Intentando con comando simplificado (sin texto)...")
            result = subprocess.run(cmd_simple, capture_output=True, text=True, check=True)
        
        print(f"  ✅ Video creado exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error creando video: {e.stderr}")
        return False
    except FileNotFoundError:
        print("  ❌ FFmpeg no encontrado. Por favor instala FFmpeg primero.")
        print("     Descarga desde: https://ffmpeg.org/download.html")
        return False

def generate_timestamp_filename(canal: str, base_time: datetime) -> str:
    """
    Generar nombre de archivo con formato timestamp.
    Formato: canal_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.ts
    """
    start_time = base_time
    end_time = base_time + timedelta(seconds=90)  # Videos de 90 segundos
    
    start_str = start_time.strftime("%Y%m%d_%H%M%S")
    end_str = end_time.strftime("%Y%m%d_%H%M%S")
    
    return f"{canal}_{start_str}_{end_str}.ts"

def create_mock_videos():
    """Crear videos mock para testing"""
    
    # Configuración
    canales = ['a24', 'tn', 'c5n']
    base_time = datetime(2025, 10, 7, 12, 0, 0)  # Fecha actual
    videos_per_channel = 10
    
    print("🎬 Creando videos mock para testing...")
    print("=" * 50)
    
    total_created = 0
    total_failed = 0
    
    for canal in canales:
        print(f"\n📺 Canal: {canal.upper()}")
        canal_dir = Path(f"canales/{canal}")
        canal_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(videos_per_channel):
            # Calcular tiempo para este video (intervalos de 90 segundos)
            video_time = base_time + timedelta(seconds=90 * i)
            filename = generate_timestamp_filename(canal, video_time)
            filepath = canal_dir / filename
            
            # Texto descriptivo para el video
            video_text = f"{canal.upper()} {video_time.strftime('%H:%M:%S')}"
            
            if create_test_video(str(filepath), duration_seconds=10, text=video_text):
                total_created += 1
            else:
                total_failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Videos creados exitosamente: {total_created}")
    if total_failed > 0:
        print(f"❌ Videos fallidos: {total_failed}")
    
    print(f"\n📁 Estructura creada:")
    for canal in canales:
        canal_dir = Path(f"canales/{canal}")
        if canal_dir.exists():
            video_count = len(list(canal_dir.glob("*.ts")))
            print(f"   📺 {canal}/ -> {video_count} videos")

def create_sample_elasticsearch_data():
    """Crear datos de ejemplo para Elasticsearch"""
    
    print("\n🔍 Datos de ejemplo para Elasticsearch:")
    print("-" * 40)
    
    # Ejemplos de documentos que deberían estar en Elasticsearch
    sample_docs = [
        {
            "text": "El presidente anunció nuevas medidas económicas para combatir la inflación",
            "slug": "a24", 
            "name": "A24 Noticias",
            "@timestamp": "2025-10-07T12:00:30Z",
            "service": "streaming_tv",
            "channel_id": "a24_main"
        },
        {
            "text": "La selección argentina se prepara para el próximo mundial de fútbol",
            "slug": "tn",
            "name": "Todo Noticias", 
            "@timestamp": "2025-10-07T12:05:15Z",
            "service": "streaming_tv",
            "channel_id": "tn_main"
        },
        {
            "text": "Nuevas protestas en la capital por el aumento de precios",
            "slug": "c5n",
            "name": "C5N Noticias",
            "@timestamp": "2025-10-07T12:10:00Z", 
            "service": "streaming_tv",
            "channel_id": "c5n_main"
        }
    ]
    
    print("📄 Ejemplos de documentos para indexar en 'streaming_tv':")
    for i, doc in enumerate(sample_docs, 1):
        print(f"\n{i}. Canal: {doc['slug']}")
        print(f"   Texto: {doc['text'][:50]}...")
        print(f"   Timestamp: {doc['@timestamp']}")

if __name__ == "__main__":
    print("🚀 Configurando entorno mock para microservicio de clips")
    print("=" * 60)
    
    # Verificar que estemos en el directorio correcto
    if not os.path.exists("backend"):
        print("❌ Error: Ejecuta este script desde la raíz del proyecto")
        exit(1)
    
    create_mock_videos()
    create_sample_elasticsearch_data()
    
    print(f"\n🎉 ¡Configuración mock completada!")
    print(f"\n📋 Próximos pasos:")
    print(f"   1. Indexar datos de ejemplo en Elasticsearch")
    print(f"   2. Levantar el backend: uvicorn backend.main:app --port 8001 --reload")
    print(f"   3. Levantar el frontend: python -m http.server 8080 (en carpeta frontend/)")
    print(f"   4. Probar búsquedas con: 'presidente', 'selección', 'protestas'")