import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.cloud_engine.providers.multi_cloud_manager import MultiCloudManager
from backend.app.cloud_engine.containers.docker_engine import DockerContainerEngine
from backend.app.cloud_engine.kubernetes.k8s_manager import KubernetesClusterManager
from backend.app.cloud_engine.deployment.cicd_deployer import CICDDeployerEngine
from backend.app.cloud_engine.monitoring.observability import CloudObservabilityEngine
from backend.app.cloud_engine.storage.storage_dr import StorageDisasterRecoveryEngine
from backend.app.cloud_engine.databases.database_manager import DatabaseInfrastructureManager
from backend.app.cloud_engine.security.cloud_security import CloudSecurityManager
from backend.app.cloud_engine.analytics.cost_optimizer import AICostOptimizationEngine

client = TestClient(app)

@pytest.mark.asyncio
async def test_multi_cloud_provisioning():
    """Verify resource provisioning across AWS, Azure, GCP (<60s target)."""
    mgr = MultiCloudManager()
    res = await mgr.provision_resource("AWS", "VirtualMachine", "web-node-01", "us-east-1")
    
    assert res["status"] == "PROVISIONED"
    assert res["provision_time_seconds"] < 60.0
    assert res["resource"]["provider"] == "AWS"

@pytest.mark.asyncio
async def test_docker_container_deployment():
    """Verify Docker container deployment & status (<30s target)."""
    docker = DockerContainerEngine()
    res = await docker.deploy_container(
        image="redis:alpine",
        container_name="cache-service",
        ports_mapping={"6379/tcp": "6379"},
        env_vars={"ALLOW_EMPTY_PASSWORD": "yes"}
    )
    assert res["status"] == "SUCCESS"
    assert res["deploy_time_seconds"] < 30.0
    assert len(await docker.list_running_containers()) == 1

@pytest.mark.asyncio
async def test_kubernetes_cluster_scaling():
    """Verify pod replicas scaling and Canary deployment rollout."""
    k8s = KubernetesClusterManager()
    scale_res = await k8s.scale_deployment("fate-core-api", 5)
    assert scale_res["status"] == "SCALED"
    assert scale_res["new_replicas"] == 5
    
    canary_res = await k8s.execute_canary_deployment("fate-core-api", "jarvis/fate-core:v1.5.0", traffic_weight_percent=20)
    assert canary_res["status"] == "CANARY_ROLLOUT_STARTED"

@pytest.mark.asyncio
async def test_cicd_pipeline_and_rollback():
    """Verify CI/CD pipeline triggers and automated deployment rollbacks (<30s target)."""
    cicd = CICDDeployerEngine()
    build = await cicd.trigger_pipeline_build("ShikharUikey/FATE", branch="main")
    assert build["status"] == "SUCCESS"
    
    rollback = await cicd.rollback_deployment("fate-core-api", target_version="v1.4.2")
    assert rollback["status"] == "ROLLED_BACK"
    assert rollback["rollback_time_seconds"] < 30.0

def test_observability_metrics():
    """Verify Prometheus & OpenTelemetry metric snapshots and incident alerts."""
    obs = CloudObservabilityEngine()
    snapshot = obs.get_cluster_metrics_snapshot()
    
    assert snapshot["cluster_health"] == "HEALTHY"
    assert snapshot["cpu_utilization_percent"] > 0
    
    alert = obs.raise_incident_alert("CRITICAL", "Database", "Replication lag exceeded threshold")
    assert alert["severity"] == "CRITICAL"

@pytest.mark.asyncio
async def test_storage_disaster_recovery():
    """Verify automated database backups and point-in-time recovery."""
    storage = StorageDisasterRecoveryEngine()
    backup_res = await storage.create_automated_backup("postgres-prod")
    assert backup_res["status"] == "SUCCESS"
    backup_id = backup_res["backup"]["backup_id"]
    
    restore_res = await storage.restore_from_point_in_time(backup_id)
    assert restore_res["status"] == "RESTORED"

@pytest.mark.asyncio
async def test_database_infrastructure():
    """Verify listing database instances and promotion failovers."""
    db = DatabaseInfrastructureManager()
    instances = await db.list_database_instances()
    assert len(instances) >= 2
    
    failover = await db.trigger_failover("fate_postgres_primary")
    assert failover["status"] == "FAILOVER_COMPLETED"

def test_cloud_security_iam():
    """Verify Cloud IAM role evaluation and compliance scanning."""
    sec = CloudSecurityManager()
    assert sec.evaluate_iam_policy("admin", "terminate_instance", "arn:aws:ec2:*") is True
    assert sec.evaluate_iam_policy("developer", "terminate_instance", "arn:aws:ec2:*") is False
    
    scan = sec.scan_cloud_compliance()
    assert scan["status"] == "COMPLIANT"

def test_cost_optimization_scaling():
    """Verify cloud cost analysis and predictive auto-scaling decisions (<10s target)."""
    opt = AICostOptimizationEngine()
    costs = opt.analyze_cloud_costs()
    assert costs["total_monthly_spend_usd"] > 0
    assert len(costs["recommendations"]) > 0
    
    scaling = opt.predict_autoscaling_demand(current_qps=250.0)
    assert scaling["decision_time_seconds"] < 10.0
    assert scaling["recommended_replicas"] == 5

def test_cloud_rest_endpoints():
    """Verify FastAPI REST API endpoints for Cloud Orchestration Engine."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/cloud/resources/provision
    res_prov = client.post(
        "/api/v1/cloud/resources/provision",
        headers=headers,
        json={"provider": "GCP", "resource_type": "KubernetesCluster", "name": "test-cluster"}
    )
    assert res_prov.status_code == 200
    assert res_prov.json()["status"] == "PROVISIONED"
    
    # GET /api/v1/cloud/resources
    res_list = client.get("/api/v1/cloud/resources", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 2
    
    # GET /api/v1/cloud/analytics/cost
    res_cost = client.get("/api/v1/cloud/analytics/cost", headers=headers)
    assert res_cost.status_code == 200
    assert "total_monthly_spend_usd" in res_cost.json()
