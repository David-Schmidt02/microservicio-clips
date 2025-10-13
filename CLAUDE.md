# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANTE: Siempre responde en español al trabajar en este proyecto.**

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
- **Task scheduling**: APScheduler for automated cleanup
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
├── main.py                      # FastAPI app entry point (with lifespan management)
├── config/
│   ├── settings.py              # Centralized config with Pydantic
│   └── .env                     # Environment variables
├── api/
│   ├── dependencies.py          # Dependency injection (repos, services, controllers)
│   └── v1/
│       ├── main.py              # API v1 router
│       └── routes/
│           ├── search.py        # Search endpoints (thin layer)
│           ├── clips.py         # Video/clip endpoints (thin layer)
│           └── maintenance.py   # Cleanup and stats endpoints
├── controllers/
│   ├── search_controller.py    # HTTP logic and input validation for search
│   └── video_controller.py     # HTTP logic and input validation for videos
├── services/
│   ├── search_service.py        # Search business logic (no try-catch)
│   ├── video_service.py         # Video processing logic (no try-catch)
│   └── cleanup_service.py       # Clip cleanup logic
├── repositories/
│   ├── base.py                  # Abstract interfaces
│   ├── elasticsearch_repo.py   # ES data access (no try-catch)
│   └── file_system_repo.py     # File system data access (no try-catch)
├── models/
│   ├── domain.py                # Domain entities (Transcripcion, Video)
│   └── schemas.py               # Pydantic request/response models
├── scheduler/
│   ├── cleanup_scheduler.py    # APScheduler for automated cleanup
│   └── instances.py            # Shared scheduler instances
├── middleware/
│   ├── transcriptionsHandleError.py  # Catches all transcription-related errors
│   └── videosHandleError.py          # Catches all video-related errors
└── utils/
    ├── time_utils.py            # Timestamp utilities
    └── validation.py            # Input validation utilities
```

**Layer responsibilities:**
- **Routes layer**: Define HTTP endpoints, delegate to controllers (ultra thin)
- **Controllers layer**: HTTP handling, input validation, response formatting
- **Services layer**: Business logic, orchestration (no HTTP details, no try-catch)
- **Repositories layer**: Data access (no try-catch, let errors propagate)
- **Middleware layer**: Error handling for all layers (catches and formats errors)
- **Models layer**: Data structures and contracts

**Error handling flow:**
1. Controllers validate HTTP inputs and raise `HTTPException` for bad requests
2. Services/Repositories raise domain exceptions (`ValueError`, `FileNotFoundError`, `RuntimeError`)
3. Middlewares catch all exceptions and format appropriate HTTP responses
4. No try-catch blocks in services or repositories - clean separation of concerns

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

### Automated Cleanup System

The application includes an automated cleanup scheduler that runs in the background:

- **Scheduler**: Uses APScheduler (asyncio-based) to periodically clean old clips
- **Configuration**: Controlled via environment variables in `settings.py`:
  - `CLEANUP_ENABLED` (default: True) - Enable/disable automatic cleanup
  - `CLEANUP_INTERVAL_HOURS` (default: 1.0) - How often to run cleanup
  - `CLEANUP_MAX_AGE_HOURS` (default: 2.0) - Delete clips older than this
- **Lifecycle**: Scheduler starts/stops with the FastAPI application lifespan
- **Implementation**: `backend/scheduler/cleanup_scheduler.py` and `backend/services/cleanup_service.py`
- **Manual control**: Use maintenance endpoints to trigger cleanup or check status

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

# Cleanup configuration (optional)
CLEANUP_ENABLED=true
CLEANUP_INTERVAL_HOURS=1.0
CLEANUP_MAX_AGE_HOURS=2.0
```

### Switching Between Dev/Prod Elasticsearch Indices

Edit `backend/config/settings.py`:
- Production: `ELASTICSEARCH_INDEX="streaming_tv"`
- Development: `ELASTICSEARCH_INDEX="streaming_tv_test"`

## Common Tasks

### Adding a New Endpoint

1. **Define Pydantic schemas** in `backend/models/schemas.py`
2. **Add repository method** in appropriate repo (e.g., `elasticsearch_repo.py`)
   - No try-catch blocks - let exceptions propagate
3. **Add service method** in appropriate service (e.g., `search_service.py`)
   - No try-catch blocks - focus on business logic
   - Raise `ValueError` for validation errors
4. **Add controller method** in appropriate controller (e.g., `search_controller.py`)
   - Validate HTTP inputs (path traversal, injection, etc.)
   - Call service methods
   - Transform responses to schemas
5. **Add route** in `backend/api/v1/routes/` (e.g., `search.py`)
   - Ultra thin - just define endpoint and delegate to controller
   - Use FastAPI's `Depends()` to inject controller
6. **Update frontend** `api.js` if needed

### Error Handling Architecture

The application uses **centralized error handling** through middlewares:

**How it works:**
1. **Controllers**: Validate inputs and raise `HTTPException` for bad requests (400, 404)
2. **Services/Repositories**: Raise domain exceptions without try-catch:
   - `ValueError` for validation/business rule violations
   - `FileNotFoundError` for missing resources
   - `RuntimeError` for processing errors (e.g., FFmpeg failures)
3. **Middlewares**: Catch exceptions and format HTTP responses:
   - `transcriptionsHandleError`: Handles Elasticsearch and transcription errors
   - `videosHandleError`: Handles file system and video processing errors

**Benefits:**
- Clean code without repetitive try-catch blocks
- Consistent error responses across all endpoints
- Easy to modify error handling globally
- Better separation of concerns

### Finding Videos by Timestamp

The `FileSystemRepository.obtener_videos_vecinos()` method:
1. Parses the target timestamp
2. Lists all `.ts` files in the channel directory
3. Finds the file whose time range contains the timestamp
4. Returns neighboring files based on `rango` parameter

**Important**: The search handles channel names with underscores (e.g., `olgaenvivo_`) correctly. Files are matched based on the channel prefix, so `olgaenvivo_20251007_120000_20251007_120130.ts` is found when searching for channel `olgaenvivo_`.

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

### Maintenance
- `POST /api/v1/maintenance/cleanup?max_age_hours={hours}` - Manually trigger cleanup
- `GET /api/v1/maintenance/stats` - Get statistics about stored clips
- `GET /api/v1/maintenance/scheduler/status` - Get scheduler status

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

## Application Lifecycle

The FastAPI application uses `@asynccontextmanager` for lifecycle management in `backend/main.py`:

**Startup**:
1. Prints startup banner with project name and version
2. Initializes cleanup scheduler if `CLEANUP_ENABLED=True`
3. Scheduler begins running in background

**Shutdown**:
1. Gracefully stops the cleanup scheduler
2. Ensures no cleanup tasks are left running

This pattern ensures clean startup/shutdown of background tasks.

## Important Notes

- **Never modify video file naming conventions** - the system relies on the timestamp format
- **Always validate timestamps** - use `time_utils.py` functions
- **Test with mock data first** - use `create_mock_videos.py` and `index_sample_data.py`
- **CORS is permissive** - restrict `ALLOWED_ORIGINS` in production
- **Automatic cleanup enabled by default** - configure via `CLEANUP_ENABLED` if you need to disable it
- **Channel names with underscores**: The system handles channel names like `olgaenvivo_` (trailing underscore)
