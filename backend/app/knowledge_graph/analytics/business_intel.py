import networkx as nx
from typing import Dict, Any, List
from backend.app.knowledge_graph.graph_engine.traversal import GraphTraversalEngine

class BusinessIntelligenceEngine:
    """Computes Knowledge Graph metrics, project bottlenecks, and collaboration density (<1s target)."""

    def __init__(self):
        self.traversal = GraphTraversalEngine()

    def compute_graph_metrics(self) -> Dict[str, Any]:
        """Calculates global network metrics (density, node degree centrality, clustering)."""
        G = self.traversal.build_networkx_graph()
        if len(G) == 0:
            return {"nodes": 0, "edges": 0, "density": 0.0, "top_central_nodes": []}

        density = nx.density(G)
        degree_centrality = nx.degree_centrality(G)
        
        # Sort top central nodes
        sorted_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        top_nodes = [
            {"id": n_id, "name": G.nodes[n_id].get("name"), "centrality": score}
            for n_id, score in sorted_nodes
        ]

        return {
            "nodes": len(G.nodes()),
            "edges": len(G.edges()),
            "density": float(density),
            "top_central_nodes": top_nodes
        }

    def discover_project_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identifies bottleneck nodes with high in-degree / out-degree centrality."""
        G = self.traversal.build_networkx_graph()
        bottlenecks = []
        if len(G) == 0:
            return bottlenecks

        in_degrees = dict(G.in_degree())
        for node_id, in_deg in in_degrees.items():
            if in_deg >= 3:  # High dependency bottleneck threshold
                bottlenecks.append({
                    "id": node_id,
                    "name": G.nodes[node_id].get("name"),
                    "entity_type": G.nodes[node_id].get("entity_type"),
                    "incoming_dependencies": in_deg,
                    "risk_level": "HIGH" if in_deg >= 5 else "MEDIUM"
                })
        return bottlenecks
