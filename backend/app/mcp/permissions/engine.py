from typing import Dict, Any, Optional
from backend.app.mcp.registry.models import MCPRiskLevel

class MCPPermissionEngine:
    """Evaluates risk levels (LOW, MEDIUM, HIGH, CRITICAL), HITL user approval, and permission scopes."""

    def evaluate_tool_permission(
        self,
        tool_id: str,
        risk_level: MCPRiskLevel = MCPRiskLevel.LOW,
        requires_hitl: bool = False,
        hitl_approved: bool = False,
        user_role: str = "operator"
    ) -> Dict[str, Any]:
        """Evaluates whether the requested action is permitted or requires HITL confirmation."""
        # 1. Critical and High Risk Tools enforce explicit Human-in-the-Loop (HITL) approval
        if (requires_hitl or risk_level in [MCPRiskLevel.HIGH, MCPRiskLevel.CRITICAL]) and not hitl_approved:
            return {
                "allowed": False,
                "reason": f"Tool [{tool_id}] has Risk Level [{risk_level.value}] and requires explicit Human-in-the-Loop (HITL) user authorization.",
                "hitl_required": True,
                "code": "HITL_APPROVAL_REQUIRED"
            }

        # 2. Role Scope Hierarchies
        role_privilege_map = {
            "admin": 4,
            "operator": 3,
            "guest": 1
        }

        risk_score_map = {
            MCPRiskLevel.LOW: 1,
            MCPRiskLevel.MEDIUM: 2,
            MCPRiskLevel.HIGH: 3,
            MCPRiskLevel.CRITICAL: 4
        }

        user_score = role_privilege_map.get(user_role.lower(), 2)
        required_score = risk_score_map.get(risk_level, 1)

        if user_score < required_score:
            return {
                "allowed": False,
                "reason": f"User role [{user_role}] does not hold privilege required for Risk Level [{risk_level.value}].",
                "hitl_required": False,
                "code": "INSUFFICIENT_ROLE_PRIVILEGE"
            }

        return {
            "allowed": True,
            "reason": "Permission granted.",
            "hitl_required": False,
            "code": "OK"
        }
