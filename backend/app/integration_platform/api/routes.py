from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
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

router = APIRouter(
    prefix="/api/v1/integration-platform",
    tags=["Enterprise Integration Platform & API Gateway"]
)

# Managers Singletons
gateway = EnterpriseAPIGateway()
registry = ServiceRegistryEngine()
router_engine = RequestSmartRouter()
event_bus = EventBusPlatform()
connectors = EnterpriseConnectorsLibrary()
mesh = EnvoyServiceMesh()
governance = SchemaGovernanceEngine()
dev_portal = DeveloperPortalPlatform()
telemetry = IntegrationTelemetryEngine()
security = GatewaySecurityGuard()

class GatewayRequestPayload(BaseModel):
    protocol: str
    path: str
    method: Optional[str] = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None

class RegisterServicePayload(BaseModel):
    service_id: str
    service_name: str
    version: str
    dependencies: List[str]

class PublishEventPayload(BaseModel):
    topic: str
    event_name: str
    payload: Dict[str, Any]

class ExecuteConnectorPayload(BaseModel):
    connector_type: str
    action: str
    parameters: Dict[str, Any]

@router.post("/gateway/request", dependencies=[Depends(verify_session_token)])
async def handle_gateway_request(payload: GatewayRequestPayload):
    """Routes request through API Gateway (<20ms target)."""
    return await gateway.handle_request(
        protocol=payload.protocol,
        path=payload.path,
        method=payload.method or "GET",
        headers=payload.headers,
        body=payload.body
    )

@router.post("/registry/services", dependencies=[Depends(verify_session_token)])
async def register_service(payload: RegisterServicePayload):
    """Registers service in discovery map."""
    return await registry.register_service(
        service_id=payload.service_id,
        service_name=payload.service_name,
        version=payload.version,
        dependencies=payload.dependencies
    )

@router.get("/registry/services", dependencies=[Depends(verify_session_token)])
async def list_services():
    """Lists registered ecosystem services."""
    return await registry.list_services()

@router.post("/events/publish", dependencies=[Depends(verify_session_token)])
async def publish_event(payload: PublishEventPayload):
    """Publishes event message to Event Bus topic."""
    return await event_bus.publish_event(
        topic=payload.topic,
        event_name=payload.event_name,
        payload=payload.payload
    )

@router.post("/connectors/execute", dependencies=[Depends(verify_session_token)])
async def execute_connector(payload: ExecuteConnectorPayload):
    """Executes enterprise software connector (Salesforce, Jira, Slack, SAP)."""
    return await connectors.execute_connector_action(
        connector_type=payload.connector_type,
        action=payload.action,
        parameters=payload.parameters
    )

@router.get("/developer/openapi", dependencies=[Depends(verify_session_token)])
async def get_openapi_doc():
    """Queries OpenAPI v3 documentation specification."""
    return dev_portal.generate_openapi_spec()

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics():
    """Queries API Gateway telemetry metrics."""
    return telemetry.get_gateway_telemetry_summary()
