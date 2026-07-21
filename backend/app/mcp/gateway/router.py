import time
import asyncio
from typing import Dict, Any, Optional
from backend.app.mcp.registry.manager import MCPToolRegistryManager
from backend.app.mcp.permissions.engine import MCPPermissionEngine
from backend.app.mcp.sandbox.runner import MCPSandboxRunner

class MCPGateway:
    """MCP Central Gateway receiving requests, validating permissions, routing actions & retrying operations (<50ms response routing)."""

    def __init__(self):
        self.registry_mgr = MCPToolRegistryManager()
        self.perm_engine = MCPPermissionEngine()
        self.sandbox_runner = MCPSandboxRunner()

    async def route_request(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        user_role: str = "operator",
        hitl_approved: bool = False,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """Routes, validates auth/permissions, and executes a tool with automatic retries."""
        start_time = time.time()
        tool = await self.registry_mgr.get_tool(tool_id)

        if not tool:
            return {
                "status": "ERROR",
                "code": 404,
                "error": f"MCP Tool [{tool_id}] not found in registry.",
                "routing_latency_ms": int((time.time() - start_time) * 1000)
            }

        if not tool.is_enabled:
            return {
                "status": "ERROR",
                "code": 403,
                "error": f"MCP Tool [{tool_id}] is disabled.",
                "routing_latency_ms": int((time.time() - start_time) * 1000)
            }

        # Validate Permissions
        perm_result = self.perm_engine.evaluate_tool_permission(
            tool_id=tool.tool_id,
            risk_level=tool.risk_level,
            requires_hitl=tool.requires_hitl,
            hitl_approved=hitl_approved,
            user_role=user_role
        )

        if not perm_result["allowed"]:
            return {
                "status": "BLOCKED",
                "code": 401,
                "error": perm_result["reason"],
                "hitl_required": perm_result.get("hitl_required", False),
                "routing_latency_ms": int((time.time() - start_time) * 1000)
            }

        # Route execution with retries
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                result = await self.sandbox_runner.execute_in_sandbox(
                    tool=tool,
                    arguments=arguments
                )
                routing_ms = int((time.time() - start_time) * 1000)
                return {
                    "status": "SUCCESS",
                    "code": 200,
                    "tool_id": tool.tool_id,
                    "attempts": attempt + 1,
                    "result": result,
                    "routing_latency_ms": routing_ms
                }
            except Exception as e:
                last_exception = e
                await asyncio.sleep(0.05 * (attempt + 1))  # Exponential backoff retry delay

        routing_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "FAILED",
            "code": 500,
            "error": f"Failed after {max_retries + 1} attempts: {str(last_exception)}",
            "routing_latency_ms": routing_ms
        }
