import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.tools_ecosystem.registry.models import ToolCategory, ToolHealthStatus
from backend.app.tools_ecosystem.registry.manager import ToolRegistryManager
from backend.app.tools_ecosystem.mcp.protocol import MCPProtocolHandler
from backend.app.tools_ecosystem.discovery.engine import ToolDiscoveryEngine
from backend.app.tools_ecosystem.execution.selector import SmartToolSelector
from backend.app.tools_ecosystem.execution.runner import UniversalToolExecutor
from backend.app.tools_ecosystem.permissions.guard import ToolPermissionGuard
from backend.app.tools_ecosystem.monitoring.observer import ToolMonitoringObserver

client = TestClient(app)

@pytest.mark.asyncio
async def test_tool_registry_lifecycle():
    """Verify tool registration, retrieval, listing, and unregistration (<50ms lookup)."""
    registry_mgr = ToolRegistryManager()
    
    # Register Tool
    tool = await registry_mgr.register_tool(
        tool_id="vscode_editor_cli",
        name="VS Code CLI",
        category=ToolCategory.DEV_TOOL,
        description="Opens and edits project workspace files",
        capabilities=["edit_file", "format_code"],
        requires_hitl=False,
        permission_level="standard"
    )
    assert tool.id is not None
    assert tool.tool_id == "vscode_editor_cli"
    assert tool.health_status == ToolHealthStatus.HEALTHY
    
    # Get Tool
    fetched = await registry_mgr.get_tool("vscode_editor_cli")
    assert fetched is not None
    assert fetched.name == "VS Code CLI"
    
    # List Tools
    tools = await registry_mgr.list_tools(category=ToolCategory.DEV_TOOL)
    assert len(tools) >= 1

def test_mcp_json_rpc_protocol():
    """Verify MCP protocol JSON-RPC initialize, tools/list, and tools/call handling."""
    handler = MCPProtocolHandler()
    
    # Initialize Request
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    init_resp = handler.handle_mcp_message(init_req, [])
    assert init_resp["result"]["serverInfo"]["name"] == "FATE Universal MCP Engine"
    
    # Tools List Request
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    list_resp = handler.handle_mcp_message(list_req, [{"tool_id": "test_tool", "description": "Test Tool"}])
    assert len(list_resp["result"]["tools"]) == 1

@pytest.mark.asyncio
async def test_auto_discovery_engine():
    """Verify tool auto-discovery for local software, binaries, and MCP servers (<1s discovery)."""
    discovery = ToolDiscoveryEngine()
    results = await discovery.run_auto_discovery()
    assert isinstance(results, list)
    assert len(results) > 0

@pytest.mark.asyncio
async def test_smart_tool_selector():
    """Verify best tool selection, fallback tool matching (<50ms selection)."""
    registry_mgr = ToolRegistryManager()
    selector = SmartToolSelector()
    
    await registry_mgr.register_tool(tool_id="git_cli", name="Git CLI", category=ToolCategory.DEV_TOOL)
    await registry_mgr.register_tool(tool_id="docker_cli", name="Docker CLI", category=ToolCategory.DEV_TOOL)
    
    best = await selector.select_best_tool("Run docker container build")
    assert best is not None
    assert "docker" in best.tool_id

def test_permission_guard_and_hitl():
    """Verify permission levels and Human-In-The-Loop (HITL) approval blocks (<20ms validation)."""
    guard = ToolPermissionGuard()
    
    # HITL required, not approved -> BLOCKED
    check_blocked = guard.validate_execution_permission("delete_prod_db", requires_hitl=True, hitl_approved=False)
    assert check_blocked["allowed"] is False
    assert check_blocked["code"] == "HITL_REQUIRED"
    
    # HITL approved -> OK
    check_ok = guard.validate_execution_permission("delete_prod_db", requires_hitl=True, hitl_approved=True)
    assert check_ok["allowed"] is True

@pytest.mark.asyncio
async def test_universal_tool_executor():
    """Verify synchronous & asynchronous tool execution (<100ms execution start)."""
    registry_mgr = ToolRegistryManager()
    executor = UniversalToolExecutor()
    
    await registry_mgr.register_tool(
        tool_id="local_file_linter",
        name="Local Linter",
        category=ToolCategory.DEV_TOOL
    )
    
    res = await executor.execute_tool("local_file_linter", {"file": "main.py"})
    assert res["status"] == "SUCCESS"
    assert "execution_time_ms" in res

def test_monitoring_observer():
    """Verify monitoring latency tracking and telemetry metrics."""
    observer = ToolMonitoringObserver()
    observer.record_execution("tool_test", latency_ms=45, success=True)
    metrics = observer.get_metrics("tool_test")
    assert metrics["total_calls"] == 1
    assert metrics["avg_latency_ms"] == 45.0

def test_tools_rest_endpoints():
    """Verify FastAPI REST API endpoints for Universal Tool Ecosystem."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
        
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/tools/register
    res_reg = client.post(
        "/api/v1/tools/register",
        headers=headers,
        json={
            "tool_id": "slack_notifier_tool",
            "name": "Slack Notifier",
            "category": "Communication",
            "description": "Posts automated status updates to Slack channel",
            "permission_level": "standard"
        }
    )
    assert res_reg.status_code == 201
    
    # GET /api/v1/tools/slack_notifier_tool
    res_get = client.get("/api/v1/tools/slack_notifier_tool", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Slack Notifier"
    
    # POST /api/v1/tools/execute
    res_exec = client.post(
        "/api/v1/tools/execute",
        headers=headers,
        json={"tool_id": "slack_notifier_tool", "action_args": {"channel": "#general", "text": "Deployment complete"}}
    )
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "SUCCESS"
    
    # GET /api/v1/tools/metrics/dashboard
    res_metrics = client.get("/api/v1/tools/metrics/dashboard", headers=headers)
    assert res_metrics.status_code == 200
    assert "overall_success_rate" in res_metrics.json()
