# 🌐 Guía de Comunicación Frontend-Backend

## 📖 Introducción

Esta guía documenta todos los endpoints del backend y cómo el frontend debe comunicarse con ellos.

> **⚠️ IMPORTANTE**: Los endpoints del backend **NO DEBEN MODIFICARSE** sin coordinación.

## 📍 Configuración Base

```javascript
// Configuración en api.js
const CONFIG = {
  API_BASE_URL: "http://127.0.0.1:8000"
};
```

## 🛠️ Endpoints y Flujos

### 🔍 **1. Búsqueda de Transcripciones**

**Endpoint:**
```http
GET /api/v1/search/buscar?palabra={palabra}
```

**Request:**
```javascript
// Flujo completo de búsqueda
export async function buscarCoincidenciasElastic(palabra) {
    const params = new URLSearchParams({ palabra });
    const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/search/buscar?${params}`);
    return await response.json();
}
```

**Response:**
```json
{
  "resultados": [
    {
      "texto": "texto que contiene la palabra",
      "canal": "nombre_del_canal",
      "name": "titulo_del_video.mp4",
      "timestamp": "2023-12-05T14:30:22Z",
      "service": "nombre_del_servicio",
      "channel_id": "123456"
    }
  ]
}
```

---

### 📺 **2. Obtener Lista de Videos**

**Endpoint:**
```http
GET /api/v1/clips/videos?canal={canal}&timestamp_start={timestamp_start}&timestamp_end={timestamp_end}
```

**Request:**
```javascript
export async function obtenerListaVideos(canal, timestamp) {
    const params = new URLSearchParams({ 
        canal, 
        timestamp,
        rango: 3 
    });
    const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/clips/videos?${params}`);
    const data = await response.json();
    return data.videos || [];
}
```

---

### 🎬 **3. Obtener Transcripción de Clip**

**Endpoint:**
```http
GET /api/v1/search/transcripcionClip?canal={canal}&timestamp={timestamp}&duracion_segundos={duracion}
```

**Request:**
```javascript
export async function obtenerTranscripcionClip(canal, timestamp, duracion_segundos = 90) {
    const params = new URLSearchParams({
        canal,
        timestamp,
        duracion_segundos: duracion_segundos.toString()
    });
    const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/search/transcripcionClip?${params}`);
    return await response.json();
}
```

---

### 🔗 **4. Concatenar Videos**

**Endpoint:**
```http
POST /api/v1/clips/concatenar
```

**Request:**
```javascript
export async function concatenarClips(canal, videos) {
    const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/clips/concatenar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ canal, videos })
    });
    return await response.json();
}
```

**Body:**
```json
{
  "canal": "nombre_del_canal",
  "videos": ["video001.mp4", "video002.mp4", "video003.mp4"]
}
```

---

### ⬇️ **5. Descargar Archivo**

**Endpoint:**
```http
GET /api/v1/clips/descargar?clip={nombre_archivo}
```

**Request:**
```javascript
export function descargarArchivo(nombreArchivo) {
    const url = `${CONFIG.API_BASE_URL}/api/v1/clips/descargar?clip=${encodeURIComponent(nombreArchivo)}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = nombreArchivo;
    link.click();
}
```

## 🔄 Flujo de Datos Completo

### **📊 Flujo Principal de la Aplicación:**

```
1. Usuario busca → GET /api/v1/search/buscar?palabra={palabra}
   ↓
2. Mostrar resultados → Renderizar en UI
   ↓
3. Usuario selecciona clip → GET /api/v1/search/transcripcionClip?canal={canal}&timestamp={timestamp}
   ↓
4. Usuario busca videos relacionados → GET /api/v1/clips/videos?canal={canal}&timestamp_start={start}&timestamp_end={end}
   ↓ 
5. Usuario concatena clips → POST /api/v1/clips/concatenar
   ↓
6. Descargar resultado → GET /api/v1/clips/descargar?clip={archivo}
```

### **🔧 Configuración por Entorno:**

```javascript
// Para cambiar entre desarrollo y producción
const CONFIG = {
  API_BASE_URL: "http://127.0.0.1:8000"    // Desarrollo
  // API_BASE_URL: "https://api.tudominio.com"  // Producción
};
```

---

**⚠️ REGLA PRINCIPAL: NO modificar los endpoints, solo el frontend.**