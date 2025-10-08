# Setup del Entorno - Microservicio de Clips

## 🚀 Instalación Rápida

### 1. Instalar dependencias de Python

```bash
# Producción
pip install -r requirements.txt

# Desarrollo (incluye dependencias de testing y linting)
pip install -r requirements-dev.txt
```

### 2. Configurar variables de entorno

Crear `backend/config/.env` con:

```bash
# Elasticsearch
ELASTIC_URL=https://172.20.100.40:9200
ELASTIC_USER=elastic
ELASTIC_PASSWORD=tu_password
ELASTICSEARCH_INDEX=streaming_tv

# Timezone
TIMEZONE=America/Argentina/Buenos_Aires

# Paths (opcionales)
VIDEOS_PATH=./videos
CLIPS_PATH=./clips
```

### 3. Levantar Elasticsearch

```bash
docker-compose up -d
```

### 4. Levantar el backend

```bash
# Backend con arquitectura en capas
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# O usando el script directo
python -m backend.main
```

### 5. Levantar el frontend

```bash
cd frontend
python -m http.server 8080
```

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8001
- **Documentación API**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Elasticsearch**: http://localhost:9200

## 🏗️ Arquitectura del Backend

### Arquitectura en Capas
- **Puerto**: 8001
- **Archivo**: `backend/main.py`
- **Estructura**: API/Services/Repositories/Models
- **Endpoints**: `/api/v1/search/`, `/api/v1/clips/`
- **Compatibilidad**: Mantiene endpoints legacy para transición

## 📦 Dependencias Principales

- **FastAPI**: Framework web moderno para APIs
- **Elasticsearch**: Motor de búsqueda para transcripciones  
- **Pydantic**: Validación de datos y configuración
- **pytz**: Manejo de zonas horarias cross-platform
- **ffmpeg-python**: Procesamiento de video
- **uvicorn**: Servidor ASGI de alto rendimiento

## 🔧 Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo

# Levantar servicios
uvicorn backend.main:app --reload --port 8001  # Backend
python -m http.server 8080                     # Frontend
docker-compose up -d                           # Elasticsearch

# Testing y calidad de código
pytest                                         # Ejecutar tests
black .                                        # Formatear código
flake8 .                                       # Linting

# Health checks
curl http://localhost:8001/health              # Backend
curl http://localhost:9200/_cluster/health     # Elasticsearch
```

## 🔍 Testing de APIs

```bash
# Buscar transcripciones
curl "http://localhost:8001/api/v1/search/buscar?palabra=test"

# Obtener videos vecinos
curl "http://localhost:8001/api/v1/clips/videos?canal=luzutv&timestamp=2025-10-08T10:00:01-03:00&rango=3"

# Obtener transcripción de clip
curl "http://localhost:8001/api/v1/search/transcripcionClip?canal=luzutv&timestamp=2025-10-08T10:00:01-03:00&duracion_segundos=30"

# Servir video individual
curl -I "http://localhost:8001/api/v1/clips/video/luzutv/luzutv_20251008_100000_20251008_100130.ts"

# Concatenar videos
curl -X POST "http://localhost:8001/api/v1/clips/concatenar" \
     -H "Content-Type: application/json" \
     -d '{"canal":"luzutv","videos":["video1.ts","video2.ts"]}'

# Health check
curl "http://localhost:8001/health"

# Documentación interactiva
open http://localhost:8001/docs
```

## 📹 Nuevos Endpoints de Video

### Servir Videos Individuales
- **Endpoint**: `GET /api/v1/clips/video/{canal}/{archivo}`
- **Descripción**: Sirve archivos de video individuales para reproducción
- **Características**:
  - ✅ Conversión automática .ts → .mp4 para mejor compatibilidad
  - ✅ Cache inteligente (no re-convierte si ya existe)
  - ✅ Headers optimizados para streaming (Accept-Ranges, Cache-Control)
  - ✅ Fallback a archivo original si falla conversión

### Obtener Videos Vecinos
- **Endpoint**: `GET /api/v1/clips/videos`
- **Parámetros**: `canal`, `timestamp`, `rango`
- **Descripción**: Encuentra videos en un rango temporal alrededor de un timestamp

### Concatenación con Nombres Descriptivos
- **Formato anterior**: `clip_uuid.mp4`
- **Formato nuevo**: `{canal}-{fecha}_{hora_inicio}_{hora_fin}.mp4`
- **Ejemplo**: `todonoticias-20251008_100000_100430.mp4`