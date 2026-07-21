from typing import Dict, Any

class HumanApprovalWorkflowGate:
    """Gates sensitive workflow transitions pending human approval verification."""

    def __init__(self):
        self._gates: Dict[str, Dict[str, Any]] = {}

    def register_approval_gate(self, execution_id: str, node_id: str, action: str) -> bool:
        """Registers a pending approval checkpoint in active workflow run state."""
        key = f"{execution_id}_{node_id}"
        self._gates[key] = {
            "execution_id": execution_id,
            "node_id": node_id,
            "action": action,
            "status": "PENDING"
        }
        return True

    def submit_gate_approval(self, execution_id: str, node_id: str, approved: bool = True) -> bool:
        """Saves confirmation choice (APPROVED/DENIED)."""
        key = f"{execution_id}_{node_id}"
        if key in self._gates:
            self._gates[key]["status"] = "APPROVED" if approved else "DENIED"
            return True
        return False

    def is_gate_approved(self, execution_id: str, node_id: str) -> bool:
        """Checks if checkpoint has received confirmation to resume."""
        key = f"{execution_id}_{node_id}"
        gate = self._gates.get(key)
        return gate is not None and gate["status"] == "APPROVED"
