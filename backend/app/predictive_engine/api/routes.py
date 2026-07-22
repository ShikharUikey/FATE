from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
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

router = APIRouter(
    prefix="/api/v1/predictive-engine",
    tags=["Predictive Intelligence & Decision Intelligence Engine"]
)

# Managers Singletons
forecaster = TimeSeriesForecaster()
optimizer = MultiObjectiveOptimizer()
simulator = MonteCarloSimulator()
decision_engine = DecisionRankingEngine()
recommender = StrategicRecommendationEngine()
causal_reasoner = CausalReasonerEngine()
digital_twin = DigitalTwinPlatform()
model_registry = ModelRegistryManager()
telemetry = PredictiveTelemetryEngine()
security = PredictiveSecurityGuard()

class ForecastPayload(BaseModel):
    metric_name: str
    horizon_days: Optional[int] = 30

class OptimizePayload(BaseModel):
    objectives: List[str]
    constraints: Dict[str, Any]

class SimulatePayload(BaseModel):
    scenario_name: str
    iterations: Optional[int] = 1000

class DecisionRankPayload(BaseModel):
    options: List[Dict[str, Any]]

@router.post("/forecast", dependencies=[Depends(verify_session_token)])
async def forecast_metric(payload: ForecastPayload):
    """Computes time-series trend forecasting (<500ms target)."""
    return await forecaster.predict_metric_trend(
        metric_name=payload.metric_name,
        forecast_horizon_days=payload.horizon_days or 30
    )

@router.post("/optimize", dependencies=[Depends(verify_session_token)])
async def optimize_resources(payload: OptimizePayload):
    """Executes multi-objective constraint optimization (<2s target)."""
    return optimizer.optimize_resource_allocation(
        objectives=payload.objectives,
        constraints=payload.constraints
    )

@router.post("/simulate", dependencies=[Depends(verify_session_token)])
async def run_simulation(payload: SimulatePayload):
    """Runs Monte Carlo scenario simulation (<5s target)."""
    return await simulator.run_scenario_simulation(
        scenario_name=payload.scenario_name,
        iterations=payload.iterations or 1000
    )

@router.post("/decision/rank", dependencies=[Depends(verify_session_token)])
async def rank_decisions(payload: DecisionRankPayload):
    """Ranks decision choices based on risk-adjusted benefit score (<200ms target)."""
    return decision_engine.rank_decision_options(payload.options)

@router.get("/recommendations", dependencies=[Depends(verify_session_token)])
async def get_recommendations():
    """Generates strategic recommendation list."""
    return recommender.generate_recommendations()

@router.get("/causal/explain", dependencies=[Depends(verify_session_token)])
async def explain_root_cause(event_name: str = "MemorySpike"):
    """Traces cause-and-effect dependency graph to explain root cause."""
    return causal_reasoner.explain_root_cause(event_name=event_name)

@router.get("/digital-twin/{twin_id}", dependencies=[Depends(verify_session_token)])
async def query_digital_twin(twin_id: str):
    """Queries virtual twin state representation (<1s query target)."""
    return digital_twin.query_twin_state(twin_id=twin_id)

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics():
    """Queries predictive analytics summary metrics."""
    return telemetry.get_predictive_engine_analytics()
