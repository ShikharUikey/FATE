from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from uuid import uuid4
import asyncio

from backend.app.core.security import verify_session_token
from backend.app.core.llm_client import LLMClient
from backend.app.core.brain import AIBrain
from backend.app.core.orchestrator import AgentOrchestrator

router = APIRouter(
    prefix="/api/v1/brain",
    tags=["Brain Engine"]
)

# Singletons initialized for runtime loop back
llm_client = LLMClient()
brain = AIBrain(llm_client)
orchestrator = AgentOrchestrator()

class QueryRequest(BaseModel):
    query: str
    voice_mode: bool = False

class QueryResponse(BaseModel):
    query_id: str
    intent: str
    response_text: str
    plan_triggered: bool
    plan_id: str

@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(verify_session_token)])
async def execute_query(payload: QueryRequest):
    """Endpoints executing the AI Brain planner and launching Orchestrator loops."""
    plan_id = uuid4()
    query_id = uuid4()
    
    # 1. Generate plan DAG and save to SQLite
    response_text, tasks = await brain.generate_plan_dag(plan_id, payload.query)
    
    plan_triggered = len(tasks) > 0
    
    # 2. Trigger Orchestrator loop in the background if tasks exist
    if plan_triggered:
        asyncio.create_task(orchestrator.execute_plan(plan_id))
        
    return QueryResponse(
        query_id=str(query_id),
        intent="ParsedPlanIntent" if plan_triggered else "DirectResponse",
        response_text=response_text,
        plan_triggered=plan_triggered,
        plan_id=str(plan_id)
    )
