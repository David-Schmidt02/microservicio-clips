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

# Health check
curl "http://localhost:8001/health"

# Documentación interactiva
open http://localhost:8001/docs
```