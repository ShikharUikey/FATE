from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from typing import List, Dict, Any

class VectorDBClient:
    """Wrapper class managing FATE's local Qdrant collections and search operations."""
    
    def __init__(self, location: str = ":memory:"):
        self.client = QdrantClient(location=location)
        self.vector_dim = 384  # Standard dimensions for MiniLM embedding models

    def init_collections(self):
        """Initializes collections if they do not already exist in Qdrant."""
        collections = ["user_memories", "document_chunks"]
        for col in collections:
            try:
                # Check if collection exists
                self.client.get_collection(col)
            except Exception:
                # Create the collection with standard cosine distance indexing
                self.client.create_collection(
                    collection_name=col,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE)
                )

    def upsert_embedding(self, collection: str, point_id: str, vector: List[float], payload: Dict[str, Any]):
        """Indexes or updates a single text embedding point in the target Qdrant collection."""
        self.init_collections()
        self.client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search_similar(self, collection: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Queries Qdrant returning the closest metadata payloads matching the query vector."""
        self.init_collections()
        response = self.client.query_points(
            collection_name=collection,
            query=query_vector,
            limit=limit
        )
        return [res.payload for res in response.points]
