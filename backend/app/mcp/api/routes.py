from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.mcp.registry.models import MCPToolCategory, MCPRiskLevel
from backend.app.mcp.registry.manager import MCPToolRegistryManager
from backend.app.mcp.gateway.router import MCPGateway
from backend.app.mcp.discovery.engine import MCPDiscoveryEngine
from backend.app.mcp.execution.chaining import MCPToolChainingEngine
from backend.app.mcp.plugins.marketplace import MCPPluginMarketplace
from backend.app.mcp.analytics.metrics import MCPAnalyticsObserver

router = APIRouter(
    prefix="/api/v1/mcp",
    tags=["MCP Universal Tool Ecosystem"]
)

# Managers Singletons
registry_mgr = MCPToolRegistryManager()
gateway = MCPGateway()
discovery_engine = MCPDiscoveryEngine()
chaining_engine = MCPToolChainingEngine()
marketplace = MCPPluginMarketplace()
analytics_obs = MCPAnalyticsObserver()

class RegisterMCPToolRequest(BaseModel):
    tool_id: str
    name: str
    category: MCPToolCategory
    description: Optional[str] = ""
    version: Optional[str] = "1.0.0"
    developer: Optional[str] = "JARVIS Core"
    risk_level: Optional[MCPRiskLevel] = MCPRiskLevel.LOW
    required_permissions: Optional[List[str]] = None
    auth_method: Optional[str] = "none"
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    requires_hitl: Optional[bool] = False

class ExecuteMCPToolRequest(BaseModel):
    tool_id: str
    arguments: Optional[Dict[str, Any]] = None
    user_role: Optional[str] = "operator"
    hitl_approved: Optional[bool] = False

class PipelineRequest(BaseModel):
    steps: List[Dict[str, Any]]
    initial_context: Optional[Dict[str, Any]] = None
    user_role: Optional[str] = "operator"
    hitl_approved: Optional[bool] = False

class InstallPluginRequest(BaseModel):
    plugin_id: str

@router.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def register_mcp_tool(payload: RegisterMCPToolRequest):
    """Registers or updates a tool entry in the MCP Tool Registry."""
    return await registry_mgr.register_tool(
        tool_id=payload.tool_id,
        name=payload.name,
        category=payload.category,
        description=payload.description or "",
        version=payload.version or "1.0.0",
        developer=payload.developer or "JARVIS Core",
        risk_level=payload.risk_level or MCPRiskLevel.LOW,
        required_permissions=payload.required_permissions,
        auth_method=payload.auth_method or "none",
        input_schema=payload.input_schema,
        output_schema=payload.output_schema,
        requires_hitl=payload.requires_hitl or False
    )

@router.get("/tools", dependencies=[Depends(verify_session_token)])
async def search_mcp_tools(
    query: Optional[str] = Query(None),
    category: Optional[MCPToolCategory] = Query(None),
    risk_level: Optional[MCPRiskLevel] = Query(None)
):
    """Searches and lists tools from the MCP Tool Registry."""
    return await registry_mgr.search_tools(query=query, category=category, risk_level=risk_level)

@router.get("/tools/{tool_id}", dependencies=[Depends(verify_session_token)])
async def get_mcp_tool(tool_id: str):
    """Retrieves tool definition by tool_id (<50ms lookup target)."""
    tool = await registry_mgr.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"MCP Tool [{tool_id}] not found")
    return tool

@router.delete("/tools/{tool_id}", dependencies=[Depends(verify_session_token)])
async def unregister_mcp_tool(tool_id: str):
    """Unregisters tool from MCP Registry."""
    success = await registry_mgr.unregister_tool(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"MCP Tool [{tool_id}] not found")
    return {"status": "SUCCESS", "message": f"Tool [{tool_id}] unregistered."}

@router.post("/discover", dependencies=[Depends(verify_session_token)])
async def run_mcp_discovery():
    """Triggers auto-discovery for local software, CLI binaries, cloud connections, and MCP servers (<100ms discovery)."""
    return await discovery_engine.discover_all_capabilities()

@router.post("/execute", dependencies=[Depends(verify_session_token)])
async def execute_mcp_tool(payload: ExecuteMCPToolRequest):
    """Routes tool execution through the MCP Gateway with retries and permissions checks (<50ms routing)."""
    return await gateway.route_request(
        tool_id=payload.tool_id,
        arguments=payload.arguments or {},
        user_role=payload.user_role or "operator",
        hitl_approved=payload.hitl_approved or False
    )

@router.post("/pipeline", dependencies=[Depends(verify_session_token)])
async def execute_mcp_pipeline(payload: PipelineRequest):
    """Executes a multi-tool pipeline chain (e.g. GitHub -> LLM -> Email -> Memory)."""
    return await chaining_engine.execute_pipeline(
        pipeline_steps=payload.steps,
        initial_context=payload.initial_context or {},
        user_role=payload.user_role or "operator",
        hitl_approved=payload.hitl_approved or False
    )

@router.get("/marketplace", dependencies=[Depends(verify_session_token)])
async def list_marketplace_plugins(query: Optional[str] = Query(None)):
    """Lists available plugins in the Plugin Marketplace store catalog."""
    return await marketplace.list_marketplace_plugins(query=query)

@router.post("/marketplace/install", dependencies=[Depends(verify_session_token)])
async def install_marketplace_plugin(payload: InstallPluginRequest):
    """Installs a verified plugin from the marketplace catalog."""
    plugin = await marketplace.install_plugin(payload.plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin [{payload.plugin_id}] not found in marketplace")
    return {"status": "SUCCESS", "installed_plugin": plugin}

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_mcp_analytics():
    """Returns telemetry dashboard metrics, token costs, and latency timeline."""
    return analytics_obs.get_observability_dashboard()
