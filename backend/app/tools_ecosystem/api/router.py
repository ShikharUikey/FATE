from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.tools_ecosystem.registry.models import ToolCategory, ToolRecord
from backend.app.tools_ecosystem.registry.manager import ToolRegistryManager
from backend.app.tools_ecosystem.discovery.engine import ToolDiscoveryEngine
from backend.app.tools_ecosystem.execution.runner import UniversalToolExecutor
from backend.app.tools_ecosystem.execution.selector import SmartToolSelector
from backend.app.tools_ecosystem.monitoring.observer import ToolMonitoringObserver
from backend.app.tools_ecosystem.mcp.protocol import MCPProtocolHandler

router = APIRouter(
    prefix="/api/v1/tools",
    tags=["Universal Tool Ecosystem"]
)

# Managers Singletons
registry_mgr = ToolRegistryManager()
discovery_engine = ToolDiscoveryEngine()
executor = UniversalToolExecutor()
selector = SmartToolSelector()
observer = ToolMonitoringObserver()
mcp_handler = MCPProtocolHandler()

class RegisterToolRequest(BaseModel):
    tool_id: str
    name: str
    category: ToolCategory
    description: Optional[str] = ""
    provider: Optional[str] = "local"
    version: Optional[str] = "1.0.0"
    capabilities: Optional[List[str]] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    requires_hitl: Optional[bool] = False
    permission_level: Optional[str] = "standard"

class ExecuteToolRequest(BaseModel):
    tool_id: str
    action_args: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = "system"
    hitl_approved: Optional[bool] = False

@router.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def register_tool(payload: RegisterToolRequest):
    """Registers a new tool or updates existing tool definition."""
    return await registry_mgr.register_tool(
        tool_id=payload.tool_id,
        name=payload.name,
        category=payload.category,
        description=payload.description or "",
        provider=payload.provider or "local",
        version=payload.version or "1.0.0",
        capabilities=payload.capabilities,
        input_schema=payload.input_schema,
        output_schema=payload.output_schema,
        requires_hitl=payload.requires_hitl or False,
        permission_level=payload.permission_level or "standard"
    )

@router.get("", dependencies=[Depends(verify_session_token)])
async def list_tools(
    category: Optional[ToolCategory] = Query(None),
    provider: Optional[str] = Query(None)
):
    """Lists registered tools."""
    return await registry_mgr.list_tools(category=category, provider=provider)

@router.get("/{tool_id}", dependencies=[Depends(verify_session_token)])
async def get_tool(tool_id: str):
    """Retrieves tool record by string tool_id (<50ms target)."""
    tool = await registry_mgr.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.delete("/{tool_id}", dependencies=[Depends(verify_session_token)])
async def unregister_tool(tool_id: str):
    """Unregisters a tool."""
    success = await registry_mgr.unregister_tool(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"status": "SUCCESS", "message": f"Tool [{tool_id}] unregistered."}

@router.post("/discover", dependencies=[Depends(verify_session_token)])
async def run_discovery():
    """Triggers auto-discovery for local apps, binaries, and MCP servers (<1s target)."""
    return await discovery_engine.run_auto_discovery()

@router.post("/execute", dependencies=[Depends(verify_session_token)])
async def execute_tool(payload: ExecuteToolRequest):
    """Executes a target tool synchronously or asynchronously (<100ms start target)."""
    return await executor.execute_tool(
        tool_id=payload.tool_id,
        action_args=payload.action_args or {},
        user_id=payload.user_id or "system",
        hitl_approved=payload.hitl_approved or False
    )

@router.get("/metrics/dashboard", dependencies=[Depends(verify_session_token)])
async def get_dashboard_metrics():
    """Returns telemetry metrics for tool usage dashboard."""
    return observer.get_metrics()

@router.post("/mcp", dependencies=[Depends(verify_session_token)])
async def handle_mcp_rpc(payload: Dict[str, Any]):
    """Handles Model Context Protocol (MCP) JSON-RPC requests."""
    registered = await registry_mgr.list_tools()
    reg_dicts = [t.dict() for t in registered]
    return mcp_handler.handle_mcp_message(payload, reg_dicts)
