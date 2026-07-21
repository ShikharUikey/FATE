from typing import Dict, Any, Optional

class ToolAuthManager:
    """Authentication and Credential Vault Manager for tool integrations."""

    def __init__(self):
        self._vault: Dict[str, Dict[str, Any]] = {}

    def register_auth_token(self, tool_id: str, auth_type: str, token_value: str) -> bool:
        """Stores authentication token or API key for a tool."""
        self._vault[tool_id] = {
            "auth_type": auth_type.lower(),  # "api_key", "bearer", "oauth", "jwt"
            "token": token_value
        }
        return True

    def get_auth_headers(self, tool_id: str) -> Dict[str, str]:
        """Generates HTTP headers for authenticated tool requests."""
        cred = self._vault.get(tool_id)
        if not cred:
            return {}

        auth_type = cred.get("auth_type")
        token = cred.get("token")

        if auth_type in ["bearer", "jwt", "oauth"]:
            return {"Authorization": f"Bearer {token}"}
        elif auth_type == "api_key":
            return {"X-API-Key": token}
        
        return {}
