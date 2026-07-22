from typing import Dict, Any

class EvolutionGovernanceManager:
    """Approval gates, versioning, and self-modification safeguards (prevents uncontrolled self-modification)."""

    def validate_evolution_proposal(
        self,
        proposal_id: str,
        modification_type: str,
        auto_approved: bool = False
    ) -> Dict[str, Any]:
        """Enforces governance approval policy on self-improvement proposals."""
        requires_human_approval = modification_type.lower() in ["core_prompt", "permission_policy", "security_rule"]
        
        if requires_human_approval and not auto_approved:
            return {
                "status": "PENDING_APPROVAL",
                "proposal_id": proposal_id,
                "requires_human_approval": True,
                "message": f"Modification [{modification_type}] requires explicit Human-In-The-Loop approval."
            }

        return {
            "status": "APPROVED",
            "proposal_id": proposal_id,
            "requires_human_approval": False
        }
