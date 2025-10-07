# Backend - Microservicio de Clips de Video

## 📋 Descripción

API REST construida con FastAPI para la búsqueda, reproducción y concatenación de clips de video basados en transcripciones almacenadas en Elasticsearch.

## 🏗️ Arquitectura en Capas

La aplicación está diseñada siguiendo los principios de **Clean Architecture** y **Separación de Responsabilidades**:

```
backend/
├── main_new.py                 # 🚀 Punto de entrada principal
├── config/                     # ⚙️  Configuración
│   ├── settings.py             # Configuración centralizada con Pydantic
│   └── .env                    # Variables de entorno
├── api/                        # 🌐 Capa de Presentación
│   ├── dependencies.py         # Inyección de dependencias
│   └── v1/
│       ├── main.py             # Router principal de API v1
│       └── routes/  
│           ├── search.py       # Endpoints de búsqueda
│           └── clips.py        # Endpoints de clips/videos
├── models/                     # 📊 Capa de Modelos
│   ├── domain.py               # Entidades de dominio (Transcripcion, Video)
│   └── schemas.py              # Esquemas Pydantic (requests/responses)
├── services/                   # 🧠 Capa de Lógica de Negocio
│   ├── search_service.py       # Lógica de búsquedas de transcripciones
│   └── video_service.py        # Lógica de manejo de videos
├── repositories/               # 🗄️  Capa de Acceso a Datos
│   ├── base.py                 # Interfaces/contratos abstractos
│   ├── elasticsearch_repo.py   # Implementación de acceso a Elasticsearch
│   └── file_system_repo.py     # Implementación de acceso al sistema de archivos
└── utils/                      # 🔧 Utilidades
    └── time_utils.py           # Utilidades para manejo de timestamps
```

### 🎯 Responsabilidades por Capa

#### **🌐 API (Capa de Presentación)**
- **Responsabilidad**: Manejar requests HTTP y responses
- **Contiene**: Validación de entrada, serialización de respuestas, manejo de errores HTTP
- **NO debe**: Contener lógica de negocio o acceso directo a base de datos

#### **🧠 Services (Capa de Lógica de Negocio)**
- **Responsabilidad**: Implementar reglas de negocio y casos de uso
- **Contiene**: Validaciones de dominio, orquestación de repositorios, transformaciones de datos
- **NO debe**: Conocer detalles de HTTP o bases de datos específicas

#### **🗄️ Repositories (Capa de Acceso a Datos)**
- **Responsabilidad**: Acceder y manipular datos de diferentes fuentes
- **Contiene**: Queries de Elasticsearch, operaciones de sistema de archivos, mapeo de datos
- **NO debe**: Contener lógica de negocio

#### **📊 Models (Capa de Modelos)**
- **Responsabilidad**: Definir estructura de datos y contratos
- **Contiene**: Entidades de dominio, esquemas de validación, tipos de datos
- **NO debe**: Contener lógica de procesamiento

## 🚀 Instalación y Configuración

### Prerequisitos

- Python 3.8+
- Docker & Docker Compose (para Elasticsearch)
- FFmpeg instalado en el sistema

### 1. Instalar Dependencias

```bash
# Navegar al directorio del proyecto
cd microservicio-clips

# Instalar dependencias de Python
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crear/editar el archivo `backend/config/.env`:

```bash
# Elasticsearch
ELASTIC_URL=https://172.20.100.40:9200
ELASTIC_USER=elastic
ELASTIC_PASSWORD=tu_password_aqui

# Directorios
VIDEO_DIR=canales
OUTPUT_DIR=clips

# FFmpeg
FFMPEG_BIN=ffmpeg

# Zona horaria
TIMEZONE_NAME=America/Argentina/Buenos_Aires
```

### 3. Levantar Elasticsearch

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que esté funcionando
curl http://localhost:9200
```

### 4. Ejecutar la Aplicación

```bash
# Levantar el servidor con la nueva arquitectura
uvicorn backend.main_new:app --host 0.0.0.0 --port 8000 --reload

# O usar el main original para compatibilidad
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### 🔍 Búsqueda de Transcripciones

#### **Nueva API (v1)**

- `GET /api/v1/search/buscar?palabra={palabra}` - Buscar transcripciones
- `GET /api/v1/search/transcripcionClip?canal={canal}&timestamp={timestamp}&duracion_segundos={duracion}` - Obtener transcripción de un clip

#### **API Legacy (compatibilidad)**

- `GET /buscar?palabra={palabra}` - Buscar transcripciones
- `GET /transcripcionClip?canal={canal}&timestamp={timestamp}` - Obtener transcripción de un clip

### 🎥 Manejo de Videos y Clips

#### **Nueva API (v1)**

- `GET /api/v1/clips/videos?canal={canal}&timestamp={timestamp}&rango={rango}` - Obtener videos vecinos
- `POST /api/v1/clips/concatenar` - Concatenar videos (body: `{canal, videos[]}`)
- `GET /api/v1/clips/descargar?clip={clip}` - Descargar clip generado

#### **API Legacy (compatibilidad)**

- `GET /videos?canal={canal}&timestamp={timestamp}` - Obtener videos vecinos
- `POST /concatenar` - Concatenar videos (body: `{canal, videos[]}`)
- `GET /descargar?clip={clip}` - Descargar clip generado

### 📚 Documentación Automática

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Configuración Avanzada

### Configuración de Elasticsearch

La configuración de Elasticsearch se maneja a través de la clase `Settings` en `backend/config/settings.py`:

```python
# Configuración personalizada
ELASTIC_URL = "https://tu-elasticsearch-url:9200"
ELASTICSEARCH_INDEX = "tu_indice_personalizado"
MAX_RESULTS_PER_CHANNEL = 15  # Máximo resultados por canal
```

### Configuración de Videos

```python
# Directorios personalizados
VIDEO_DIR = "ruta/a/tus/videos"
OUTPUT_DIR = "ruta/a/clips/generados"

# Configuración de clips
DEFAULT_CLIP_DURATION = 120    # Duración por defecto en segundos
MAX_CLIP_DURATION = 600        # Duración máxima permitida
DEFAULT_VIDEO_RANGE = 5        # Videos vecinos por defecto
```

## 🧪 Testing

### Estructura de Tests (Recomendada)

```
tests/
├── unit/
│   ├── test_services/
│   ├── test_repositories/
│   └── test_utils/
├── integration/
│   ├── test_elasticsearch/
│   └── test_api/
└── fixtures/
    └── sample_data/
```

### Ejecutar Tests

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=backend

# Ejecutar solo tests unitarios
pytest tests/unit/

# Ejecutar solo tests de integración
pytest tests/integration/
```

## 🛠️ Desarrollo

### Inyección de Dependencias

La aplicación usa el sistema de dependencias de FastAPI:

```python
# En un endpoint
@router.get("/buscar")
async def buscar(
    palabra: str,
    search_service: SearchService = Depends(get_search_service)
):
    return await search_service.buscar_transcripciones(palabra)

# Para testing, es fácil crear mocks
def get_mock_search_service():
    return MockSearchService()

app.dependency_overrides[get_search_service] = get_mock_search_service
```

### Agregando Nueva Funcionalidad

#### 1. Agregar nuevo endpoint:

```python
# En backend/api/v1/routes/nueva_funcionalidad.py
@router.get("/nuevo-endpoint")
async def nuevo_endpoint(service: MiServicio = Depends(get_mi_servicio)):
    return await service.hacer_algo()
```

#### 2. Agregar nueva lógica de negocio:

```python
# En backend/services/mi_servicio.py
class MiServicio:
    def __init__(self, repo: MiRepositorio):
        self.repo = repo
    
    async def hacer_algo(self):
        # Lógica de negocio aquí
        return await self.repo.obtener_datos()
```

#### 3. Agregar nuevo repositorio:

```python
# En backend/repositories/mi_repositorio.py
class MiRepositorio(MiRepositorioInterface):
    async def obtener_datos(self):
        # Acceso a datos aquí
        pass
```

### Linting y Formateo

```bash
# Formatear código
black backend/

# Linting
flake8 backend/

# Type checking
mypy backend/
```

## 🔒 Seguridad

### Variables de Entorno Sensibles

- Nunca commitear el archivo `.env` con datos reales
- Usar `backend/config/.env.example` como plantilla
- En producción, usar variables de entorno del sistema o secretos seguros

### CORS

Por defecto permite todos los orígenes (`["*"]`). En producción:

```python
ALLOWED_ORIGINS = [
    "https://tu-dominio.com",
    "https://frontend.tu-dominio.com"
]
```

## 🚀 Despliegue

### Usando Docker

```dockerfile
# Dockerfile para el backend
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
EXPOSE 8000

CMD ["uvicorn", "backend.main_new:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Usando Systemd (Linux)

```ini
# /etc/systemd/system/microservicio-clips.service
[Unit]
Description=Microservicio de Clips
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/app
ExecStart=/path/to/venv/bin/uvicorn backend.main_new:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📈 Monitoreo y Logs

### Configuración de Logs

```python
# En backend/config/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("microservicio-clips")
```

### Métricas Recomendadas

- Tiempo de respuesta de endpoints
- Errores de Elasticsearch
- Uso de almacenamiento (clips generados)
- Tiempo de procesamiento de concatenación de videos

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para la nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commitear cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

### Estándares de Código

- Seguir PEP 8
- Documentar funciones y clases
- Escribir tests para nueva funcionalidad
- Usar type hints
- Mantener cobertura de tests > 80%

## 📄 Licencia

[Especificar licencia del proyecto]

## 🆘 Troubleshooting

### Problemas Comunes

#### Error de conexión a Elasticsearch
```bash
# Verificar que Elasticsearch esté corriendo
docker ps | grep elasticsearch

# Ver logs de Elasticsearch
docker-compose logs elasticsearch
```

#### Error con FFmpeg
```bash
# Verificar que FFmpeg esté instalado
ffmpeg -version

# En Ubuntu/Debian
sudo apt install ffmpeg

# En Windows
# Descargar desde https://ffmpeg.org/download.html
```

#### Error de zona horaria
```bash
# Instalar pytz
pip install pytz

# Verificar zona horaria disponible
python -c "import pytz; print('America/Argentina/Buenos_Aires' in pytz.all_timezones)"
```

#### Problemas de permisos con directorios
```bash
# Crear directorios necesarios
mkdir -p canales clips

# Ajustar permisos (Linux)
chmod 755 canales clips
```

---

**¿Necesitas ayuda?** Abre un issue en el repositorio con detalles del problema y los logs relevantes.