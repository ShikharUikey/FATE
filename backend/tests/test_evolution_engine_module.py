import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
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

client = TestClient(app)

@pytest.mark.asyncio
async def test_experience_repository():
    """Verify capturing and storing experiences (<100ms latency target)."""
    repo = ExperienceRepository()
    res = await repo.capture_experience(
        context="K8s canary deployment",
        actions=["verify_prometheus", "scale_pods"],
        results={"success": True},
        feedback_score=1.0
    )
    
    assert res["status"] == "CAPTURED"
    assert res["latency_ms"] < 100.0
    assert len(await repo.list_experiences()) == 1

@pytest.mark.asyncio
async def test_structured_reflection_engine():
    """Verify structured reflection report generation (<1s target)."""
    reflection = StructuredReflectionEngine()
    res = await reflection.generate_reflection_report("workflow_executor")
    
    assert res["status"] == "COMPLETED"
    assert res["reflection_time_seconds"] < 1.0
    assert len(res["lessons_learned"]) >= 1

def test_continual_learning_engine():
    """Verify RL reward signal processing."""
    learner = ContinualLearningEngine()
    res = learner.process_reward_signal("agent_coding_master", "refactor_code", reward_score=1.5)
    
    assert res["learning_policy_updated"] is True
    assert res["new_action_weight"] > 0.5

@pytest.mark.asyncio
async def test_prompt_optimizer_engine():
    """Verify prompt auto-tuning (<2s target)."""
    optimizer = PromptOptimizerEngine()
    res = await optimizer.optimize_prompt("You are a helpful coding assistant.")
    
    assert res["status"] == "OPTIMIZED"
    assert res["duration_seconds"] < 2.0
    assert "[Optimization Rule:" in res["optimized_prompt"]

@pytest.mark.asyncio
async def test_skill_discovery_platform():
    """Verify reusable skill discovery (<3s target)."""
    discoverer = SkillDiscoveryPlatform()
    res = await discoverer.discover_new_skill([{"step": "check_k8s"}, {"step": "verify_canary"}])
    
    assert res["status"] == "DISCOVERED"
    assert res["duration_seconds"] < 3.0
    assert res["reusable"] is True

def test_workflow_evolver_engine():
    """Verify workflow execution optimization."""
    evolver = WorkflowEvolverEngine()
    res = evolver.evolve_workflow_structure("wf_cicd_deploy", [{"step": "build"}, {"step": "test"}])
    
    assert res["status"] == "EVOLVED"
    assert res["estimated_speedup_percent"] > 0.0

def test_model_evaluation_engine():
    """Verify model accuracy metrics & hallucination detection."""
    evaluator = ModelEvaluationEngine()
    res = evaluator.evaluate_model_performance("gemini_pro_flash")
    
    assert res["status"] == "HEALTHY"
    assert res["accuracy"] > 0.9

def test_evolution_governance_and_security():
    """Verify evolutionary governance policies and experience privacy masking."""
    gov = EvolutionGovernanceManager()
    proposal = gov.validate_evolution_proposal("prop_001", "permission_policy")
    assert proposal["requires_human_approval"] is True
    
    sec = EvolutionSecurityGuard()
    privacy = sec.validate_experience_privacy({"user_query": "secret_key"})
    assert privacy["privacy_compliance"] == "VERIFIED"

def test_evolution_engine_rest_endpoints():
    """Verify FastAPI REST API endpoints for Autonomous Learning Engine."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/evolution-engine/experience/store
    res_exp = client.post(
        "/api/v1/evolution-engine/experience/store",
        headers=headers,
        json={"context": "Build test", "actions": ["compile"], "results": {"status": "ok"}}
    )
    assert res_exp.status_code == 200
    assert res_exp.json()["status"] == "CAPTURED"
    
    # POST /api/v1/evolution-engine/reflection/generate
    res_ref = client.post("/api/v1/evolution-engine/reflection/generate", headers=headers, json={})
    assert res_ref.status_code == 200
    assert res_ref.json()["status"] == "COMPLETED"
    
    # POST /api/v1/evolution-engine/prompts/optimize
    res_prm = client.post(
        "/api/v1/evolution-engine/prompts/optimize",
        headers=headers,
        json={"current_prompt": "Answer concisely."}
    )
    assert res_prm.status_code == 200
    assert res_prm.json()["status"] == "OPTIMIZED"
    
    # GET /api/v1/evolution-engine/analytics
    res_an = client.get("/api/v1/evolution-engine/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "learning_velocity_score" in res_an.json()
