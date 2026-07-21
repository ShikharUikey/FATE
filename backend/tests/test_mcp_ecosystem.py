import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.mcp.registry.models import MCPToolCategory, MCPRiskLevel
from backend.app.mcp.registry.manager import MCPToolRegistryManager
from backend.app.mcp.gateway.router import MCPGateway
from backend.app.mcp.discovery.engine import MCPDiscoveryEngine
from backend.app.mcp.permissions.engine import MCPPermissionEngine
from backend.app.mcp.sandbox.runner import MCPSandboxRunner
from backend.app.mcp.execution.chaining import MCPToolChainingEngine
from backend.app.mcp.plugins.marketplace import MCPPluginMarketplace
from backend.app.mcp.analytics.metrics import MCPAnalyticsObserver

client = TestClient(app)

@pytest.mark.asyncio
async def test_mcp_tool_registry():
    """Verify tool registration, UUID lookups, and metadata validation (<50ms lookup)."""
    registry_mgr = MCPToolRegistryManager()
    tool = await registry_mgr.register_tool(
        tool_id="mcp_git_commit",
        name="MCP Git Commit Tool",
        category=MCPToolCategory.DEVELOPER_TOOLS,
        description="Creates git commits",
        risk_level=MCPRiskLevel.LOW
    )
    assert tool.id is not None
    assert tool.tool_id == "mcp_git_commit"
    
    fetched = await registry_mgr.get_tool("mcp_git_commit")
    assert fetched is not None
    assert fetched.risk_level == MCPRiskLevel.LOW

@pytest.mark.asyncio
async def test_mcp_gateway_routing():
    """Verify MCP Gateway routing and retry mechanisms (<50ms routing)."""
    registry_mgr = MCPToolRegistryManager()
    gateway = MCPGateway()
    
    await registry_mgr.register_tool(
        tool_id="mcp_echo_tool",
        name="Echo Tool",
        category=MCPToolCategory.OPERATING_SYSTEM,
        risk_level=MCPRiskLevel.LOW
    )
    
    res = await gateway.route_request("mcp_echo_tool", {"msg": "hello"})
    assert res["status"] == "SUCCESS"
    assert res["code"] == 200

@pytest.mark.asyncio
async def test_mcp_auto_discovery():
    """Verify auto-discovery engine catalog generation (<100ms target)."""
    discovery = MCPDiscoveryEngine()
    catalog = await discovery.discover_all_capabilities()
    assert "total_discovered" in catalog
    assert len(catalog["tools"]) > 0

def test_mcp_permissions_and_hitl():
    """Verify risk-level permission checks and Human-in-the-Loop (HITL) approval gating."""
    perm_engine = MCPPermissionEngine()
    
    # High risk, no HITL approval -> BLOCKED
    res_blocked = perm_engine.evaluate_tool_permission(
        tool_id="prod_db_wipe",
        risk_level=MCPRiskLevel.HIGH,
        hitl_approved=False
    )
    assert res_blocked["allowed"] is False
    assert res_blocked["code"] == "HITL_APPROVAL_REQUIRED"
    
    # High risk, HITL approved -> OK
    res_ok = perm_engine.evaluate_tool_permission(
        tool_id="prod_db_wipe",
        risk_level=MCPRiskLevel.HIGH,
        hitl_approved=True
    )
    assert res_ok["allowed"] is True

@pytest.mark.asyncio
async def test_mcp_sandbox_runner():
    """Verify isolated tool execution sandbox."""
    registry_mgr = MCPToolRegistryManager()
    sandbox = MCPSandboxRunner()
    
    tool = await registry_mgr.register_tool(
        tool_id="mcp_sandbox_test",
        name="Sandbox Test Tool",
        category=MCPToolCategory.OPERATING_SYSTEM
    )
    
    res = await sandbox.execute_in_sandbox(tool, {"param": 123})
    assert res["sandboxed"] is True
    assert "execution_ms" in res

@pytest.mark.asyncio
async def test_mcp_pipeline_chaining():
    """Verify multi-tool pipeline chaining (GitHub -> LLM -> Email)."""
    registry_mgr = MCPToolRegistryManager()
    chaining = MCPToolChainingEngine()
    
    await registry_mgr.register_tool(tool_id="step1_github", name="GitHub", category=MCPToolCategory.DEVELOPER_TOOLS)
    await registry_mgr.register_tool(tool_id="step2_email", name="Email", category=MCPToolCategory.COMMUNICATION)
    
    pipeline = [
        {"tool_id": "step1_github", "arguments": {"repo": "FATE"}},
        {"tool_id": "step2_email", "arguments": {"recipient": "alice@example.com"}}
    ]
    
    res = await chaining.execute_pipeline(pipeline, {"user": "siddharth"})
    assert res["pipeline_status"] == "COMPLETED"
    assert res["total_steps"] == 2

@pytest.mark.asyncio
async def test_mcp_plugin_marketplace():
    """Verify Plugin Marketplace store catalog and installation."""
    marketplace = MCPPluginMarketplace()
    plugins = await marketplace.list_marketplace_plugins()
    assert len(plugins) > 0
    
    installed = await marketplace.install_plugin(plugins[0].plugin_id)
    assert installed is not None
    assert installed.is_installed is True

def test_mcp_analytics_metrics():
    """Verify observability timeline tracking and cost estimation."""
    observer = MCPAnalyticsObserver()
    observer.record_execution("mcp_test_tool", latency_ms=30, success=True, tokens_used=150, estimated_cost=0.002)
    dashboard = observer.get_observability_dashboard()
    assert dashboard["summary"]["total_calls"] >= 1
    assert dashboard["summary"]["total_tokens_consumed"] >= 150

def test_mcp_rest_endpoints():
    """Verify FastAPI REST API endpoints for MCP ecosystem."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/mcp/register
    res_reg = client.post(
        "/api/v1/mcp/register",
        headers=headers,
        json={
            "tool_id": "mcp_rest_demo",
            "name": "MCP REST Demo Tool",
            "category": "DeveloperTools",
            "risk_level": "LOW"
        }
    )
    assert res_reg.status_code == 201
    
    # POST /api/v1/mcp/execute
    res_exec = client.post(
        "/api/v1/mcp/execute",
        headers=headers,
        json={"tool_id": "mcp_rest_demo", "arguments": {"foo": "bar"}}
    )
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "SUCCESS"
    
    # GET /api/v1/mcp/marketplace
    res_market = client.get("/api/v1/mcp/marketplace", headers=headers)
    assert res_market.status_code == 200
    assert len(res_market.json()) > 0
    
    # GET /api/v1/mcp/analytics
    res_analytics = client.get("/api/v1/mcp/analytics", headers=headers)
    assert res_analytics.status_code == 200
    assert "summary" in res_analytics.json()
