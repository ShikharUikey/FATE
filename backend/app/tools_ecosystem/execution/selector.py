from typing import Optional, Dict, Any, List
from backend.app.tools_ecosystem.registry.manager import ToolRegistryManager
from backend.app.tools_ecosystem.registry.models import ToolRecord, ToolCategory, ToolHealthStatus

class SmartToolSelector:
    """Smart Tool Selection Engine (Best Tool, Fallback Tool, Fastest, Offline) (<50ms target)."""

    def __init__(self):
        self.registry_mgr = ToolRegistryManager()

    async def select_best_tool(
        self,
        task_description: str,
        category: Optional[ToolCategory] = None,
        require_offline: bool = False
    ) -> Optional[ToolRecord]:
        """Determines optimal tool for given task description and requirements."""
        tools = await self.registry_mgr.list_tools(category=category, enabled_only=True)
        if not tools:
            # Fallback to all tools if category empty
            tools = await self.registry_mgr.list_tools(enabled_only=True)

        if not tools:
            return None

        desc_lower = task_description.lower()

        # Score matching tools
        scored_tools = []
        for t in tools:
            score = 0.0
            if t.health_status != ToolHealthStatus.HEALTHY:
                score -= 10.0
            if require_offline and t.provider not in ["local", "local_cli", "macos_app", "mcp"]:
                continue

            name_words = [w for w in t.name.lower().split() if len(w) > 2]
            id_words = [w for w in t.tool_id.lower().split('_') if len(w) > 2]
            
            for w in name_words + id_words:
                if w in desc_lower:
                    score += 5.0

            for cap in t.capabilities:
                if cap.lower() in desc_lower:
                    score += 2.0
            scored_tools.append((score, t))

        if not scored_tools:
            return tools[0] if tools else None

        scored_tools.sort(key=lambda item: item[0], reverse=True)
        return scored_tools[0][1]

    async def get_fallback_tool(self, current_tool_id: str) -> Optional[ToolRecord]:
        """Provides healthy secondary fallback tool if primary tool fails."""
        primary = await self.registry_mgr.get_tool(current_tool_id)
        if not primary:
            return None

        # Look for alternative in same category
        alternatives = await self.registry_mgr.list_tools(category=primary.category, enabled_only=True)
        for alt in alternatives:
            if alt.tool_id != current_tool_id and alt.health_status == ToolHealthStatus.HEALTHY:
                return alt

        # Generic CLI fallback
        cli_alts = await self.registry_mgr.list_tools(category=ToolCategory.DEV_TOOL, enabled_only=True)
        for alt in cli_alts:
            if alt.tool_id != current_tool_id:
                return alt

        return None
