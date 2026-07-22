import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.analytics_platform.ingestion.pipeline import EnterpriseDataPipeline
from backend.app.analytics_platform.processing.processor import MetricsKPIProcessor
from backend.app.analytics_platform.dashboards.dashboard_manager import ExecutiveDashboardPlatform
from backend.app.analytics_platform.insights.ai_insight_engine import AIInsightEngine
from backend.app.analytics_platform.forecasting.forecasting_engine import PredictiveForecastingEngine
from backend.app.analytics_platform.reporting.reporting_engine import AutomatedReportingEngine
from backend.app.analytics_platform.visualization.visualization_engine import DataVisualizationEngine
from backend.app.analytics_platform.alerts.alert_manager import AnalyticsAlertManager
from backend.app.analytics_platform.security.analytics_security import AnalyticsSecurityGuard

client = TestClient(app)

@pytest.mark.asyncio
async def test_data_pipeline_ingestion():
    """Verify multi-module telemetry streaming ingestion (<1s target)."""
    pipe = EnterpriseDataPipeline()
    res = await pipe.ingest_event(
        source_module="workflow_engine",
        event_type="WORKFLOW_COMPLETED",
        payload={"workflow_id": "wf_101", "duration_ms": 240}
    )
    assert res["status"] == "INGESTED"
    assert res["ingest_duration_ms"] < 1000.0
    assert await pipe.get_buffer_count() == 1

def test_metrics_kpi_processor():
    """Verify system-wide KPI calculation and metrics aggregation."""
    proc = MetricsKPIProcessor()
    kpis = proc.compute_system_kpis()
    
    assert kpis["task_completion_rate_percent"] > 90.0
    assert kpis["cloud_cost_monthly_usd"] > 0
    assert "total_llm_tokens_consumed" in kpis

@pytest.mark.asyncio
async def test_executive_dashboard_rendering():
    """Verify executive overview & cloud cost dashboards rendering (<2s load target)."""
    dash = ExecutiveDashboardPlatform()
    res = await dash.render_dashboard("executive_overview")
    
    assert res["dashboard"] == "executive_overview"
    assert res["load_time_ms"] < 2000.0
    assert len(res["content"]["widgets"]) > 0

def test_ai_insight_engine():
    """Verify AI insight discovery and natural language bottleneck explanations."""
    engine = AIInsightEngine()
    result = engine.generate_executive_insights()
    
    assert result["insights_count"] > 0
    assert "explanation" in result["insights"][0]

def test_predictive_forecasting_engine():
    """Verify predictive cloud spend forecasting (<500ms query target)."""
    forecaster = PredictiveForecastingEngine()
    fc = forecaster.forecast_cloud_spend(horizon_days=30)
    
    assert fc["query_duration_ms"] < 500.0
    assert fc["projected_spend_usd"] > fc["current_monthly_spend_usd"]

@pytest.mark.asyncio
async def test_automated_reporting_engine():
    """Verify executive report document generation (<10s target)."""
    reporter = AutomatedReportingEngine()
    report = await reporter.generate_executive_report(report_type="daily_executive", export_format="json")
    
    assert report["status"] == "GENERATED"
    assert report["generation_time_seconds"] < 10.0
    assert "kpis" in report["content"]

def test_data_visualization_engine():
    """Verify chart payload formatting for line, bar, and heatmap visualizers."""
    vis = DataVisualizationEngine()
    chart = vis.format_chart_payload("line_chart", {"x": [1, 2, 3], "y": [10, 20, 15]})
    
    assert chart["chart_type"] == "line_chart"
    assert chart["render_config"]["animation"] is True

def test_alert_manager():
    """Verify analytical alert dispatches and alerts listing."""
    alerts = AnalyticsAlertManager()
    res = alerts.dispatch_alert("CloudBudget", "Monthly Budget Warning", "85% of AWS budget reached", severity="WARNING")
    
    assert res["status"] == "DISPATCHED"
    assert len(alerts.list_active_alerts()) == 1

def test_analytics_security():
    """Verify RBAC dashboard access evaluation and payload data masking."""
    sec = AnalyticsSecurityGuard()
    assert sec.evaluate_dashboard_access("executive", "executive_overview") is True
    assert sec.evaluate_dashboard_access("developer", "executive_overview") is False
    
    masked = sec.mask_sensitive_payload({"user": "admin", "token": "secret_12345"})
    assert masked["token"] == "***MASKED***"

def test_analytics_rest_endpoints():
    """Verify FastAPI REST API endpoints for Analytics Platform."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/analytics-platform/ingest
    res_ing = client.post(
        "/api/v1/analytics-platform/ingest",
        headers=headers,
        json={"source_module": "brain", "event_type": "LLM_INFERENCE", "payload": {"tokens": 150}}
    )
    assert res_ing.status_code == 200
    assert res_ing.json()["status"] == "INGESTED"
    
    # GET /api/v1/analytics-platform/kpis
    res_kpi = client.get("/api/v1/analytics-platform/kpis", headers=headers)
    assert res_kpi.status_code == 200
    assert "task_completion_rate_percent" in res_kpi.json()
    
    # GET /api/v1/analytics-platform/dashboards/executive_overview
    res_dash = client.get("/api/v1/analytics-platform/dashboards/executive_overview", headers=headers)
    assert res_dash.status_code == 200
    assert res_dash.json()["dashboard"] == "executive_overview"
    
    # GET /api/v1/analytics-platform/forecasting/spend
    res_fc = client.get("/api/v1/analytics-platform/forecasting/spend", headers=headers)
    assert res_fc.status_code == 200
    assert "projected_spend_usd" in res_fc.json()
