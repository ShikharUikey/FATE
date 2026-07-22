from typing import Dict, Any

class AnalyticsSecurityGuard:
    """Enforces RBAC dashboard access permissions and data masking."""

    def evaluate_dashboard_access(self, user_role: str, dashboard_name: str) -> bool:
        """Evaluates user role permissions for accessing sensitive dashboards."""
        if user_role in ["executive", "admin", "ciso"]:
            return True
        if user_role == "developer" and dashboard_name in ["operations", "agent_performance"]:
            return True
        return False

    def mask_sensitive_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Masks sensitive token credentials and user emails for analytics display."""
        masked = dict(payload)
        for key in ["email", "phone", "token", "secret"]:
            if key in masked:
                masked[key] = "***MASKED***"
        return masked
