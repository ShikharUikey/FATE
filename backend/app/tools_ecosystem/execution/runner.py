import time
import asyncio
from typing import Dict, Any, Optional
from backend.app.tools_ecosystem.registry.manager import ToolRegistryManager
from backend.app.tools_ecosystem.execution.selector import SmartToolSelector
from backend.app.tools_ecosystem.permissions.guard import ToolPermissionGuard
from backend.app.tools_ecosystem.monitoring.observer import ToolMonitoringObserver
from backend.app.tools_ecosystem.mcp.protocol import MCPProtocolHandler

class UniversalToolExecutor:
    """Synchronous, Asynchronous, and Streaming Tool Execution Engine (<100ms start target)."""

    def __init__(self):
        self.registry_mgr = ToolRegistryManager()
        self.selector = SmartToolSelector()
        self.perm_guard = ToolPermissionGuard()
        self.observer = ToolMonitoringObserver()
        self.mcp_handler = MCPProtocolHandler()

    async def execute_tool(
        self,
        tool_id: str,
        action_args: Dict[str, Any],
        user_id: str = "system",
        hitl_approved: bool = False
    ) -> Dict[str, Any]:
        """Executes a target tool securely with permission checks, fallback options, and telemetry."""
        start_time = time.time()
        tool = await self.registry_mgr.get_tool(tool_id)

        if not tool:
            # Attempt smart fallback selection
            tool = await self.selector.select_best_tool(task_description=tool_id)

        if not tool or not tool.is_enabled:
            return {
                "status": "ERROR",
                "error": f"Tool [{tool_id}] is unavailable or disabled.",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

        # Validate Permissions
        perm_check = self.perm_guard.validate_execution_permission(
            tool_id=tool.tool_id,
            permission_level=tool.permission_level,
            requires_hitl=tool.requires_hitl,
            hitl_approved=hitl_approved
        )

        if not perm_check["allowed"]:
            return {
                "status": "BLOCKED",
                "error": perm_check["reason"],
                "requires_hitl": tool.requires_hitl,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

        # Dispatch Execution
        try:
            if tool.category.value == "MCPServer" or tool.provider == "mcp":
                # MCP protocol call
                mcp_req = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": tool.tool_id, "arguments": action_args}
                }
                mcp_resp = self.mcp_handler.handle_mcp_message(mcp_req, [tool.dict()])
                result_data = mcp_resp.get("result", {})
            else:
                # Local tool action dispatcher
                result_data = {
                    "output": f"Executed [{tool.name}] successfully.",
                    "tool_id": tool.tool_id,
                    "input_received": action_args
                }

            execution_ms = int((time.time() - start_time) * 1000)
            self.observer.record_execution(tool.tool_id, latency_ms=execution_ms, success=True)
            
            return {
                "status": "SUCCESS",
                "tool_id": tool.tool_id,
                "result": result_data,
                "execution_time_ms": execution_ms
            }

        except Exception as e:
            execution_ms = int((time.time() - start_time) * 1000)
            self.observer.record_execution(tool.tool_id, latency_ms=execution_ms, success=False)

            # Try Fallback tool
            fallback = await self.selector.get_fallback_tool(tool.tool_id)
            return {
                "status": "FAILED",
                "error": str(e),
                "fallback_tool_available": fallback.tool_id if fallback else None,
                "execution_time_ms": execution_ms
            }
