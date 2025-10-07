#!/usr/bin/env python3
"""
Script para indexar datos de ejemplo en Elasticsearch para testing
"""

import json
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Deshabilitar warnings SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de Elasticsearch
ELASTICSEARCH_URL = "https://172.20.100.40:9200"
ELASTICSEARCH_USER = "elastic" 
ELASTICSEARCH_PASSWORD = "7=cZYAocp_XYeNfjsuk5"  # Password from .env
INDEX_NAME = "streaming_tv_test"  # Índice separado para testing/desarrollo

def create_sample_documents():
    """Crear documentos de ejemplo que coincidan con los videos mock"""
    
    base_time = datetime(2025, 10, 7, 12, 0, 0)
    documents = []
    
    # Documentos para A24 (ajustado a UTC+3 para mostrar horario correcto en Argentina)
    a24_docs = [
        {
            "text": "El presidente anunció nuevas medidas económicas para combatir la inflación que afecta a todos los sectores",
            "slug": "a24",
            "name": "A24 Noticias",
            "@timestamp": "2025-10-07T15:00:30Z",
            "service": "streaming_tv",
            "channel_id": "a24_main"
        },
        {
            "text": "La crisis económica sigue siendo el tema principal en el debate político nacional",
            "slug": "a24", 
            "name": "A24 Noticias",
            "@timestamp": "2025-10-07T15:02:15Z",
            "service": "streaming_tv",
            "channel_id": "a24_main"
        },
        {
            "text": "Empresarios piden medidas urgentes para frenar la inflación y estabilizar la moneda",
            "slug": "a24",
            "name": "A24 Noticias", 
            "@timestamp": "2025-10-07T15:04:45Z",
            "service": "streaming_tv",
            "channel_id": "a24_main"
        }
    ]
    
    # Documentos para TN (ajustado a UTC+3 para mostrar horario correcto en Argentina)
    tn_docs = [
        {
            "text": "La selección argentina se prepara para el próximo mundial de fútbol con nuevos entrenamientos",
            "slug": "tn",
            "name": "Todo Noticias",
            "@timestamp": "2025-10-07T15:05:15Z", 
            "service": "streaming_tv",
            "channel_id": "tn_main"
        },
        {
            "text": "Messi lidera la lista de convocados para los próximos partidos de la selección",
            "slug": "tn",
            "name": "Todo Noticias",
            "@timestamp": "2025-10-07T15:06:30Z",
            "service": "streaming_tv", 
            "channel_id": "tn_main"
        },
        {
            "text": "El técnico de la selección confirmó la formación titular para el próximo encuentro",
            "slug": "tn",
            "name": "Todo Noticias",
            "@timestamp": "2025-10-07T15:08:10Z",
            "service": "streaming_tv",
            "channel_id": "tn_main"
        }
    ]
    
    # Documentos para C5N (ajustado a UTC+3 para mostrar horario correcto en Argentina)
    c5n_docs = [
        {
            "text": "Nuevas protestas en la capital por el aumento de precios en productos básicos",
            "slug": "c5n",
            "name": "C5N Noticias",
            "@timestamp": "2025-10-07T15:10:00Z",
            "service": "streaming_tv", 
            "channel_id": "c5n_main"
        },
        {
            "text": "Los manifestantes reclaman medidas para controlar el aumento del costo de vida",
            "slug": "c5n",
            "name": "C5N Noticias", 
            "@timestamp": "2025-10-07T15:11:20Z",
            "service": "streaming_tv",
            "channel_id": "c5n_main"
        },
        {
            "text": "Las protestas se extendieron por varias cuadras del centro porteño",
            "slug": "c5n",
            "name": "C5N Noticias",
            "@timestamp": "2025-10-07T15:12:45Z", 
            "service": "streaming_tv",
            "channel_id": "c5n_main"
        }
    ]
    
    return a24_docs + tn_docs + c5n_docs

def create_test_index():
    """Crear el índice de testing si no existe"""
    
    # Verificar si el índice ya existe
    auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    check_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}"
    
    try:
        response = requests.head(check_url, auth=auth, verify=False)
        if response.status_code == 200:
            print(f"✅ Índice {INDEX_NAME} ya existe")
            return True
    except Exception:
        pass
    
    # Crear el índice con mapping similar al original
    mapping = {
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "text": {"type": "text", "analyzer": "spanish"},
                "slug": {"type": "keyword"},
                "name": {"type": "text"},
                "service": {"type": "keyword"},
                "channel_id": {"type": "keyword"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    try:
        response = requests.put(
            check_url,
            json=mapping,
            headers={"Content-Type": "application/json"},
            auth=auth,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Índice de testing {INDEX_NAME} creado exitosamente")
            return True
        else:
            print(f"❌ Error creando índice: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creando índice: {e}")
        return False

def index_document(doc, doc_id=None):
    """Indexar un documento en Elasticsearch"""
    
    url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_doc"
    if doc_id:
        url += f"/{doc_id}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    
    try:
        response = requests.post(
            url,
            json=doc,
            headers=headers, 
            auth=auth,
            verify=False  # Deshabilitar verificación SSL para desarrollo
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Documento indexado: {doc['slug']} - {doc['text'][:50]}...")
            return True
        else:
            print(f"❌ Error indexando documento: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_elasticsearch_connection():
    """Verificar conexión con Elasticsearch"""
    
    try:
        auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
        response = requests.get(
            f"{ELASTICSEARCH_URL}/_cluster/health",
            auth=auth,
            verify=False
        )
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Elasticsearch conectado - Estado: {health.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Error conectando a Elasticsearch: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión a Elasticsearch: {e}")
        print("   Verifica que Elasticsearch esté ejecutándose en:", ELASTICSEARCH_URL)
        return False

def create_index_if_not_exists():
    """Crear el índice si no existe"""
    
    mapping = {
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "slug": {"type": "keyword"}, 
                "name": {"type": "text"},
                "@timestamp": {"type": "date"},
                "service": {"type": "keyword"},
                "channel_id": {"type": "keyword"}
            }
        }
    }
    
    auth = HTTPBasicAuth(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD)
    
    try:
        # Verificar si el índice existe
        response = requests.head(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}",
            auth=auth,
            verify=False
        )
        
        if response.status_code == 200:
            print(f"✅ Índice '{INDEX_NAME}' ya existe")
            return True
        
        # Crear el índice
        response = requests.put(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}",
            json=mapping,
            auth=auth,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Índice '{INDEX_NAME}' creado exitosamente")
            return True
        else:
            print(f"❌ Error creando índice: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error manejando índice: {e}")
        return False

def main():
    """Función principal"""
    
    print("🔍 Indexando datos de ejemplo en Elasticsearch (TESTING)")
    print(f"📍 Índice de destino: {INDEX_NAME}")
    print("=" * 50)
    
    # Verificar conexión
    if not check_elasticsearch_connection():
        return
    
    # Crear índice de testing si no existe
    if not create_test_index():
        return
    
    # Crear y indexar documentos
    documents = create_sample_documents()
    
    print(f"\n📄 Indexando {len(documents)} documentos de ejemplo...")
    
    success_count = 0
    for i, doc in enumerate(documents, 1):
        if index_document(doc, f"mock_{i}"):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Documentos indexados exitosamente: {success_count}/{len(documents)}")
    print(f"📊 Índice de testing: {INDEX_NAME}")
    
    if success_count > 0:
        print(f"\n🎯 Palabras clave para probar:")
        print(f"   - 'presidente' (A24)")
        print(f"   - 'selección' (TN)") 
        print(f"   - 'protestas' (C5N)")
        print(f"   - 'inflación' (A24)")
        print(f"   - 'fútbol' (TN)")
        print(f"   - 'precios' (C5N)")
        print(f"\n⚠️  NOTA: Para usar estos datos en la app, actualiza el backend")
        print(f"         para usar el índice '{INDEX_NAME}' en desarrollo")

if __name__ == "__main__":
    main()