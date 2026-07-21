from typing import Dict, Any, List, Optional
from uuid import UUID
from backend.app.knowledge_graph.entities.manager import EntityManager
from backend.app.knowledge_graph.graph_engine.traversal import GraphTraversalEngine
from backend.app.knowledge_graph.semantic_search.hybrid_search import HybridSearchEngine

class AIContextEngine:
    """Provides structured Knowledge Graph context expansion and dependency retrieval for LLMs."""

    def __init__(self):
        self.entity_mgr = EntityManager()
        self.traversal = GraphTraversalEngine()
        self.search_engine = HybridSearchEngine()

    async def generate_structured_context(
        self,
        query: str,
        root_entity_id: Optional[UUID] = None,
        max_hops: int = 2
    ) -> Dict[str, Any]:
        """Generates interconnected graph context formatted for LLM system prompt injection."""
        context_data = {
            "query": query,
            "matched_entities": [],
            "subgraph": {"nodes": [], "edges": []},
            "formatted_prompt_context": ""
        }

        # Find initial seed entities
        search_results = await self.search_engine.search(query, limit=5)
        context_data["matched_entities"] = search_results

        target_id = root_entity_id
        if not target_id and search_results:
            try:
                target_id = UUID(search_results[0]["entity"]["id"])
            except Exception:
                pass

        if target_id:
            subgraph = self.traversal.get_subgraph(target_id, max_depth=max_hops)
            context_data["subgraph"] = subgraph

        # Format readable markdown context for LLM prompt injection
        lines = ["### KNOWLEDGE GRAPH REASONING CONTEXT ###"]
        if search_results:
            lines.append("Relevant Entities:")
            for item in search_results:
                ent = item["entity"]
                lines.append(f"- [{ent.get('entity_type')}] {ent.get('name')}: {ent.get('description', '')}")

        if context_data["subgraph"]["edges"]:
            lines.append("\nEntity Relationships & Dependencies:")
            for edge in context_data["subgraph"]["edges"]:
                lines.append(f"- ({edge.get('source')}) --[{edge.get('relationship_type')}]--> ({edge.get('target')}) [Weight: {edge.get('weight')}]")

        context_data["formatted_prompt_context"] = "\n".join(lines)
        return context_data
