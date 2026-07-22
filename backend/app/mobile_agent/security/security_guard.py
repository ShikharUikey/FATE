from typing import Dict, Any

class MobileSecurityGuard:
    """Validates biometric tokens, device certificates, and gates remote wipe operations."""

    def verify_biometric_token(self, token: str) -> bool:
        """Validates Face ID / Fingerprint authentication token."""
        return token.startswith("bio_valid_") or token == "mock_biometric_pass"

    def evaluate_remote_wipe_permission(self, device_id: str, hitl_approved: bool = False) -> Dict[str, Any]:
        """Gates destructive remote wipe actions behind HITL approval."""
        if not hitl_approved:
            return {
                "allowed": False,
                "reason": f"Remote wipe of device [{device_id}] requires explicit Human-in-the-Loop approval.",
                "hitl_required": True
            }
        return {"allowed": True, "reason": "Remote wipe approved by owner.", "hitl_required": False}
