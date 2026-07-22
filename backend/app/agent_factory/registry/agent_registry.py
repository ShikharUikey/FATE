import time
from typing import Dict, Any, List, Optional

class AgentRegistryManager:
    """Agent Registry database maintaining agent profiles, capabilities, versioning, and health scores."""

    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {
            "agent_coding_master": {
                "agent_id": "agent_coding_master",
                "name": "JARVIS Senior Engineer Agent",
                "owner": "Siddharth Uikey",
                "version": "1.4.0",
                "lifecycle_state": "DEPLOYED",
                "health_score_percent": 99.5,
                "capabilities": ["code_generation", "refactoring", "testing"],
                "tools": ["terminal_executor", "git_connector"],
                "token_budget": 1000000,
                "updated_at": time.time()
            }
        }

    async def register_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a new AI agent in the factory registry."""
        agent_id = agent_config["agent_id"]
        agent_config["health_score_percent"] = 100.0
        agent_config["updated_at"] = time.time()
        self._registry[agent_id] = agent_config
        return agent_config

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Queries agent registry profile by agent_id."""
        return self._registry.get(agent_id)

    async def list_registered_agents(self) -> List[Dict[str, Any]]:
        """Lists registered AI agents in ecosystem."""
        return list(self._registry.values())
