from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.evolution_engine.experience.experience_repository import ExperienceRepository
from backend.app.evolution_engine.reflection.reflection_engine import StructuredReflectionEngine
from backend.app.evolution_engine.learning.continual_learner import ContinualLearningEngine
from backend.app.evolution_engine.prompts.prompt_optimizer import PromptOptimizerEngine
from backend.app.evolution_engine.skills.skill_discoverer import SkillDiscoveryPlatform
from backend.app.evolution_engine.workflows.workflow_evolver import WorkflowEvolverEngine
from backend.app.evolution_engine.evaluation.model_evaluator import ModelEvaluationEngine
from backend.app.evolution_engine.governance.evolution_governance import EvolutionGovernanceManager
from backend.app.evolution_engine.research.ai_research_lab import AIResearchLabEngine
from backend.app.evolution_engine.analytics.evolution_telemetry import EvolutionTelemetryEngine
from backend.app.evolution_engine.security.evolution_security import EvolutionSecurityGuard

router = APIRouter(
    prefix="/api/v1/evolution-engine",
    tags=["Autonomous Learning & Evolution Engine"]
)

# Managers Singletons
experience_repo = ExperienceRepository()
reflection_engine = StructuredReflectionEngine()
learning_engine = ContinualLearningEngine()
prompt_optimizer = PromptOptimizerEngine()
skill_discoverer = SkillDiscoveryPlatform()
workflow_evolver = WorkflowEvolverEngine()
model_evaluator = ModelEvaluationEngine()
governance = EvolutionGovernanceManager()
research_lab = AIResearchLabEngine()
telemetry = EvolutionTelemetryEngine()
security = EvolutionSecurityGuard()

class CaptureExperiencePayload(BaseModel):
    context: str
    actions: List[str]
    results: Dict[str, Any]
    feedback_score: Optional[float] = 1.0

class ReflectionPayload(BaseModel):
    target_entity: Optional[str] = "workflow_executor"

class OptimizePromptPayload(BaseModel):
    current_prompt: str
    target_goal: Optional[str] = "reduce_token_cost"

class DiscoverSkillPayload(BaseModel):
    execution_trace: List[Dict[str, Any]]

class RewardSignalPayload(BaseModel):
    agent_id: str
    action_name: str
    reward_score: float

@router.post("/experience/store", dependencies=[Depends(verify_session_token)])
async def store_experience(payload: CaptureExperiencePayload):
    """Captures and stores experience record (<100ms target)."""
    return await experience_repo.capture_experience(
        context=payload.context,
        actions=payload.actions,
        results=payload.results,
        feedback_score=payload.feedback_score or 1.0
    )

@router.get("/experience/list", dependencies=[Depends(verify_session_token)])
async def list_experiences():
    """Lists captured experience records."""
    return await experience_repo.list_experiences()

@router.post("/reflection/generate", dependencies=[Depends(verify_session_token)])
async def generate_reflection(payload: ReflectionPayload):
    """Generates structured reflection report (<1s target)."""
    return await reflection_engine.generate_reflection_report(target_entity=payload.target_entity or "workflow_executor")

@router.post("/prompts/optimize", dependencies=[Depends(verify_session_token)])
async def optimize_prompt(payload: OptimizePromptPayload):
    """Auto-tunes prompt text to reduce latency and token usage (<2s target)."""
    return await prompt_optimizer.optimize_prompt(current_prompt=payload.current_prompt, target_goal=payload.target_goal or "reduce_token_cost")

@router.post("/skills/discover", dependencies=[Depends(verify_session_token)])
async def discover_skill(payload: DiscoverSkillPayload):
    """Synthesizes reusable skill from execution trace (<3s target)."""
    return await skill_discoverer.discover_new_skill(payload.execution_trace)

@router.post("/reward", dependencies=[Depends(verify_session_token)])
async def submit_reward(payload: RewardSignalPayload):
    """Submits RL reward signal for policy optimization."""
    return learning_engine.process_reward_signal(
        agent_id=payload.agent_id,
        action_name=payload.action_name,
        reward_score=payload.reward_score
    )

@router.get("/research/upgrades", dependencies=[Depends(verify_session_token)])
async def evaluate_upgrades():
    """Queries AI Research Lab benchmarked model upgrades."""
    return research_lab.evaluate_model_upgrades()

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics():
    """Queries evolution platform telemetry statistics."""
    return telemetry.get_evolution_analytics_summary()
