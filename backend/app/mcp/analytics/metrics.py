from typing import Dict, Any, List, Optional
from datetime import datetime

class MCPAnalyticsObserver:
    """Telemetry observer recording latency, token usage, cost estimation, and execution metrics."""

    _tool_metrics: Dict[str, Dict[str, Any]] = {}
    _timeline_history: List[Dict[str, Any]] = []

    def record_execution(
        self,
        tool_id: str,
        latency_ms: int,
        success: bool = True,
        tokens_used: int = 0,
        estimated_cost: float = 0.0
    ):
        """Records telemetry data for an MCP tool execution event."""
        if tool_id not in self._tool_metrics:
            self._tool_metrics[tool_id] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency_ms": 0.0,
                "last_executed": None
            }

        m = self._tool_metrics[tool_id]
        m["total_calls"] += 1
        if success:
            m["successful_calls"] += 1
        else:
            m["failed_calls"] += 1

        m["total_tokens"] += tokens_used
        m["total_cost"] += estimated_cost
        
        # Calculate moving average latency
        prev_calls = m["total_calls"]
        m["avg_latency_ms"] = ((m["avg_latency_ms"] * (prev_calls - 1)) + latency_ms) / prev_calls
        m["last_executed"] = datetime.utcnow().isoformat()

        # Append to execution timeline
        self._timeline_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "tool_id": tool_id,
            "latency_ms": latency_ms,
            "success": success,
            "tokens_used": tokens_used,
            "cost": estimated_cost
        })

    def get_observability_dashboard(self) -> Dict[str, Any]:
        """Returns analytics summary for MCP Dashboard visualization."""
        total_calls = sum(m["total_calls"] for m in self._tool_metrics.values())
        total_failed = sum(m["failed_calls"] for m in self._tool_metrics.values())
        total_tokens = sum(m["total_tokens"] for m in self._tool_metrics.values())
        total_cost = sum(m["total_cost"] for m in self._tool_metrics.values())
        success_rate = 1.0 if total_calls == 0 else (total_calls - total_failed) / total_calls

        return {
            "summary": {
                "total_calls": total_calls,
                "success_rate": float(success_rate),
                "total_tokens_consumed": total_tokens,
                "estimated_api_cost_usd": float(round(total_cost, 4))
            },
            "per_tool_metrics": self._tool_metrics,
            "recent_timeline": self._timeline_history[-30:]
        }
