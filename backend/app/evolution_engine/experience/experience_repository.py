import time
from typing import Dict, Any, List
from uuid import uuid4

class ExperienceRepository:
    """Captures and stores user interactions, workflow execution outcomes, and human feedback (<100ms target)."""

    def __init__(self):
        self._experiences: Dict[str, Dict[str, Any]] = {}

    async def capture_experience(
        self,
        context: str,
        actions: List[str],
        results: Dict[str, Any],
        feedback_score: float = 1.0
    ) -> Dict[str, Any]:
        """Stores experience event record (<100ms latency target)."""
        start_time = time.time()
        exp_id = f"exp_{str(uuid4())[:8]}"
        
        record = {
            "experience_id": exp_id,
            "context": context,
            "actions": actions,
            "results": results,
            "feedback_score": feedback_score,
            "timestamp": time.time()
        }
        self._experiences[exp_id] = record
        
        duration_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "CAPTURED",
            "experience_id": exp_id,
            "latency_ms": duration_ms
        }

    async def list_experiences(self) -> List[Dict[str, Any]]:
        """Lists captured experience records."""
        return list(self._experiences.values())
