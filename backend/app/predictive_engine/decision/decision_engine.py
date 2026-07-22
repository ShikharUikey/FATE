import time
from typing import Dict, Any, List

class DecisionRankingEngine:
    """Decision Engine evaluating expected benefits, risks, costs & confidence (<200ms prediction target)."""

    def rank_decision_options(
        self,
        options: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Ranks decision choices based on risk-adjusted benefit score (<200ms target)."""
        ranked = []
        for opt in options:
            benefit = opt.get("benefit_score", 80)
            risk = opt.get("risk_score", 20)
            cost = opt.get("cost_score", 30)
            score = round((benefit * 0.6) - (risk * 0.25) - (cost * 0.15), 2)
            
            ranked_opt = dict(opt)
            ranked_opt["decision_rank_score"] = score
            ranked.append(ranked_opt)
            
        return sorted(ranked, key=lambda x: x["decision_rank_score"], reverse=True)
