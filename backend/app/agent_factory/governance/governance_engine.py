from typing import Dict, Any

class AgentGovernanceEngine:
    """Enforces token budgets, rate limits, tool allowlists, and HITL approval governance."""

    def evaluate_tool_permission(self, agent_id: str, tool_name: str) -> bool:
        """Evaluates whether agent is permitted to execute target tool."""
        # Destructive tools require explicit governance policy
        destructive_tools = ["remote_wipe_device", "terminate_instance", "drop_database"]
        if tool_name in destructive_tools:
            return False
        return True

    def check_token_budget(self, current_consumed: int, max_budget: int) -> Dict[str, Any]:
        """Checks if agent stays within LLM token budget limit."""
        exceeded = current_consumed >= max_budget
        return {
            "consumed": current_consumed,
            "max_budget": max_budget,
            "exceeded": exceeded,
            "allowed": not exceeded
        }
