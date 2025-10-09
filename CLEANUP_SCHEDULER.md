# Sistema de Limpieza Automática de Clips

## 📋 Descripción

El sistema de limpieza automática elimina clips temporales antiguos de forma programada, evitando que se acumulen archivos innecesarios y ocupen espacio en disco.

## 🚀 Instalación

### 1. Instalar la dependencia APScheduler

```bash
pip install APScheduler>=3.10.0
```

O instalar todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

El scheduler se configura mediante variables de entorno en `backend/config/.env`:

```env
# Habilitar/deshabilitar limpieza automática
CLEANUP_ENABLED=True

# Cada cuántas horas ejecutar la limpieza
CLEANUP_INTERVAL_HOURS=1

# Edad máxima de clips a mantener (en horas)
CLEANUP_MAX_AGE_HOURS=2
```

### Valores por defecto:
- `CLEANUP_ENABLED`: `True` (habilitado)
- `CLEANUP_INTERVAL_HOURS`: `1` (ejecuta cada 1 hora)
- `CLEANUP_MAX_AGE_HOURS`: `2` (elimina clips de más de 2 horas)

## 🎯 Funcionamiento

### Inicio automático
El scheduler se inicia automáticamente al levantar la aplicación FastAPI:

```bash
# Al ejecutar uvicorn
uvicorn backend.main:app --reload
```

Verás en la consola:

```
============================================================
🚀 Iniciando Microservicio de Clips v1.0.0
============================================================

🕐 Scheduler de limpieza iniciado:
   - Intervalo: cada 1 hora(s)
   - Elimina clips de más de 2 hora(s)
   - Directorio: C:\...\clips

============================================================
```

### Ejecuciones programadas
Cada hora (o el intervalo configurado), verás en la consola:

```
🧹 Limpieza automática ejecutada:
   ✅ 3 archivo(s) eliminado(s)
      - C13-20250109_143022_145522.mp4
      - TN-20250109_120530_122030.mp4
      - A24-20250109_095015_100515.mp4
```

Si no hay clips antiguos:
```
✓ Limpieza automática: No hay clips antiguos para eliminar
```

## 📡 Endpoints de la API

### 1. Estado del Scheduler
```bash
GET /api/v1/maintenance/scheduler/status
```

**Respuesta cuando está activo:**
```json
{
  "activo": true,
  "tareas": 1,
  "proxima_ejecucion": "2025-01-09T17:00:00-03:00",
  "nombre_tarea": "Limpieza de clips cada 1h"
}
```

**Respuesta cuando está inactivo:**
```json
{
  "activo": false,
  "mensaje": "Scheduler no está ejecutándose"
}
```

### 2. Limpieza manual (forzar)
```bash
POST /api/v1/maintenance/cleanup?max_age_hours=2
```

**Respuesta:**
```json
{
  "message": "Limpieza completada: 3 archivo(s) eliminado(s)",
  "cantidad_eliminados": 3,
  "archivos_eliminados": [
    "C13-20250109_143022_145522.mp4",
    "TN-20250109_120530_122030.mp4",
    "A24-20250109_095015_100515.mp4"
  ]
}
```

### 3. Estadísticas de clips
```bash
GET /api/v1/maintenance/stats
```

**Respuesta:**
```json
{
  "cantidad_clips": 15,
  "tamano_total_mb": 245.67,
  "clip_mas_antiguo": "2025-01-09 12:30:45",
  "clip_mas_reciente": "2025-01-09 16:22:10"
}
```

## 🔧 Personalización

### Cambiar el intervalo de limpieza

Opción 1: Modificar `.env`:
```env
CLEANUP_INTERVAL_HOURS=6  # Ejecutar cada 6 horas
CLEANUP_MAX_AGE_HOURS=12  # Eliminar clips de más de 12 horas
```

Opción 2: Modificar `backend/main.py` directamente:
```python
cleanup_scheduler.iniciar(
    intervalo_horas=6,    # Ejecutar cada 6 horas
    max_age_hours=12      # Eliminar clips de más de 12 horas
)
```

### Deshabilitar la limpieza automática

En `.env`:
```env
CLEANUP_ENABLED=False
```

Verás en la consola:
```
⚠️  Limpieza automática deshabilitada (CLEANUP_ENABLED=False)
```

## 🛠️ Casos de uso

### Desarrollo local
```env
CLEANUP_ENABLED=False  # Deshabilitado para debugging
```

### Entorno de pruebas
```env
CLEANUP_ENABLED=True
CLEANUP_INTERVAL_HOURS=1
CLEANUP_MAX_AGE_HOURS=1  # Limpieza agresiva
```

### Producción
```env
CLEANUP_ENABLED=True
CLEANUP_INTERVAL_HOURS=6
CLEANUP_MAX_AGE_HOURS=24  # Mantener clips del día
```

## 📝 Notas importantes

1. **Solo elimina archivos `.mp4`**: El scheduler solo elimina clips generados, NO los videos originales `.ts`

2. **No afecta a archivos en uso**: Si un archivo está siendo descargado, la eliminación fallará de forma segura

3. **Multiplataforma**: Funciona en Windows, Linux y macOS sin configuración adicional

4. **No requiere permisos especiales**: No necesita acceso root/administrador

5. **Se detiene con la aplicación**: Cuando detienes FastAPI, el scheduler también se detiene

## 🐛 Troubleshooting

### El scheduler no inicia
- Verifica que APScheduler esté instalado: `pip install APScheduler`
- Revisa que `CLEANUP_ENABLED=True` en `.env`
- Verifica la consola al iniciar la app

### No se eliminan archivos
- Confirma que los clips tengan más antigüedad que `CLEANUP_MAX_AGE_HOURS`
- Verifica permisos de escritura en el directorio `clips/`
- Revisa la consola para mensajes de error

### Errores en la consola
```
❌ Error en limpieza automática: [Errno 13] Permission denied
```
Solución: Verifica permisos del directorio `clips/`

## 📚 Archivos relacionados

- **Configuración**: `backend/config/settings.py:130-142`
- **Scheduler**: `backend/scheduler/cleanup_scheduler.py`
- **Servicio**: `backend/services/cleanup_service.py`
- **Endpoints**: `backend/api/v1/routes/maintenance.py`
- **Integración**: `backend/main.py:17-45`
