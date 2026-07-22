import time
from typing import Dict, Any, List

class DigitalTwinPlatform:
    """Virtual digital twin models representing Users, Infrastructure, Agents & Cloud Clusters (<1s target)."""

    def __init__(self):
        self._twins: Dict[str, Dict[str, Any]] = {
            "twin_cluster_aws_prod": {
                "twin_id": "twin_cluster_aws_prod",
                "entity_name": "AWS Production Cluster",
                "entity_type": "Infrastructure",
                "virtual_status": "HEALTHY",
                "active_nodes": 6,
                "cpu_utilization_percent": 42.5,
                "memory_utilization_percent": 58.0
            }
        }

    def query_twin_state(self, twin_id: str) -> Dict[str, Any]:
        """Queries virtual twin state representation (<1s query target)."""
        start_time = time.time()
        twin = self._twins.get(twin_id, {
            "twin_id": twin_id,
            "entity_name": f"Digital Twin {twin_id}",
            "entity_type": "Virtual Model",
            "virtual_status": "ONLINE"
        })
        twin["query_latency_ms"] = round((time.time() - start_time) * 1000, 2)
        return twin
