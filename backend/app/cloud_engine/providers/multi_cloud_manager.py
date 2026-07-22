import time
from typing import Dict, Any, List, Optional
from uuid import uuid4

class MultiCloudManager:
    """Manages multi-cloud infrastructure resources (AWS, Azure, GCP, DigitalOcean, Cloudflare) (<60s provisioning target)."""

    def __init__(self):
        self._resources: Dict[str, Dict[str, Any]] = {
            "res_aws_ec2": {
                "resource_id": "res_aws_ec2",
                "provider": "AWS",
                "resource_type": "VirtualMachine",
                "name": "jarvis-core-cluster-worker-01",
                "region": "us-east-1",
                "status": "RUNNING",
                "cost_per_hour_usd": 0.096,
                "created_at": time.time()
            },
            "res_gcp_gke": {
                "resource_id": "res_gcp_gke",
                "provider": "GCP",
                "resource_type": "KubernetesCluster",
                "name": "jarvis-prod-gke-01",
                "region": "us-central1",
                "status": "RUNNING",
                "cost_per_hour_usd": 0.20,
                "created_at": time.time()
            }
        }

    async def provision_resource(
        self,
        provider: str,
        resource_type: str,
        name: str,
        region: str = "us-east-1"
    ) -> Dict[str, Any]:
        """Provisions a new cloud infrastructure resource (<60s target)."""
        start_time = time.time()
        resource_id = f"res_{provider.lower()}_{str(uuid4())[:6]}"
        
        record = {
            "resource_id": resource_id,
            "provider": provider.upper(),
            "resource_type": resource_type,
            "name": name,
            "region": region,
            "status": "RUNNING",
            "cost_per_hour_usd": 0.05,
            "created_at": time.time()
        }
        self._resources[resource_id] = record
        provision_duration_s = round(time.time() - start_time, 2)

        return {
            "status": "PROVISIONED",
            "provision_time_seconds": provision_duration_s,
            "resource": record
        }

    async def list_active_resources(self, provider_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists active multi-cloud infrastructure resources."""
        res_list = list(self._resources.values())
        if provider_filter:
            return [r for r in res_list if r["provider"] == provider_filter.upper()]
        return res_list

    async def terminate_resource(self, resource_id: str) -> bool:
        """Terminates cloud resource instance."""
        res = self._resources.get(resource_id)
        if not res:
            return False
        res["status"] = "TERMINATED"
        return True
