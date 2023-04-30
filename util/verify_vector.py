from qdrant_client import QdrantClient


qdrant_client = QdrantClient(host="localhost", port=6333, timeout=30)
print(qdrant_client.get_collections())
print(qdrant_client.get_collection(collection_name='wiki_collection'))
