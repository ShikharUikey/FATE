from typing import List, Dict, Any
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.core.vector_db import VectorDBClient
from backend.app.knowledge_graph.entities.models import EntityRecord
from backend.app.knowledge_graph.graph_engine.traversal import GraphTraversalEngine

vector_db = VectorDBClient()

class HybridSearchEngine:
    """Hybrid Search combining dense Qdrant vector retrieval with Knowledge Graph subgraphs (<300ms target)."""

    def __init__(self):
        self.traversal = GraphTraversalEngine()

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Executes hybrid semantic search over Knowledge Graph entities and vectors."""
        if not query:
            return []

        query_lower = query.lower().strip()
        matched_entities = []

        # 1. Relational Entity Name / Description Keyword Match
        with Session(engine) as session:
            all_entities = session.exec(select(EntityRecord)).all()
            for e in all_entities:
                score = 0.0
                if query_lower in e.name.lower():
                    score += 0.8
                if e.description and query_lower in e.description.lower():
                    score += 0.5
                for tag in e.tags:
                    if query_lower in tag.lower():
                        score += 0.6

                if score > 0.0:
                    matched_entities.append({
                        "entity": {
                            "id": str(e.id),
                            "name": e.name,
                            "entity_type": e.entity_type,
                            "description": e.description,
                            "tags": e.tags
                        },
                        "score": min(1.0, score),
                        "source": "graph_keyword"
                    })

        # 2. Vector Index Search
        try:
            vector_results = await vector_db.search_vectors("user_memories", query, limit=limit)
            for v in vector_results:
                matched_entities.append({
                    "entity": {
                        "id": str(v.get("id")),
                        "name": v.get("payload", {}).get("name", "Memory Node"),
                        "entity_type": "VectorMemory",
                        "description": v.get("payload", {}).get("text", "")
                    },
                    "score": float(v.get("score", 0.7)),
                    "source": "qdrant_vector"
                })
        except Exception:
            pass

        # Sort combined results by score descending
        matched_entities.sort(key=lambda item: item["score"], reverse=True)
        return matched_entities[:limit]
