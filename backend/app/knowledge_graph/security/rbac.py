from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class SecurityManager:
    """Role-Based Access Control (RBAC) and Entity-Level Authorization Manager."""

    def check_permission(self, user_role: str, action: str) -> bool:
        """Verifies role permissions for graph actions (read, write, delete, admin)."""
        role_map = {
            "admin": ["read", "write", "delete", "admin"],
            "analyst": ["read", "write"],
            "viewer": ["read"]
        }
        allowed = role_map.get(user_role.lower(), ["read"])
        return action.lower() in allowed

    def evaluate_entity_acl(self, owner_id: str, requester_id: str, action: str) -> bool:
        """Evaluates entity-level ACLs."""
        if requester_id == "system" or requester_id == owner_id:
            return True
        if action == "read":
            return True
        return False

    def log_audit_event(self, user_id: str, action: str, target_id: UUID) -> Dict[str, Any]:
        """Generates audit log entries for graph security compliance."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "target_id": str(target_id),
            "status": "ALLOWED"
        }
