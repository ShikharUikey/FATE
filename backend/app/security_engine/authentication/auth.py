import time
from typing import Dict, Any, Optional

class ZeroTrustAuthManager:
    """Adaptive Zero-Trust authentication and trusted session verification (<100ms target)."""

    def __init__(self):
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._trusted_devices: Dict[str, Dict[str, Any]] = {
            "device_owner_mac": {"device_id": "device_owner_mac", "trust_score": 0.98, "is_verified": True}
        }

    def authenticate_user(
        self,
        username: str,
        pin_code: str,
        device_id: str,
        mfa_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validates credentials, checks device trust, and registers active session."""
        # Simple simulated authentication check
        if username == "admin" and pin_code == "1234":
            device = self._trusted_devices.get(device_id, {"device_id": device_id, "trust_score": 0.5, "is_verified": False})
            
            # Session expiration 1 hour from now
            session_token = f"session_{username}_{int(time.time())}"
            self._active_sessions[session_token] = {
                "username": username,
                "device_id": device_id,
                "trust_score": device["trust_score"],
                "expires_at": time.time() + 3600,
                "last_active": time.time()
            }

            return {
                "authenticated": True,
                "session_token": session_token,
                "device_trusted": device["is_verified"],
                "trust_score": device["trust_score"]
            }

        return {"authenticated": False, "error": "Invalid credentials"}

    def verify_session(self, session_token: str, current_time: Optional[float] = None) -> bool:
        """Verifies session expiration and idle timeout threshold limits."""
        session = self._active_sessions.get(session_token)
        if not session:
            return False

        now = current_time or time.time()
        # 1. Expiration check
        if now > session["expires_at"]:
            self._active_sessions.pop(session_token, None)
            return False

        # 2. Idle timeout check (30 minutes = 1800s)
        if now - session["last_active"] > 1800:
            self._active_sessions.pop(session_token, None)
            return False

        # Update last active timestamp
        session["last_active"] = now
        return True

    def register_device(self, device_id: str, trust_score: float = 1.0) -> bool:
        """Registers a device as verified inside identity profile trust score vault."""
        self._trusted_devices[device_id] = {
            "device_id": device_id,
            "trust_score": trust_score,
            "is_verified": True
        }
        return True

    def revoke_session(self, session_token: str):
        """Immediately terminates session token."""
        self._active_sessions.pop(session_token, None)
