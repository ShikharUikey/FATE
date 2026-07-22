import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.predictive_engine.forecasting.forecaster import TimeSeriesForecaster
from backend.app.predictive_engine.optimization.optimizer import MultiObjectiveOptimizer
from backend.app.predictive_engine.simulation.simulator import MonteCarloSimulator
from backend.app.predictive_engine.decision.decision_engine import DecisionRankingEngine
from backend.app.predictive_engine.recommendation.recommender import StrategicRecommendationEngine
from backend.app.predictive_engine.causal_ai.causal_reasoner import CausalReasonerEngine
from backend.app.predictive_engine.digital_twin.twin_platform import DigitalTwinPlatform
from backend.app.predictive_engine.models.model_registry import ModelRegistryManager
from backend.app.predictive_engine.analytics.predictive_telemetry import PredictiveTelemetryEngine
from backend.app.predictive_engine.security.predictive_security import PredictiveSecurityGuard

client = TestClient(app)

@pytest.mark.asyncio
async def test_time_series_forecaster():
    """Verify metric trend forecasting (<500ms query target)."""
    forecaster = TimeSeriesForecaster()
    res = await forecaster.predict_metric_trend("cloud_cost_monthly", forecast_horizon_days=14)
    
    assert res["status"] == "SUCCESS"
    assert res["latency_ms"] < 500.0
    assert len(res["forecast_trajectory"]) == 14

def test_multi_objective_optimizer():
    """Verify multi-objective resource constraint optimization (<2s target)."""
    optimizer = MultiObjectiveOptimizer()
    res = optimizer.optimize_resource_allocation(
        objectives=["reduce_cloud_cost", "improve_latency"],
        constraints={"max_budget_usd": 1000}
    )
    
    assert res["status"] == "OPTIMAL"
    assert res["duration_seconds"] < 2.0
    assert "recommended_allocation" in res

@pytest.mark.asyncio
async def test_monte_carlo_simulator():
    """Verify Monte Carlo scenario simulator (<5s target)."""
    simulator = MonteCarloSimulator()
    res = await simulator.run_scenario_simulation("CloudOutageDisaster", iterations=500)
    
    assert res["status"] == "SIMULATED"
    assert res["simulation_duration_seconds"] < 5.0
    assert res["worst_case_score"] < res["best_case_score"]

def test_decision_ranking_engine():
    """Verify decision choices ranking (<200ms prediction target)."""
    engine = DecisionRankingEngine()
    options = [
        {"option_id": "opt_a", "benefit_score": 90, "risk_score": 10, "cost_score": 20},
        {"option_id": "opt_b", "benefit_score": 60, "risk_score": 50, "cost_score": 40}
    ]
    ranked = engine.rank_decision_options(options)
    
    assert len(ranked) == 2
    assert ranked[0]["option_id"] == "opt_a"

def test_strategic_recommendation_engine():
    """Verify strategic recommendations for costs and security."""
    recommender = StrategicRecommendationEngine()
    recs = recommender.generate_recommendations()
    assert len(recs) >= 2

def test_causal_reasoner_engine():
    """Verify cause-and-effect dependency tree and root cause analysis."""
    causal = CausalReasonerEngine()
    res = causal.explain_root_cause("DatabaseConnectionTimeout")
    assert res["causal_confidence"] > 0.9
    assert len(res["dependency_path"]) >= 3

def test_digital_twin_platform():
    """Verify virtual twin state representation query (<1s target)."""
    twin_platform = DigitalTwinPlatform()
    twin = twin_platform.query_twin_state("twin_cluster_aws_prod")
    
    assert twin["virtual_status"] == "HEALTHY"
    assert twin["query_latency_ms"] < 1000.0

def test_model_registry_and_security():
    """Verify ML model registry metadata and prediction access controls."""
    registry = ModelRegistryManager()
    models = registry.list_models()
    assert len(models) >= 1
    
    sec = PredictiveSecurityGuard()
    assert sec.validate_prediction_access("Admin") is True

def test_predictive_engine_rest_endpoints():
    """Verify FastAPI REST API endpoints for Predictive Intelligence Engine."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/predictive-engine/forecast
    res_fc = client.post(
        "/api/v1/predictive-engine/forecast",
        headers=headers,
        json={"metric_name": "task_workload", "horizon_days": 7}
    )
    assert res_fc.status_code == 200
    assert res_fc.json()["status"] == "SUCCESS"
    
    # POST /api/v1/predictive-engine/optimize
    res_opt = client.post(
        "/api/v1/predictive-engine/optimize",
        headers=headers,
        json={"objectives": ["cost"], "constraints": {}}
    )
    assert res_opt.status_code == 200
    assert res_opt.json()["status"] == "OPTIMAL"
    
    # GET /api/v1/predictive-engine/recommendations
    res_rec = client.get("/api/v1/predictive-engine/recommendations", headers=headers)
    assert res_rec.status_code == 200
    assert len(res_rec.json()) >= 2
    
    # GET /api/v1/predictive-engine/analytics
    res_an = client.get("/api/v1/predictive-engine/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "forecast_accuracy_percent" in res_an.json()
