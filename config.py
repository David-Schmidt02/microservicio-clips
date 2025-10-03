import os
from elasticsearch import Elasticsearch

ELASTIC_URL = os.getenv("ELASTIC_URL", "https://localhost:9200")
ELASTIC_USER = os.getenv("ELASTIC_USER", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "davidadrian09")