from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.agent_factory.builder.agent_builder import AgentBuilder
from backend.app.agent_factory.templates.template_catalog import AgentTemplateCatalog
from backend.app.agent_factory.registry.agent_registry import AgentRegistryManager
from backend.app.agent_factory.lifecycle.lifecycle_manager import AgentLifecycleManager
from backend.app.agent_factory.deployment.deployer import AgentDeployerPlatform
from backend.app.agent_factory.marketplace.agent_store import AgentMarketplaceStore
from backend.app.agent_factory.governance.governance_engine import AgentGovernanceEngine
from backend.app.agent_factory.analytics.agent_telemetry import AgentTelemetryEngine
from backend.app.agent_factory.security.agent_security import AgentSecurityGuard

router = APIRouter(
    prefix="/api/v1/agent-factory",
    tags=["AI Agent Factory & Lifecycle Management Platform"]
)

# Managers Singletons
builder = AgentBuilder()
templates = AgentTemplateCatalog()
registry = AgentRegistryManager()
lifecycle = AgentLifecycleManager(registry)
deployer = AgentDeployerPlatform()
marketplace = AgentMarketplaceStore()
governance = AgentGovernanceEngine()
telemetry = AgentTelemetryEngine()
security = AgentSecurityGuard()

class BuildAgentPromptPayload(BaseModel):
    prompt: str
    owner: Optional[str] = "Admin"

class StateTransitionPayload(BaseModel):
    agent_id: str
    new_state: str

class RollbackPayload(BaseModel):
    agent_id: str
    target_version: str

class DeployAgentPayload(BaseModel):
    agent_id: str
    target_environment: Optional[str] = "cloud_container"

class InstallMarketplacePayload(BaseModel):
    marketplace_id: str

@router.post("/build/prompt", dependencies=[Depends(verify_session_token)])
async def build_agent_from_prompt(payload: BuildAgentPromptPayload):
    """Generates complete AI Agent configuration from natural language prompt (<2s target)."""
    res = await builder.build_agent_from_prompt(payload.prompt, owner=payload.owner or "Admin")
    if res["status"] == "BUILD_SUCCESS":
        await registry.register_agent(res["agent_config"])
    return res

@router.get("/templates", dependencies=[Depends(verify_session_token)])
async def list_templates():
    """Lists reusable pre-built agent templates."""
    return templates.list_templates()

@router.get("/agents", dependencies=[Depends(verify_session_token)])
async def list_agents():
    """Lists registered AI agents."""
    return await registry.list_registered_agents()

@router.post("/lifecycle/state", dependencies=[Depends(verify_session_token)])
async def transition_state(payload: StateTransitionPayload):
    """Transitions agent lifecycle state (CREATED, DEPLOYED, PAUSED, RETIRED)."""
    return await lifecycle.transition_state(payload.agent_id, payload.new_state)

@router.post("/lifecycle/rollback", dependencies=[Depends(verify_session_token)])
async def rollback_agent(payload: RollbackPayload):
    """Rolls back agent configuration version (<10s target)."""
    return await lifecycle.rollback_agent_version(payload.agent_id, payload.target_version)

@router.post("/deploy", dependencies=[Depends(verify_session_token)])
async def deploy_agent(payload: DeployAgentPayload):
    """Deploys agent package to target environment (<30s target)."""
    return await deployer.deploy_agent_package(payload.agent_id, target_environment=payload.target_environment or "cloud_container")

@router.get("/marketplace", dependencies=[Depends(verify_session_token)])
async def list_marketplace(category: Optional[str] = None):
    """Lists enterprise agent marketplace offerings."""
    return marketplace.list_marketplace_agents(category=category)

@router.post("/marketplace/install", dependencies=[Depends(verify_session_token)])
async def install_marketplace_agent(payload: InstallMarketplacePayload):
    """Installs verified marketplace agent into local ecosystem."""
    return await marketplace.install_marketplace_agent(payload.marketplace_id)

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics():
    """Queries agent factory platform telemetry statistics."""
    return telemetry.get_agent_factory_analytics()
