from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.app.core.security import verify_session_token
from backend.app.workflow_engine.designer.manager import WorkflowDesignerManager
from backend.app.workflow_engine.designer.models import WorkflowStatus
from backend.app.workflow_engine.execution.runner import WorkflowExecutionRunner
from backend.app.workflow_engine.scheduler.cron_scheduler import WorkflowTaskScheduler
from backend.app.workflow_engine.triggers.event_trigger import EventTriggerEngine
from backend.app.workflow_engine.approvals.workflow_gate import HumanApprovalWorkflowGate
from backend.app.workflow_engine.templates.catalog import WorkflowTemplatesCatalog
from backend.app.workflow_engine.analytics.telemetry import WorkflowAnalyticsTelemetry
from backend.app.workflow_engine.optimization.ai_generator import AIWorkflowGenerator

router = APIRouter(
    prefix="/api/v1/workflows",
    tags=["Workflow Engine"]
)

# Managers Singletons
designer_mgr = WorkflowDesignerManager()
runner = WorkflowExecutionRunner()
scheduler = WorkflowTaskScheduler()
event_engine = EventTriggerEngine()
approval_gate = HumanApprovalWorkflowGate()
analytics = WorkflowAnalyticsTelemetry()
ai_generator = AIWorkflowGenerator()

class CreateWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    transitions: Optional[List[Dict[str, Any]]] = None
    cron_expression: Optional[str] = None

class ExecuteWorkflowRequest(BaseModel):
    workflow_id: UUID
    variables: Optional[Dict[str, Any]] = None

class ResumeWorkflowRequest(BaseModel):
    execution_id: UUID

class SubmitApprovalRequest(BaseModel):
    execution_id: str
    node_id: str
    approved: bool

class GeneratePromptRequest(BaseModel):
    prompt: str

@router.post("", dependencies=[Depends(verify_session_token)])
async def create_workflow(payload: CreateWorkflowRequest):
    """Saves workflow graph design template."""
    return await designer_mgr.create_workflow(
        name=payload.name,
        description=payload.description,
        nodes=payload.nodes,
        transitions=payload.transitions,
        cron_expression=payload.cron_expression
    )

@router.post("/execute", dependencies=[Depends(verify_session_token)])
async def execute_workflow(payload: ExecuteWorkflowRequest):
    """Asynchronously starts and runs workflow execution pipeline (<100ms startup)."""
    wf = await designer_mgr.get_workflow(payload.workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    exec_rec = await runner.start_execution(wf, initial_vars=payload.variables)
    # Async execution
    return await runner.execute_workflow(exec_rec.id)

@router.post("/resume", dependencies=[Depends(verify_session_token)])
async def resume_workflow(payload: ResumeWorkflowRequest):
    """Restores variables and resumes workflow from last saved state checkpoint (<1s target)."""
    return await runner.recover_from_checkpoint(payload.execution_id)

@router.post("/approvals/submit", dependencies=[Depends(verify_session_token)])
async def submit_approval(payload: SubmitApprovalRequest):
    """Submits confirmation to resume a gated pending approval node transition."""
    success = approval_gate.submit_gate_approval(
        execution_id=payload.execution_id,
        node_id=payload.node_id,
        approved=payload.approved
    )
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/generate", dependencies=[Depends(verify_session_token)])
async def generate_workflow(payload: GeneratePromptRequest):
    """AI natural language prompt workflow builder generation parser."""
    return ai_generator.generate_workflow_from_prompt(payload.prompt)

@router.get("/templates", dependencies=[Depends(verify_session_token)])
async def get_templates():
    """Lists pre-configured workflow templates."""
    return WorkflowTemplatesCatalog.get_templates()

@router.get("/dashboard/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics_metrics():
    """Queries dashboard metrics summary (cost, token allocations, success ratios)."""
    return await analytics.get_dashboard_metrics()
