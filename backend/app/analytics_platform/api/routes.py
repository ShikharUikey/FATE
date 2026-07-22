from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.analytics_platform.ingestion.pipeline import EnterpriseDataPipeline
from backend.app.analytics_platform.processing.processor import MetricsKPIProcessor
from backend.app.analytics_platform.dashboards.dashboard_manager import ExecutiveDashboardPlatform
from backend.app.analytics_platform.insights.ai_insight_engine import AIInsightEngine
from backend.app.analytics_platform.forecasting.forecasting_engine import PredictiveForecastingEngine
from backend.app.analytics_platform.reporting.reporting_engine import AutomatedReportingEngine
from backend.app.analytics_platform.visualization.visualization_engine import DataVisualizationEngine
from backend.app.analytics_platform.alerts.alert_manager import AnalyticsAlertManager
from backend.app.analytics_platform.security.analytics_security import AnalyticsSecurityGuard

router = APIRouter(
    prefix="/api/v1/analytics-platform",
    tags=["Enterprise Analytics & Intelligence Platform"]
)

# Managers Singletons
pipeline = EnterpriseDataPipeline()
processor = MetricsKPIProcessor()
dashboards = ExecutiveDashboardPlatform()
insights_engine = AIInsightEngine()
forecaster = PredictiveForecastingEngine()
reporter = AutomatedReportingEngine()
visualizer = DataVisualizationEngine()
alerts_mgr = AnalyticsAlertManager()
security_guard = AnalyticsSecurityGuard()

class IngestEventRequest(BaseModel):
    source_module: str
    event_type: str
    payload: Dict[str, Any]

class GenerateReportRequest(BaseModel):
    report_type: Optional[str] = "daily_executive"
    export_format: Optional[str] = "json"

class DispatchAlertRequest(BaseModel):
    alert_category: str
    title: str
    message: str
    severity: Optional[str] = "WARNING"

@router.post("/ingest", dependencies=[Depends(verify_session_token)])
async def ingest_event(payload: IngestEventRequest):
    """Ingests telemetry event from JARVIS modules (<1s target)."""
    return await pipeline.ingest_event(
        source_module=payload.source_module,
        event_type=payload.event_type,
        payload=payload.payload
    )

@router.get("/kpis", dependencies=[Depends(verify_session_token)])
async def get_system_kpis():
    """Queries aggregated system-wide executive KPIs."""
    return processor.compute_system_kpis()

@router.get("/dashboards/{name}", dependencies=[Depends(verify_session_token)])
async def get_dashboard(name: str):
    """Renders executive dashboard content (<2s load target)."""
    return await dashboards.render_dashboard(dashboard_name=name)

@router.get("/insights", dependencies=[Depends(verify_session_token)])
async def get_insights():
    """Queries AI-discovered operational insights & bottleneck explanations."""
    return insights_engine.generate_executive_insights()

@router.get("/forecasting/spend", dependencies=[Depends(verify_session_token)])
async def forecast_spend(horizon_days: Optional[int] = 30):
    """Queries predictive cloud spend trajectory forecast (<500ms target)."""
    return forecaster.forecast_cloud_spend(horizon_days=horizon_days or 30)

@router.post("/reports/generate", dependencies=[Depends(verify_session_token)])
async def generate_report(payload: GenerateReportRequest):
    """Generates executive report document (<10s target)."""
    return await reporter.generate_executive_report(
        report_type=payload.report_type or "daily_executive",
        export_format=payload.export_format or "json"
    )

@router.post("/alerts/dispatch", dependencies=[Depends(verify_session_token)])
async def dispatch_alert(payload: DispatchAlertRequest):
    """Dispatches analytical alert notification."""
    return alerts_mgr.dispatch_alert(
        alert_category=payload.alert_category,
        title=payload.title,
        message=payload.message,
        severity=payload.severity or "WARNING"
    )
