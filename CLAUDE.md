# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **video clip search and concatenation microservice** for TV streaming content. The system searches transcriptions stored in Elasticsearch and generates video clips by concatenating segments from the file system.

**Core functionality:**
- Search transcriptions by keyword in Elasticsearch
- Find video segments matching specific timestamps
- Concatenate video segments using FFmpeg
- Serve video clips with proper streaming headers

**Tech stack:**
- **Backend**: FastAPI (Python) with layered architecture
- **Database**: Elasticsearch for transcription search
- **Video processing**: FFmpeg for concatenation
- **Frontend**: Vanilla JavaScript (HTML/CSS/JS modules)
- **Timezone**: All timestamps use `America/Argentina/Buenos_Aires` (pytz)

## Development Commands

### Running the Application

```bash
# Backend (port 8001)
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (port 8080)
cd frontend && python -m http.server 8080

# Elasticsearch (Docker)
docker-compose up -d
```

### Testing & Quality

```bash
# Run tests (when implemented)
pytest
pytest --cov=backend

# Code formatting and linting
black backend/
flake8 backend/
mypy backend/
```

### Mock Data Generation

```bash
# Create mock video files for testing
python create_mock_videos.py

# Index sample transcription data to Elasticsearch
python index_sample_data.py
```

### Health Checks

```bash
# Backend health
curl http://localhost:8001/health

# Elasticsearch health
curl http://localhost:9200/_cluster/health
```

## Architecture

### Backend Layered Architecture

The backend follows **Clean Architecture** principles with clear separation of concerns:

```
backend/
├── main.py                      # FastAPI app entry point
├── config/
│   ├── settings.py              # Centralized config with Pydantic
│   └── .env                     # Environment variables
├── api/
│   ├── dependencies.py          # Dependency injection
│   └── v1/
│       ├── main.py              # API v1 router
│       └── routes/
│           ├── search.py        # Search endpoints
│           └── clips.py         # Video/clip endpoints
├── services/
│   ├── search_service.py        # Search business logic
│   └── video_service.py         # Video processing logic
├── repositories/
│   ├── base.py                  # Abstract interfaces
│   ├── elasticsearch_repo.py   # ES data access
│   └── file_system_repo.py     # File system data access
├── models/
│   ├── domain.py                # Domain entities (Transcripcion, Video)
│   └── schemas.py               # Pydantic request/response models
└── utils/
    └── time_utils.py            # Timestamp utilities
```

**Layer responsibilities:**
- **API layer**: HTTP handling, validation, serialization (no business logic)
- **Services layer**: Business logic, orchestration, validation (no HTTP/DB details)
- **Repositories layer**: Data access (Elasticsearch, file system)
- **Models layer**: Data structures and contracts

### Frontend Architecture

```
frontend/
├── index.html
├── css/
└── js/
    ├── main.js      # Entry point, coordinates modules
    ├── api.js       # Backend HTTP communication
    ├── ui.js        # DOM manipulation
    ├── player.js    # Video player control
    ├── state.js     # Application state
    ├── channels.js  # Channel configuration
    └── utils.js     # Utilities
```

## Key Implementation Details

### Timestamp Handling

**CRITICAL**: All timestamps are timezone-aware using `America/Argentina/Buenos_Aires` (pytz).

- Video filenames use format: `{canal}_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.ts`
- Elasticsearch timestamps are ISO 8601 with timezone
- Always use `backend/utils/time_utils.py` for parsing/formatting
- Never use `ZoneInfo` (cross-platform compatibility issue) - use `pytz` instead

### Video File Structure

Videos are organized by channel in the `canales/` directory:
```
canales/
├── todonoticias/
│   ├── todonoticias_20251007_120000_20251007_120130.ts
│   └── ...
├── luzutv/
└── olgaenvivo_/
```

Each video segment is 90 seconds (configurable via `DEFAULT_CLIP_DURATION`).

### Video Concatenation

The system uses FFmpeg's concat demuxer:
1. Creates a temporary list file with input video paths
2. Runs: `ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4`
3. Output filename format: `{canal}-{fecha}_{hora_inicio}_{hora_fin}.mp4`
4. Generated clips are stored in `clips/` directory

### Elasticsearch Search

Search queries:
- Filter to last 24 hours by default
- Aggregate results by channel (`slug.keyword`)
- Return top 10 results per channel
- Use `@timestamp` field for temporal queries

### API Versioning

The backend maintains **backward compatibility** with legacy endpoints:
- New API: `/api/v1/search/buscar`, `/api/v1/clips/concatenar`, etc.
- Legacy API: `/buscar`, `/concatenar`, etc. (redirects to new API)

Both APIs are functional; new code should use `/api/v1` endpoints.

## Configuration

### Environment Variables

Create `backend/config/.env` based on `.env.example`:

```bash
ELASTIC_URL=https://172.20.100.40:9200
ELASTIC_USER=elastic
ELASTIC_PASSWORD=your_password
ELASTICSEARCH_INDEX=streaming_tv        # or streaming_tv_test for dev
TIMEZONE_NAME=America/Argentina/Buenos_Aires
VIDEO_DIR=canales
OUTPUT_DIR=clips
FFMPEG_BIN=ffmpeg
```

### Switching Between Dev/Prod Elasticsearch Indices

Edit `backend/config/settings.py`:
- Production: `ELASTICSEARCH_INDEX="streaming_tv"`
- Development: `ELASTICSEARCH_INDEX="streaming_tv_test"`

## Common Tasks

### Adding a New Endpoint

1. **Define Pydantic schemas** in `backend/models/schemas.py`
2. **Add repository method** in appropriate repo (e.g., `elasticsearch_repo.py`)
3. **Add service method** in appropriate service (e.g., `search_service.py`)
4. **Add route** in `backend/api/v1/routes/` (e.g., `search.py`)
5. **Update frontend** `api.js` if needed

### Finding Videos by Timestamp

The `FileSystemRepository.obtener_videos_vecinos()` method:
1. Parses the target timestamp
2. Lists all `.ts` files in the channel directory
3. Finds the file whose time range contains the timestamp
4. Returns neighboring files based on `rango` parameter

### Debugging Video Concatenation Issues

The repository includes debug print statements:
- Check `backend/repositories/file_system_repo.py` for debug output
- Verify input file paths exist before concatenation
- Check FFmpeg error output in subprocess exceptions
- Inspect the temporary list file generated for concat

### Frontend-Backend Communication

The frontend **must not modify backend endpoints** (see `frontend/API-COMMUNICATION.md`).

**API Base URL**: Configured in `frontend/js/api.js`:
```javascript
const CONFIG = { API_BASE_URL: "http://127.0.0.1:8001" };
```

## Known Issues & Workarounds

### Timezone Handling
- All code now uses `pytz` (not `ZoneInfo`) for cross-platform compatibility
- Timestamps in filenames are compared as naive datetimes (all in Argentina timezone)

### FFmpeg Requirements
- FFmpeg must be installed and accessible in PATH
- On Windows, download from https://ffmpeg.org/download.html
- Verify with: `ffmpeg -version`

### Mock Video Generation
- `create_mock_videos.py` creates test videos with test patterns
- If font rendering fails, it falls back to videos without text overlay

## API Endpoints Reference

### Search
- `GET /api/v1/search/buscar?palabra={palabra}` - Search transcriptions
- `GET /api/v1/search/transcripcionClip?canal={canal}&timestamp={timestamp}&duracion_segundos={duracion}` - Get clip transcription

### Videos/Clips
- `GET /api/v1/clips/videos?canal={canal}&timestamp={timestamp}&rango={rango}` - Get neighboring videos
- `POST /api/v1/clips/concatenar` - Concatenate videos (body: `{canal, videos[]}`)
- `GET /api/v1/clips/descargar?clip={clip}` - Download generated clip
- `GET /api/v1/clips/video/{canal}/{archivo}` - Serve individual video file

### Health
- `GET /health` - Service health check

Full API documentation: http://localhost:8001/api/v1/docs

## Dependency Injection

The application uses FastAPI's dependency injection:

```python
# In routes
@router.get("/buscar")
async def buscar(
    palabra: str,
    search_service: SearchService = Depends(get_search_service)
):
    return await search_service.buscar_transcripciones(palabra)
```

Dependencies are defined in `backend/api/dependencies.py`.

For testing, override dependencies:
```python
app.dependency_overrides[get_search_service] = lambda: MockSearchService()
```

## Git Workflow

- Main branch: `main`
- Development branch: `development` (current)
- Recent commits focus on timezone fixes and layered architecture refactoring

## Important Notes

- **Never modify video file naming conventions** - the system relies on the timestamp format
- **Always validate timestamps** - use `time_utils.py` functions
- **Test with mock data first** - use `create_mock_videos.py` and `index_sample_data.py`
- **CORS is permissive** - restrict `ALLOWED_ORIGINS` in production
- **Clean up generated clips** - the `clips/` directory grows over time
