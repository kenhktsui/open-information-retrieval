from typing import List
from qdrant_client import QdrantClient
from oir.realm_encoder import RealmEncoder


class RealmRetriever:
    collection_name = "wiki_collection"

    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.encoder = RealmEncoder()
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

    def search(self,
               text: str,
               top_k: int,
               score_threshold: float,
               ) -> List[dict]:
        vector = self.encoder.encode(text)
        hits = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            with_payload=True,
            limit=top_k,
            score_threshold=score_threshold,
        )
        return [{**hit.payload, "score": hit.score} for hit in hits]
