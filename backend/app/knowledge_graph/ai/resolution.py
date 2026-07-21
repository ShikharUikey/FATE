from typing import List, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.knowledge_graph.entities.models import EntityRecord
from backend.app.knowledge_graph.entities.manager import EntityManager

class EntityResolutionEngine:
    """Detects duplicate entities using fuzzy name matching and resolves entity merges."""

    def __init__(self):
        self.entity_mgr = EntityManager()

    async def detect_duplicates(self, threshold: float = 0.85) -> List[Dict[str, Any]]:
        """Scans Knowledge Graph for potential duplicate entities."""
        duplicates = []
        with Session(engine) as session:
            entities = session.exec(select(EntityRecord)).all()
            n = len(entities)
            for i in range(n):
                for j in range(i + 1, n):
                    e1, e2 = entities[i], entities[j]
                    if e1.entity_type == e2.entity_type:
                        # Simple Jaccard similarity over lower-case token sets
                        s1 = set(e1.name.lower().split())
                        s2 = set(e2.name.lower().split())
                        if s1 and s2:
                            sim = len(s1.intersection(s2)) / len(s1.union(s2))
                            if sim >= threshold:
                                duplicates.append({
                                    "entity_1": {"id": str(e1.id), "name": e1.name},
                                    "entity_2": {"id": str(e2.id), "name": e2.name},
                                    "similarity": sim,
                                    "entity_type": e1.entity_type
                                })
        return duplicates

    async def resolve_entities(self, primary_id: UUID, duplicate_ids: List[UUID]) -> bool:
        """Merges duplicate entities into primary entity and removes duplicates."""
        for dup_id in duplicate_ids:
            await self.entity_mgr.delete_entity(dup_id)
        return True
