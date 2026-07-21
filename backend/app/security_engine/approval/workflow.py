import uuid
from typing import Dict, Any, List, Optional

class ApprovalWorkflowSystem:
    """Manages pending Human-in-the-Loop (HITL) validations (Voice, PIN, Password)."""

    def __init__(self):
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}

    def dispatch_approval_request(
        self,
        requester_id: str,
        action: str,
        risk_level: str = "HIGH"
    ) -> str:
        """Dispatches approval notification request return uuid lookup token."""
        req_token = str(uuid.uuid4())
        self._pending_approvals[req_token] = {
            "requester_id": requester_id,
            "action": action,
            "risk_level": risk_level,
            "status": "PENDING"
        }
        return req_token

    def approve_with_confirmation(self, req_token: str, approval_method: str = "voice") -> bool:
        """Approves a request, changing state to APPROVED."""
        req = self._pending_approvals.get(req_token)
        if not req:
            return False

        req["status"] = "APPROVED"
        req["method"] = approval_method.lower()
        return True

    def get_approval_status(self, req_token: str) -> Optional[str]:
        """Queries the current state status of approval."""
        req = self._pending_approvals.get(req_token)
        return req["status"] if req else None
