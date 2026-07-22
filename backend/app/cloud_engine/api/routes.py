from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.cloud_engine.providers.multi_cloud_manager import MultiCloudManager
from backend.app.cloud_engine.containers.docker_engine import DockerContainerEngine
from backend.app.cloud_engine.kubernetes.k8s_manager import KubernetesClusterManager
from backend.app.cloud_engine.deployment.cicd_deployer import CICDDeployerEngine
from backend.app.cloud_engine.monitoring.observability import CloudObservabilityEngine
from backend.app.cloud_engine.storage.storage_dr import StorageDisasterRecoveryEngine
from backend.app.cloud_engine.databases.database_manager import DatabaseInfrastructureManager
from backend.app.cloud_engine.security.cloud_security import CloudSecurityManager
from backend.app.cloud_engine.analytics.cost_optimizer import AICostOptimizationEngine

router = APIRouter(
    prefix="/api/v1/cloud",
    tags=["Cloud Orchestration & Infrastructure Engine"]
)

# Managers Singletons
cloud_mgr = MultiCloudManager()
docker_engine = DockerContainerEngine()
k8s_mgr = KubernetesClusterManager()
cicd_deployer = CICDDeployerEngine()
observability = CloudObservabilityEngine()
storage_dr = StorageDisasterRecoveryEngine()
db_infra = DatabaseInfrastructureManager()
cloud_security = CloudSecurityManager()
cost_optimizer = AICostOptimizationEngine()

class ProvisionResourceRequest(BaseModel):
    provider: str
    resource_type: str
    name: str
    region: Optional[str] = "us-east-1"

class DeployContainerRequest(BaseModel):
    image: str
    container_name: str
    ports_mapping: Dict[str, str]
    env_vars: Dict[str, str]

class ScaleK8sRequest(BaseModel):
    deployment_name: str
    replica_count: int

class RollbackDeploymentRequest(BaseModel):
    deployment_name: str
    target_version: str

class BackupRequest(BaseModel):
    target_service: str

@router.post("/resources/provision", dependencies=[Depends(verify_session_token)])
async def provision_resource(payload: ProvisionResourceRequest):
    """Provisions a new cloud infrastructure resource (<60s target)."""
    return await cloud_mgr.provision_resource(
        provider=payload.provider,
        resource_type=payload.resource_type,
        name=payload.name,
        region=payload.region or "us-east-1"
    )

@router.get("/resources", dependencies=[Depends(verify_session_token)])
async def list_resources(provider: Optional[str] = None):
    """Lists active multi-cloud infrastructure resources."""
    return await cloud_mgr.list_active_resources(provider_filter=provider)

@router.post("/containers/deploy", dependencies=[Depends(verify_session_token)])
async def deploy_container(payload: DeployContainerRequest):
    """Deploys container instance (<30s target)."""
    return await docker_engine.deploy_container(
        image=payload.image,
        container_name=payload.container_name,
        ports_mapping=payload.ports_mapping,
        env_vars=payload.env_vars
    )

@router.post("/kubernetes/scale", dependencies=[Depends(verify_session_token)])
async def scale_k8s_deployment(payload: ScaleK8sRequest):
    """Scales Kubernetes deployment replicas."""
    return await k8s_mgr.scale_deployment(payload.deployment_name, payload.replica_count)

@router.post("/deployment/rollback", dependencies=[Depends(verify_session_token)])
async def rollback_deployment(payload: RollbackDeploymentRequest):
    """Executes automated deployment rollback (<30s target)."""
    return await cicd_deployer.rollback_deployment(payload.deployment_name, payload.target_version)

@router.get("/monitoring/metrics", dependencies=[Depends(verify_session_token)])
async def get_metrics():
    """Queries cluster CPU, Memory, Network I/O, and SLA status."""
    return observability.get_cluster_metrics_snapshot()

@router.post("/storage/backup", dependencies=[Depends(verify_session_token)])
async def create_backup(payload: BackupRequest):
    """Creates automated backup snapshot."""
    return await storage_dr.create_automated_backup(payload.target_service)

@router.get("/analytics/cost", dependencies=[Depends(verify_session_token)])
async def get_cost_analytics():
    """Queries cloud cost analysis breakdown & recommendations."""
    return cost_optimizer.analyze_cloud_costs()
