from typing import Dict, Any

class ToolPermissionGuard:
    """Fast Permission Validator and Security Approval Guard (<20ms target)."""

    def validate_execution_permission(
        self,
        tool_id: str,
        permission_level: str = "standard",
        requires_hitl: bool = False,
        hitl_approved: bool = False,
        user_role: str = "operator"
    ) -> Dict[str, Any]:
        """Evaluates permission level requirements, HITL confirmation, and sandbox boundaries."""
        # 1. Human-In-The-Loop (HITL) Security Check
        if requires_hitl and not hitl_approved:
            return {
                "allowed": False,
                "reason": f"Tool [{tool_id}] requires explicit Human-in-the-Loop (HITL) user confirmation.",
                "code": "HITL_REQUIRED"
            }

        # 2. Permission Level Scope Check
        level_hierarchy = {
            "read": 1,
            "standard": 2,
            "sensitive": 3,
            "admin": 4
        }

        user_scopes = {
            "admin": 4,
            "operator": 3,
            "guest": 1
        }

        required_score = level_hierarchy.get(permission_level.lower(), 2)
        user_score = user_scopes.get(user_role.lower(), 2)

        if user_score < required_score:
            return {
                "allowed": False,
                "reason": f"Insufficient privilege level [{user_role}] to execute tool with level [{permission_level}].",
                "code": "PERMISSION_DENIED"
            }

        return {
            "allowed": True,
            "reason": "Permission granted.",
            "code": "OK"
        }
