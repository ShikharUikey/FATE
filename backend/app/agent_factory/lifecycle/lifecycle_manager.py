import time
from typing import Dict, Any, Optional
from backend.app.agent_factory.registry.agent_registry import AgentRegistryManager

class AgentLifecycleManager:
    """Manages AI Agent state machine (CREATE -> TEST -> DEPLOY -> PAUSE -> RETIRE) and rollbacks (<10s recovery target)."""

    def __init__(self, registry: AgentRegistryManager):
        self.registry = registry

    async def transition_state(self, agent_id: str, new_state: str) -> Dict[str, Any]:
        """Transitions agent lifecycle state."""
        agent = await self.registry.get_agent(agent_id)
        if not agent:
            return {"status": "FAILED", "error": f"Agent [{agent_id}] not found."}

        previous_state = agent.get("lifecycle_state", "CREATED")
        agent["lifecycle_state"] = new_state.upper()
        agent["updated_at"] = time.time()

        return {
            "status": "TRANSITIONED",
            "agent_id": agent_id,
            "previous_state": previous_state,
            "current_state": new_state.upper()
        }

    async def rollback_agent_version(self, agent_id: str, target_version: str) -> Dict[str, Any]:
        """Rolls back agent version configuration (<10s recovery target)."""
        start_time = time.time()
        agent = await self.registry.get_agent(agent_id)
        if not agent:
            return {"status": "FAILED", "error": f"Agent [{agent_id}] not found."}

        agent["version"] = target_version
        recovery_duration_s = round(time.time() - start_time, 2)

        return {
            "status": "ROLLED_BACK",
            "agent_id": agent_id,
            "target_version": target_version,
            "recovery_time_seconds": recovery_duration_s
        }
