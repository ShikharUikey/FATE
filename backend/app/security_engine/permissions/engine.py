from typing import Dict, Any, Optional
from backend.app.security_engine.identity.manager import IdentityRegistryManager
from backend.app.security_engine.authorization.policies import ABACPolicyEvaluator

class ZeroTrustPermissionEngine:
    """Core Decoupled Zero Trust Permission Engine gating actions by evaluating WHO/AGENT/TOOL (<50ms checks)."""

    def __init__(self):
        self.identity_mgr = IdentityRegistryManager()
        self.abac_evaluator = ABACPolicyEvaluator()

    async def check_action_permission(
        self,
        requester_id: str,
        target_tool_id: str,
        required_privilege: str = "standard",
        context_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Decoupled validation mapping request identity, target tools, and ABAC context constraints."""
        identity = await self.identity_mgr.get_identity(requester_id)
        
        # 1. Identity Check
        if not identity or not identity.is_active:
            return {
                "allowed": False,
                "reason": f"Identity profile [{requester_id}] is unknown or inactive.",
                "code": "IDENTITY_NOT_FOUND"
            }

        # 2. Scope check: Does identity have role or permissions for this tool?
        if required_privilege.lower() not in identity.permissions and identity.role.value != "Owner":
            return {
                "allowed": False,
                "reason": f"Identity [{requester_id}] holds role [{identity.role.value}] with insufficient scope parameters.",
                "code": "SCOPE_CHECK_FAILED"
            }

        # 3. ABAC context attributes check
        if context_attributes:
            ip = context_attributes.get("ip", "127.0.0.1")
            sensitivity = context_attributes.get("sensitivity", "standard")
            hour = context_attributes.get("current_hour", 12)
            network = context_attributes.get("network_type", "secure")

            abac_passed = self.abac_evaluator.evaluate_policy_attributes(
                requester_ip=ip,
                resource_sensitivity=sensitivity,
                current_hour=hour,
                network_type=network
            )

            if not abac_passed:
                return {
                    "allowed": False,
                    "reason": "ABAC policy evaluation rejected context parameters.",
                    "code": "ABAC_POLICY_REJECT"
                }

        return {
            "allowed": True,
            "reason": "Permission granted.",
            "code": "OK"
        }
