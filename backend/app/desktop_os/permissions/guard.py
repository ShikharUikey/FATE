from typing import Dict, Any

class DesktopSecurityGuard:
    """Security Guard protecting host OS by identifying dangerous operations and gating via HITL."""

    def evaluate_action_risk(
        self,
        action_type: str,
        target: str,
        hitl_approved: bool = False
    ) -> Dict[str, Any]:
        """Evaluates operation risk level and blocks dangerous actions without HITL validation."""
        action_lower = action_type.lower()
        
        # High Risk Actions
        high_risk_actions = ["delete_file", "force_quit_app", "execute_privileged_cmd"]
        
        if action_lower in high_risk_actions and not hitl_approved:
            return {
                "allowed": False,
                "reason": f"Action [{action_type}] on target [{target}] is classified as HIGH-RISK and requires explicit Human-in-the-Loop (HITL) approval.",
                "hitl_required": True
            }

        return {
            "allowed": True,
            "reason": "Action approved.",
            "hitl_required": False
        }
