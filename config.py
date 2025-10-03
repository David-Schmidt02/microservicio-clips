import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "https://172.20.100.40:9200")
ELASTIC_USER = os.getenv("ELASTIC_USER", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "davidadrian09")