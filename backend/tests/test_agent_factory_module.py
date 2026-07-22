import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.agent_factory.builder.agent_builder import AgentBuilder
from backend.app.agent_factory.templates.template_catalog import AgentTemplateCatalog
from backend.app.agent_factory.registry.agent_registry import AgentRegistryManager
from backend.app.agent_factory.lifecycle.lifecycle_manager import AgentLifecycleManager
from backend.app.agent_factory.deployment.deployer import AgentDeployerPlatform
from backend.app.agent_factory.marketplace.agent_store import AgentMarketplaceStore
from backend.app.agent_factory.governance.governance_engine import AgentGovernanceEngine
from backend.app.agent_factory.analytics.agent_telemetry import AgentTelemetryEngine
from backend.app.agent_factory.security.agent_security import AgentSecurityGuard

client = TestClient(app)

@pytest.mark.asyncio
async def test_agent_builder_from_prompt():
    """Verify NL Agent configuration generation (<2s creation target)."""
    builder = AgentBuilder()
    res = await builder.build_agent_from_prompt("Monitor GitHub pull requests and post Slack digests")
    
    assert res["status"] == "BUILD_SUCCESS"
    assert res["build_time_seconds"] < 2.0
    assert "github_connector" in res["agent_config"]["tools"]

def test_agent_template_catalog():
    """Verify listing and retrieving agent templates."""
    catalog = AgentTemplateCatalog()
    templates = catalog.list_templates()
    assert len(templates) >= 3
    
    tpl = catalog.get_template("coding_agent")
    assert tpl["name"] == "Full-Stack Software Engineer"

@pytest.mark.asyncio
async def test_agent_registry():
    """Verify agent profile registration and listing."""
    reg = AgentRegistryManager()
    agent = await reg.get_agent("agent_coding_master")
    assert agent["version"] == "1.4.0"
    
    agents = await reg.list_registered_agents()
    assert len(agents) >= 1

@pytest.mark.asyncio
async def test_agent_lifecycle_manager():
    """Verify agent lifecycle state transitions and rollback recovery (<10s target)."""
    reg = AgentRegistryManager()
    lifecycle = AgentLifecycleManager(reg)
    
    # State transition
    trans = await lifecycle.transition_state("agent_coding_master", "PAUSED")
    assert trans["status"] == "TRANSITIONED"
    assert trans["current_state"] == "PAUSED"
    
    # Rollback version
    rollback = await lifecycle.rollback_agent_version("agent_coding_master", "1.3.9")
    assert rollback["status"] == "ROLLED_BACK"
    assert rollback["recovery_time_seconds"] < 10.0

@pytest.mark.asyncio
async def test_agent_deployer_platform():
    """Verify agent packaging & container deployment (<30s target)."""
    deployer = AgentDeployerPlatform()
    res = await deployer.deploy_agent_package("agent_coding_master", target_environment="kubernetes")
    
    assert res["status"] == "DEPLOYED"
    assert res["deploy_time_seconds"] < 30.0

@pytest.mark.asyncio
async def test_agent_marketplace():
    """Verify marketplace listing and 1-click installation."""
    store = AgentMarketplaceStore()
    items = store.list_marketplace_agents()
    assert len(items) >= 2
    
    install = await store.install_marketplace_agent("mp_devops_assistant")
    assert install["status"] == "INSTALLED"

def test_agent_governance_engine():
    """Verify tool allowlist evaluation and token budget checks."""
    gov = AgentGovernanceEngine()
    
    assert gov.evaluate_tool_permission("agent_01", "search_web") is True
    assert gov.evaluate_tool_permission("agent_01", "terminate_instance") is False
    
    budget = gov.check_token_budget(current_consumed=50000, max_budget=100000)
    assert budget["allowed"] is True

def test_agent_telemetry_and_security():
    """Verify factory telemetry statistics and sandbox isolation checks."""
    telemetry = AgentTelemetryEngine()
    stats = telemetry.get_agent_factory_analytics()
    assert stats["total_agents_count"] > 0
    
    sec = AgentSecurityGuard()
    sandbox = sec.validate_agent_sandbox("agent_01")
    assert sandbox["sandbox_active"] is True

def test_agent_factory_rest_endpoints():
    """Verify FastAPI REST API endpoints for AI Agent Factory."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/agent-factory/build/prompt
    res_bld = client.post(
        "/api/v1/agent-factory/build/prompt",
        headers=headers,
        json={"prompt": "Build an email summarizing agent", "owner": "Admin"}
    )
    assert res_bld.status_code == 200
    assert res_bld.json()["status"] == "BUILD_SUCCESS"
    
    # GET /api/v1/agent-factory/templates
    res_tpl = client.get("/api/v1/agent-factory/templates", headers=headers)
    assert res_tpl.status_code == 200
    assert len(res_tpl.json()) >= 3
    
    # GET /api/v1/agent-factory/agents
    res_ag = client.get("/api/v1/agent-factory/agents", headers=headers)
    assert res_ag.status_code == 200
    assert len(res_ag.json()) >= 1
    
    # GET /api/v1/agent-factory/analytics
    res_an = client.get("/api/v1/agent-factory/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "total_agents_count" in res_an.json()
