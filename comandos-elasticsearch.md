# Comandos Elasticsearch - Guía Práctica

## 🚀 Iniciar Elasticsearch
```bash
docker-compose up -d
```

## ✅ Verificar que esté funcionando
```bash
curl -X GET "http://localhost:9200/"
```

**Respuesta esperada:**
```json
{
  "name" : "ed73b93dfdb0",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "abc123...",
  "version" : {
    "number" : "8.13.4"
  },
  "tagline" : "You Know, for Search"
}
```

---

## 📁 Gestión de Índices

### Crear índice para transcripciones
```bash
curl -X PUT "http://localhost:9200/transcripciones"
```

### Ver todos los índices
```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

### Eliminar un índice
```bash
curl -X DELETE "http://localhost:9200/transcripciones"
```

---

## 📄 Gestión de Documentos

### 1. Agregar transcripción (ID automático)
```bash
curl -X POST "http://localhost:9200/transcripciones/_doc" -H 'Content-Type: application/json' -d'{
  "texto": "En este fragmento hablamos de microservicios y elasticsearch para búsquedas",
  "video": "video_1.mp4",
  "segundo_inicio": 75,
  "segundo_fin": 105,
  "timestamp": "2025-09-15T10:00:00",
  "tags": ["microservicios", "elasticsearch", "tecnología"]
}'
```

### 2. Agregar más transcripciones de ejemplo
```bash
curl -X POST "http://localhost:9200/transcripciones/_doc" -H 'Content-Type: application/json' -d'{
  "texto": "Aquí explicamos cómo usar Python con FastAPI para crear APIs REST",
  "video": "video_2.mp4", 
  "segundo_inicio": 120,
  "segundo_fin": 180,
  "timestamp": "2025-09-15T10:05:00",
  "tags": ["python", "fastapi", "api"]
}'
```

```bash
curl -X POST "http://localhost:9200/transcripciones/_doc" -H 'Content-Type: application/json' -d'{
  "texto": "Docker containers nos permiten empaquetar aplicaciones con sus dependencias",
  "video": "video_3.mp4",
  "segundo_inicio": 200,
  "segundo_fin": 240, 
  "timestamp": "2025-09-15T10:10:00",
  "tags": ["docker", "containers", "devops"]
}'
```

### 3. Obtener documento por ID
```bash
curl -X GET "http://localhost:9200/transcripciones/_doc/ID_DEL_DOCUMENTO"
```

---

## 🔍 Búsquedas

### Búsqueda simple por texto
```bash
curl -X GET "http://localhost:9200/transcripciones/_search?q=microservicios"
```

### Búsqueda en campo específico
```bash
curl -X GET "http://localhost:9200/transcripciones/_search?q=video:video_1.mp4"
```

### Búsqueda avanzada - Match query
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "match": {
      "texto": "microservicios elasticsearch"
    }
  }
}'
```

### Búsqueda en múltiples campos
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "multi_match": {
      "query": "python",
      "fields": ["texto", "tags"]
    }
  }
}'
```

### Búsqueda por rango de tiempo
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "range": {
      "segundo_inicio": {
        "gte": 60,
        "lte": 180
      }
    }
  }
}'
```

### Búsqueda combinada (Bool Query)
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "bool": {
      "must": [
        {"match": {"texto": "python"}},
        {"term": {"video": "video_2.mp4"}}
      ],
      "filter": [
        {"range": {"segundo_inicio": {"gte": 100}}}
      ]
    }
  }
}'
```

---

## 📊 Casos de Uso Específicos

### Buscar clips de un video específico
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "term": {
      "video": "video_1.mp4"
    }
  },
  "sort": [
    {"segundo_inicio": {"order": "asc"}}
  ]
}'
```

### Buscar por palabras clave en tags
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "terms": {
      "tags": ["python", "fastapi", "docker"]
    }
  }
}'
```

### Contar transcripciones por video
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "size": 0,
  "aggs": {
    "videos": {
      "terms": {
        "field": "video.keyword"
      }
    }
  }
}'
```

---

## 🛠️ Utilidades

### Ver todas las transcripciones
```bash
curl -X GET "http://localhost:9200/transcripciones/_search" -H 'Content-Type: application/json' -d'{
  "query": {
    "match_all": {}
  }
}'
```

### Contar documentos total
```bash
curl -X GET "http://localhost:9200/transcripciones/_count"
```

### Ver mapping (estructura) del índice
```bash
curl -X GET "http://localhost:9200/transcripciones/_mapping"
```

### Salud del cluster
```bash
curl -X GET "http://localhost:9200/_cluster/health"
```

---

## 🔧 Para tu aplicación FastAPI

### Instalar librería de Python
```bash
pip install elasticsearch
```

### Ejemplo de conexión en Python
```python
from elasticsearch import Elasticsearch

# Conectar
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Buscar
result = es.search(
    index="transcripciones",
    body={
        "query": {
            "match": {"texto": "microservicios"}
        }
    }
)
```
