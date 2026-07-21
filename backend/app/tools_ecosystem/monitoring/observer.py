from typing import Dict, Any, List, Optional
from datetime import datetime

class ToolMonitoringObserver:
    """Monitoring, Latency, and Telemetry Observer for Universal Tools."""

    _metrics: Dict[str, Dict[str, Any]] = {}
    _execution_history: List[Dict[str, Any]] = []

    def record_execution(self, tool_id: str, latency_ms: int, success: bool = True):
        """Records telemetry data for a tool execution."""
        if tool_id not in self._metrics:
            self._metrics[tool_id] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "avg_latency_ms": 0.0,
                "last_executed_at": None
            }

        data = self._metrics[tool_id]
        data["total_calls"] += 1
        if success:
            data["successful_calls"] += 1
        else:
            data["failed_calls"] += 1

        # Update rolling average latency
        prev_total = data["total_calls"]
        data["avg_latency_ms"] = ((data["avg_latency_ms"] * (prev_total - 1)) + latency_ms) / prev_total
        data["last_executed_at"] = datetime.utcnow().isoformat()

        # Log to execution history buffer
        self._execution_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "tool_id": tool_id,
            "latency_ms": latency_ms,
            "success": success
        })

    def get_metrics(self, tool_id: Optional[str] = None) -> Dict[str, Any]:
        """Returns execution telemetry and dashboard health statistics."""
        if tool_id:
            return self._metrics.get(tool_id, {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "avg_latency_ms": 0.0
            })

        total_system_calls = sum(m["total_calls"] for m in self._metrics.values())
        total_failures = sum(m["failed_calls"] for m in self._metrics.values())
        overall_success_rate = 1.0 if total_system_calls == 0 else ((total_system_calls - total_failures) / total_system_calls)

        return {
            "total_system_calls": total_system_calls,
            "overall_success_rate": float(overall_success_rate),
            "tool_metrics": self._metrics,
            "recent_executions": self._execution_history[-20:]
        }
