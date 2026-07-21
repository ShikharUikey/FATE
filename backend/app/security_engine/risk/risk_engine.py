from typing import Dict, Any

class RiskTelemetryEngine:
    """Calculates risk levels (LOW, MEDIUM, HIGH, CRITICAL) and isolates suspicious agent threats (<100ms target)."""

    def calculate_action_risk(
        self,
        requester_role: str,
        action: str,
        device_trust_score: float = 1.0,
        failures_count: int = 0
    ) -> Dict[str, Any]:
        """Runs security telemetry algorithm to compute operational risk metric."""
        score = 0.0

        # 1. Base action risk checks
        action_lower = action.lower()
        if any(kw in action_lower for kw in ["delete", "wipe", "format", "killall", "rm -rf"]):
            score += 0.7
        elif any(kw in action_lower for kw in ["write", "update", "modify"]):
            score += 0.3

        # 2. Device trust penalty
        if device_trust_score < 0.6:
            score += 0.4

        # 3. Repeated failures penalty (indicates suspicious brute-forcing or anomalous agent behavior)
        if failures_count >= 3:
            score += 0.5

        # 4. Requester role buffer
        if requester_role.lower() == "owner":
            score -= 0.2

        # Clamp score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))

        # Categorize
        if final_score >= 0.8:
            risk_level = "CRITICAL"
        elif final_score >= 0.6:
            risk_level = "HIGH"
        elif final_score >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_score": round(final_score, 2),
            "risk_level": risk_level,
            "requires_isolation": final_score >= 0.8
        }
