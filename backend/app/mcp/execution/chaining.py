import time
from typing import List, Dict, Any
from backend.app.mcp.gateway.router import MCPGateway

class MCPToolChainingEngine:
    """Orchestrates multi-tool execution pipelines (e.g. GitHub -> LLM -> Email -> Memory -> Knowledge Graph)."""

    def __init__(self):
        self.gateway = MCPGateway()

    async def execute_pipeline(
        self,
        pipeline_steps: List[Dict[str, Any]],
        initial_context: Dict[str, Any],
        user_role: str = "operator",
        hitl_approved: bool = False
    ) -> Dict[str, Any]:
        """Executes a sequential sequence of tools passing step results to downstream stages."""
        pipeline_start = time.time()
        step_results = []
        current_context = dict(initial_context)

        for idx, step in enumerate(pipeline_steps):
            tool_id = step.get("tool_id")
            step_args = step.get("arguments", {})
            # Merge current context into step arguments
            step_args.update({"pipeline_context": current_context})

            res = await self.gateway.route_request(
                tool_id=tool_id,
                arguments=step_args,
                user_role=user_role,
                hitl_approved=hitl_approved
            )

            step_results.append({
                "step": idx + 1,
                "tool_id": tool_id,
                "status": res["status"],
                "output": res.get("result", {}),
                "error": res.get("error")
            })

            if res["status"] != "SUCCESS":
                return {
                    "pipeline_status": "ABORTED",
                    "failed_step": idx + 1,
                    "failed_tool_id": tool_id,
                    "error": res.get("error"),
                    "completed_steps": step_results,
                    "total_latency_ms": int((time.time() - pipeline_start) * 1000)
                }

            # Update context for next pipeline step
            current_context[f"step_{idx+1}_output"] = res.get("result", {})

        return {
            "pipeline_status": "COMPLETED",
            "total_steps": len(pipeline_steps),
            "step_results": step_results,
            "final_context": current_context,
            "total_latency_ms": int((time.time() - pipeline_start) * 1000)
        }
