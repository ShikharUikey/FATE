import networkx as nx
from typing import List, Dict, Any, Optional, Set
from uuid import UUID
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.knowledge_graph.entities.models import EntityRecord
from backend.app.knowledge_graph.relationships.engine import RelationshipRecord

class GraphTraversalEngine:
    """NetworkX + SQLite Graph Traverser for subgraphs, shortest paths, and visualization exports."""

    def build_networkx_graph(self) -> nx.DiGraph:
        """Constructs an in-memory NetworkX directed graph from SQLite persistence."""
        G = nx.DiGraph()
        with Session(engine) as session:
            entities = session.exec(select(EntityRecord)).all()
            for e in entities:
                G.add_node(
                    str(e.id),
                    name=e.name,
                    entity_type=e.entity_type,
                    description=e.description or "",
                    tags=e.tags
                )

            relationships = session.exec(select(RelationshipRecord)).all()
            for r in relationships:
                G.add_edge(
                    str(r.source_id),
                    str(r.target_id),
                    id=str(r.id),
                    relationship_type=r.relationship_type,
                    weight=r.weight,
                    confidence=r.confidence_score
                )
        return G

    def get_subgraph(self, root_id: UUID, max_depth: int = 2) -> Dict[str, Any]:
        """Extracts N-hop ego subgraph around root entity (<150ms target)."""
        G = self.build_networkx_graph()
        root_str = str(root_id)

        if root_str not in G:
            return {"nodes": [], "edges": []}

        # Single-source shortest path lengths to restrict depth
        lengths = nx.single_source_shortest_path_length(G.to_undirected(), root_str, cutoff=max_depth)
        sub_nodes: Set[str] = set(lengths.keys())
        subgraph = G.subgraph(sub_nodes)

        nodes = [{"id": n, **subgraph.nodes[n]} for n in subgraph.nodes()]
        edges = [
            {
                "source": u,
                "target": v,
                **subgraph.edges[u, v]
            }
            for u, v in subgraph.edges()
        ]

        return {"nodes": nodes, "edges": edges}

    def find_shortest_path(self, source_id: UUID, target_id: UUID) -> List[Dict[str, Any]]:
        """Calculates shortest relationship path between two entities."""
        G = self.build_networkx_graph()
        src_str, tgt_str = str(source_id), str(target_id)

        if src_str not in G or tgt_str not in G:
            return []

        try:
            path_nodes = nx.shortest_path(G.to_undirected(), source=src_str, target=tgt_str)
            path_info = []
            for node_id in path_nodes:
                path_info.append({"id": node_id, **G.nodes[node_id]})
            return path_info
        except nx.NetworkXNoPath:
            return []

    def export_visualization_json(self) -> Dict[str, Any]:
        """Exports full graph topology formatted for D3/vis.js interactive visualization (<2s target)."""
        G = self.build_networkx_graph()
        nodes = [{"id": n, **G.nodes[n]} for n in G.nodes()]
        edges = [{"source": u, "target": v, **G.edges[u, v]} for u, v in G.edges()]
        return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes), "total_edges": len(edges)}
