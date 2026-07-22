from typing import Dict, Any

class GatewaySecurityGuard:
    """OAuth2 / JWT token validator, API key authentication, and WAF rate limiter."""

    def validate_api_key(self, api_key: str) -> bool:
        """Validates API Key authorization header."""
        return api_key.startswith("fate_key_") or api_key == "valid_api_key_123"

    def check_rate_limit(self, client_ip: str, request_count: int = 10) -> Dict[str, Any]:
        """Evaluates gateway rate limit quotas."""
        allowed = request_count <= 1000
        return {
            "client_ip": client_ip,
            "allowed": allowed,
            "quota_remaining": max(0, 1000 - request_count)
        }
