# Elasticsearch con Docker

## Levantar Elasticsearch

Para iniciar Elasticsearch usando Docker Compose:

```bash
docker-compose up -d
```

## Verificar que funciona

1. Espera unos segundos a que el contenedor inicie completamente
2. Visita http://localhost:9200 en tu navegador
3. O desde terminal:
   ```bash
   curl http://localhost:9200
   ```

## Comandos útiles

### Ver logs de Elasticsearch
```bash
docker-compose logs -f elasticsearch
```

### Detener Elasticsearch
```bash
docker-compose down
```

### Detener y eliminar datos
```bash
docker-compose down -v
```

## Comandos básicos de Elasticsearch

### Crear un índice
```bash
curl -X PUT "localhost:9200/mi_indice"
```

### Agregar un documento
```bash
curl -X POST "localhost:9200/mi_indice/_doc" \
-H "Content-Type: application/json" \
-d '{"campo": "valor", "fecha": "2025-09-15"}'
```

### Buscar documentos
```bash
curl -X GET "localhost:9200/mi_indice/_search?q=valor"
```

### Ver todos los índices
```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

## Características de esta configuración

- **Puerto 9200**: API REST de Elasticsearch
- **Puerto 9300**: Comunicación entre nodos (no necesario en modo single-node)
- **Seguridad deshabilitada**: Para desarrollo local
- **Memoria limitada**: 512MB para no consumir demasiados recursos
- **Datos persistentes**: Se guardan en un volumen de Docker
- **Health check**: Verifica que el servicio esté funcionando

## Endpoints principales de Elasticsearch

### 📋 Gestión de Índices

#### Crear un índice
```bash
curl -X PUT "localhost:9200/transcripciones"
```

#### Ver todos los índices
```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

#### Obtener información de un índice
```bash
curl -X GET "localhost:9200/transcripciones"
```

#### Eliminar un índice
```bash
curl -X DELETE "localhost:9200/transcripciones"
```

### 📄 Gestión de Documentos

#### Agregar un documento (con ID automático)
```bash
curl -X POST "localhost:9200/transcripciones/_doc" \
-H "Content-Type: application/json" \
-d '{
  "texto": "En este video hablamos de microservicios",
  "video": "video_1.mp4",
  "segundo_inicio": 75,
  "timestamp": "2025-09-15T10:00:00"
}'
```

#### Agregar un documento (con ID específico)
```bash
curl -X PUT "localhost:9200/transcripciones/_doc/1" \
-H "Content-Type: application/json" \
-d '{
  "texto": "Ejemplo con ID específico",
  "video": "video_2.mp4",
  "segundo_inicio": 120
}'
```

#### Obtener un documento por ID
```bash
curl -X GET "localhost:9200/transcripciones/_doc/1"
```

#### Actualizar un documento
```bash
curl -X POST "localhost:9200/transcripciones/_update/1" \
-H "Content-Type: application/json" \
-d '{
  "doc": {
    "segundo_inicio": 130
  }
}'
```

#### Eliminar un documento
```bash
curl -X DELETE "localhost:9200/transcripciones/_doc/1"
```

### 🔍 Búsquedas Básicas

#### Buscar en todos los documentos
```bash
curl -X GET "localhost:9200/transcripciones/_search"
```

#### Búsqueda simple (query string)
```bash
curl -X GET "localhost:9200/transcripciones/_search?q=microservicios"
```

#### Búsqueda en un campo específico
```bash
curl -X GET "localhost:9200/transcripciones/_search?q=texto:python"
```

### 🎯 Búsquedas Avanzadas (Query DSL)

#### Match query (búsqueda de texto)
```bash
curl -X GET "localhost:9200/transcripciones/_search" \
-H "Content-Type: application/json" \
-d '{
  "query": {
    "match": {
      "texto": "microservicios"
    }
  }
}'
```

#### Multi-match (buscar en múltiples campos)
```bash
curl -X GET "localhost:9200/transcripciones/_search" \
-H "Content-Type: application/json" \
-d '{
  "query": {
    "multi_match": {
      "query": "python",
      "fields": ["texto", "video"]
    }
  }
}'
```

#### Bool query (consultas complejas con AND/OR)
```bash
curl -X GET "localhost:9200/transcripciones/_search" \
-H "Content-Type: application/json" \
-d '{
  "query": {
    "bool": {
      "must": [
        {"match": {"texto": "microservicios"}},
        {"range": {"segundo_inicio": {"gte": 60}}}
      ],
      "filter": [
        {"term": {"video": "video_1.mp4"}}
      ]
    }
  }
}'
```

#### Range query (rangos numéricos o de fechas)
```bash
curl -X GET "localhost:9200/transcripciones/_search" \
-H "Content-Type: application/json" \
-d '{
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

### 📊 Agregaciones (Analytics)

#### Contar documentos por video
```bash
curl -X GET "localhost:9200/transcripciones/_search" \
-H "Content-Type: application/json" \
-d '{
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

### 🛠️ Utilidades

#### Verificar salud del cluster
```bash
curl -X GET "localhost:9200/_cluster/health"
```

#### Ver estadísticas del índice
```bash
curl -X GET "localhost:9200/transcripciones/_stats"
```

#### Contar documentos en un índice
```bash
curl -X GET "localhost:9200/transcripciones/_count"
```

#### Mapping del índice (estructura de campos)
```bash
curl -X GET "localhost:9200/transcripciones/_mapping"
```

## Próximos pasos

1. Instalar la librería de Python: `pip install elasticsearch`
2. Conectar tu aplicación Python con Elasticsearch
3. Crear índices para tus transcripciones de video
4. Implementar búsquedas desde FastAPI