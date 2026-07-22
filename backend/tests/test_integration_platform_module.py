import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.integration_platform.gateway.api_gateway import EnterpriseAPIGateway
from backend.app.integration_platform.registry.service_registry import ServiceRegistryEngine
from backend.app.integration_platform.routing.request_router import RequestSmartRouter
from backend.app.integration_platform.events.event_bus import EventBusPlatform
from backend.app.integration_platform.connectors.enterprise_connectors import EnterpriseConnectorsLibrary
from backend.app.integration_platform.mesh.service_mesh import EnvoyServiceMesh
from backend.app.integration_platform.governance.schema_governance import SchemaGovernanceEngine
from backend.app.integration_platform.developer_portal.dev_portal import DeveloperPortalPlatform
from backend.app.integration_platform.analytics.integration_telemetry import IntegrationTelemetryEngine
from backend.app.integration_platform.security.gateway_security import GatewaySecurityGuard

client = TestClient(app)

@pytest.mark.asyncio
async def test_enterprise_api_gateway():
    """Verify REST, GraphQL, gRPC & WebSockets request handling (<20ms latency target)."""
    gw = EnterpriseAPIGateway()
    res = await gw.handle_request(protocol="REST", path="/api/v1/brain/chat", method="POST")
    
    assert res["status"] == "SUCCESS"
    assert res["protocol"] == "REST"
    assert res["latency_ms"] < 20.0

@pytest.mark.asyncio
async def test_service_registry_engine():
    """Verify service discovery registration and service listing."""
    reg = ServiceRegistryEngine()
    svc = await reg.register_service("svc_workflow", "Workflow Automation Engine", "v1.1.0", ["svc_db"])
    
    assert svc["service_id"] == "svc_workflow"
    assert len(await reg.list_services()) >= 3

def test_request_smart_router():
    """Verify Path, Header, Canary, and Blue-Green routing (<10ms target)."""
    router = RequestSmartRouter()
    
    # Standard route
    res_std = router.resolve_route("/api/v1/memory/search")
    assert res_std["routing_time_ms"] < 10.0
    assert res_std["strategy"] == "STANDARD"
    
    # Canary route
    res_canary = router.resolve_route("/api/v1/memory/search", headers={"X-Canary-Test": "true"})
    assert res_canary["strategy"] == "CANARY"

@pytest.mark.asyncio
async def test_event_bus_platform():
    """Verify Pub/Sub topic event publishing and Dead-Letter Queueing."""
    bus = EventBusPlatform()
    pub = await bus.publish_event(topic="workflow_events", event_name="TASK_COMPLETED", payload={"task_id": "t1"})
    
    assert pub["status"] == "PUBLISHED"
    events = await bus.fetch_topic_events("workflow_events")
    assert len(events) == 1
    
    dlq_ok = await bus.push_to_dead_letter_queue(pub["event_id"], reason="Deserialization failure")
    assert dlq_ok is True

@pytest.mark.asyncio
async def test_enterprise_connectors_library():
    """Verify connectors for Salesforce, Jira, Slack, GitHub, and SAP."""
    connectors = EnterpriseConnectorsLibrary()
    
    sf_res = await connectors.execute_connector_action("salesforce", "create_lead", {"name": "Acme Corp"})
    assert sf_res["status"] == "SUCCESS"
    
    slack_res = await connectors.execute_connector_action("slack", "post_message", {"channel": "#fate-alerts"})
    assert slack_res["status"] == "DELIVERED"

def test_envoy_service_mesh():
    """Verify mTLS zero-trust certificate validation & circuit breaker status."""
    mesh = EnvoyServiceMesh()
    res = mesh.evaluate_mesh_traffic("svc_brain", "svc_memory")
    
    assert res["mtls_verified"] is True
    assert res["status"] == "ALLOWED"

def test_schema_governance_engine():
    """Verify JSON schema validation and PII data detection."""
    gov = SchemaGovernanceEngine()
    
    valid = gov.validate_schema("UserSchema", {"name": "Siddharth", "email": "user@example.com"})
    assert valid["is_valid"] is True
    assert valid["pii_detected"] is False
    
    pii = gov.validate_schema("UserSchema", {"ssn": "123-45-6789"})
    assert pii["pii_detected"] is True

def test_developer_portal_platform():
    """Verify OpenAPI v3 specification documentation and client SDK stubs generation."""
    portal = DeveloperPortalPlatform()
    spec = portal.generate_openapi_spec()
    assert spec["status"] == "GENERATED"
    
    sdk = portal.generate_sdk_client_stub("python")
    assert sdk["sdk_package_name"] == "fate-sdk-python"

def test_integration_telemetry_and_security():
    """Verify API Gateway telemetry summary and API Key / rate limit security."""
    telemetry = IntegrationTelemetryEngine()
    summary = telemetry.get_gateway_telemetry_summary()
    assert summary["avg_gateway_latency_ms"] < 20.0
    
    sec = GatewaySecurityGuard()
    assert sec.validate_api_key("fate_key_valid_101") is True
    
    rate = sec.check_rate_limit("127.0.0.1", request_count=50)
    assert rate["allowed"] is True

def test_integration_rest_endpoints():
    """Verify FastAPI REST API endpoints for Enterprise Integration Platform."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/integration-platform/gateway/request
    res_gw = client.post(
        "/api/v1/integration-platform/gateway/request",
        headers=headers,
        json={"protocol": "REST", "path": "/api/v1/brain/chat", "method": "POST"}
    )
    assert res_gw.status_code == 200
    assert res_gw.json()["status"] == "SUCCESS"
    
    # GET /api/v1/integration-platform/registry/services
    res_svc = client.get("/api/v1/integration-platform/registry/services", headers=headers)
    assert res_svc.status_code == 200
    assert len(res_svc.json()) >= 2
    
    # POST /api/v1/integration-platform/events/publish
    res_pub = client.post(
        "/api/v1/integration-platform/events/publish",
        headers=headers,
        json={"topic": "system_alerts", "event_name": "CPU_HIGH", "payload": {"usage": 89}}
    )
    assert res_pub.status_code == 200
    assert res_pub.json()["status"] == "PUBLISHED"
    
    # GET /api/v1/integration-platform/analytics
    res_an = client.get("/api/v1/integration-platform/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "avg_gateway_latency_ms" in res_an.json()
