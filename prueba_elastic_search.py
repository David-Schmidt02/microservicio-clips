from elasticsearch import Elasticsearch
# Definiciones de Elasticsearch
    # - Documento -> Análogo a una fila, una entidad, un objeto
    # - Índice -> Análogo a una tabla, colección de documentos


# Conectar al servidor (por defecto localhost:9200)
es = Elasticsearch("http://localhost:9200")

# 1. Indexar (guardar) un documento en un índice llamado "libros"
doc = {
    "titulo": "El Quijote",
    "autor": "Miguel de Cervantes",
    "año": 1605,
    "categoria": "Novela"
}

res = es.index(index="libros", document=doc)
print("Documento indexado:", res["_id"])

# 2. Buscar documentos con la palabra "Quijote"
query = {
    "query": {
        "match": {
            "titulo": "Quijote"
        }
    }
}

res = es.search(index="libros", body=query)
print("Resultados encontrados:")
for hit in res["hits"]["hits"]:
    print(hit["_source"])
