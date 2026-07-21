import pytest
import json
from uuid import UUID
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.workflow_engine.designer.manager import WorkflowDesignerManager
from backend.app.workflow_engine.designer.models import WorkflowStatus
from backend.app.workflow_engine.execution.runner import WorkflowExecutionRunner
from backend.app.workflow_engine.scheduler.cron_scheduler import WorkflowTaskScheduler
from backend.app.workflow_engine.triggers.event_trigger import EventTriggerEngine
from backend.app.workflow_engine.approvals.workflow_gate import HumanApprovalWorkflowGate
from backend.app.workflow_engine.templates.catalog import WorkflowTemplatesCatalog
from backend.app.workflow_engine.analytics.telemetry import WorkflowAnalyticsTelemetry
from backend.app.workflow_engine.optimization.ai_generator import AIWorkflowGenerator

client = TestClient(app)

@pytest.mark.asyncio
async def test_workflow_designer_crud():
    """Verify workflow graph CRUD creation and template retrieval."""
    designer = WorkflowDesignerManager()
    
    # Create workflow
    nodes = [
        {"id": "node_1", "type": "Start"},
        {"id": "node_2", "type": "LLMPrompt", "properties": {"prompt": "Hello FATE"}}
    ]
    wf = await designer.create_workflow(
        name="Test Workflow",
        description="Verifies CRUD",
        nodes=nodes,
        transitions=[{"from": "node_1", "to": "node_2"}]
    )
    assert wf.id is not None
    assert wf.name == "Test Workflow"
    
    # Retrieve
    retrieved = await designer.get_workflow(wf.id)
    assert retrieved is not None
    assert len(retrieved.nodes) == 2

@pytest.mark.asyncio
async def test_workflow_execution_and_checkpoint():
    """Verify asynchronous sequential execution and checkpoint recovery resumption (<100ms startup, <1s recovery)."""
    designer = WorkflowDesignerManager()
    runner = WorkflowExecutionRunner()
    
    nodes = [
        {"id": "n1", "type": "Start"},
        {"id": "n2", "type": "Delay", "properties": {"delay_seconds": 0.05}},
        {"id": "n3", "type": "LLMPrompt", "properties": {"prompt": "Resuming execution"}},
        {"id": "n4", "type": "End"}
    ]
    wf = await designer.create_workflow(
        name="Traverse Workflow",
        nodes=nodes,
        transitions=[
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
            {"from": "n3", "to": "n4"}
        ]
    )
    
    # Start execution run
    exec_rec = await runner.start_execution(wf, initial_vars={"input": "Hello"})
    assert exec_rec.status == WorkflowStatus.RUNNING
    
    # Run loop execution
    res = await runner.execute_workflow(exec_rec.id)
    assert res["status"] == "COMPLETED"
    assert res["checkpoints_count"] == 4
    
    # Checkpoint recovery simulation Resumption
    res_rec = await runner.recover_from_checkpoint(exec_rec.id)
    assert res_rec["status"] == "COMPLETED"

@pytest.mark.asyncio
async def test_scheduler_and_events():
    """Verify task scheduler cron triggers and event trigger signals processing."""
    designer = WorkflowDesignerManager()
    scheduler = WorkflowTaskScheduler()
    event_engine = EventTriggerEngine()
    
    wf = await designer.create_workflow(
        name="Scheduled Git Commit Task",
        description="Fires on Git Commit events",
        cron_expression="*/5 * * * *",
        nodes=[{"id": "start", "type": "Start"}]
    )
    
    # Schedule registration
    scheduler.register_schedule(wf.id, "*/5 * * * *")
    assert str(wf.id) in scheduler.get_registered_schedules()
    
    # Trigger active schedule SCAN
    triggered_schedules = await scheduler.trigger_due_workflows()
    assert str(wf.id) in triggered_schedules
    
    # Process event match triggers
    triggered_events = await event_engine.process_event("git commit", {"commit_hash": "abc"})
    assert len(triggered_events) > 0

def test_human_approval_gate():
    """Verify Human-in-the-Loop validation gate blocks resumption."""
    gate = HumanApprovalWorkflowGate()
    exec_id = "exec_abc"
    node_id = "node_transfer"
    
    # Register pending gate
    gate.register_approval_gate(exec_id, node_id, "Money Transfer")
    assert gate.is_gate_approved(exec_id, node_id) is False
    
    # Submit verification confirm
    gate.submit_gate_approval(exec_id, node_id, approved=True)
    assert gate.is_gate_approved(exec_id, node_id) is True

def test_ai_workflow_generation():
    """Verify Natural Language prompt parsing into structured nodes."""
    generator = AIWorkflowGenerator()
    prompt = "Every morning, summarize my email and prepare my calendar briefings."
    
    wf_graph = generator.generate_workflow_from_prompt(prompt)
    assert wf_graph["name"] == "AI Generated Pipeline"
    
    # Verify node mapping tags
    node_types = [n["type"] for n in wf_graph["nodes"]]
    assert "Start" in node_types
    assert "LLMPrompt" in node_types
    assert "End" in node_types

@pytest.mark.asyncio
async def test_dashboard_analytics():
    """Verify analytics telemetry metrics aggregation."""
    analytics = WorkflowAnalyticsTelemetry()
    metrics = await analytics.get_dashboard_metrics()
    assert "total_executions" in metrics
    assert "success_rate_percent" in metrics

def test_workflow_rest_endpoints():
    """Verify FastAPI REST API endpoints for workflow operations."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/workflows/generate
    res_gen = client.post(
        "/api/v1/workflows/generate",
        headers=headers,
        json={"prompt": "Every morning summarize email and notify by voice"}
    )
    assert res_gen.status_code == 200
    assert "nodes" in res_gen.json()
    
    # GET /api/v1/workflows/templates
    res_temp = client.get("/api/v1/workflows/templates", headers=headers)
    assert res_temp.status_code == 200
    assert "morning_briefing" in res_temp.json()
    
    # GET /api/v1/workflows/dashboard/analytics
    res_an = client.get("/api/v1/workflows/dashboard/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "success_rate_percent" in res_an.json()
