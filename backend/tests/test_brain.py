import pytest
import json
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from backend.app.main import app
from backend.app.core.db import engine
from backend.app.core.llm_client import LLMClient
from backend.app.core.brain import AIBrain
from backend.app.core.security import SESSION_FILE, STARTUP_TOKEN
from backend.app.models.schemas import TaskQueue

client = TestClient(app)

@pytest.mark.asyncio
async def test_llm_client_mock_mode():
    """Verify that the LLM client handles fallback mock outputs correctly."""
    llm = LLMClient(provider="mock")
    # Query matching standard plan keyword
    res = await llm.generate_response("system", "Build a plan for coding task", json_mode=True)
    parsed = json.loads(res)
    assert parsed["intent"] == "CreateMeetingAndEmail"
    assert len(parsed["tasks"]) == 2

@pytest.mark.asyncio
async def test_ai_brain_plan_generation():
    """Verify that the AI Brain compiles queries into structured TaskQueue models in SQLite."""
    llm = LLMClient(provider="mock")
    brain = AIBrain(llm)
    
    plan_id = uuid4()
    resp_text, tasks = await brain.generate_plan_dag(plan_id, "Schedule meeting with Bob and email him")
    
    assert len(tasks) == 2
    assert "scheduling" in resp_text.lower()
    
    # Task 2 (CommunicationAgent) must depend on Task 1 (CalendarAgent)
    task1 = tasks[0]
    task2 = tasks[1]
    
    assert task1.agent_name == "CalendarAgent"
    assert task2.agent_name == "CommunicationAgent"
    
    # Verify database insertion
    with Session(engine) as session:
        statement = select(TaskQueue).where(TaskQueue.plan_id == plan_id)
        saved = session.exec(statement).all()
        assert len(saved) == 2
        
        # Verify dependency link resolved from indices to database UUID string
        t2_db = [t for t in saved if t.agent_name == "CommunicationAgent"][0]
        t1_db = [t for t in saved if t.agent_name == "CalendarAgent"][0]
        
        deps = json.loads(t2_db.dependencies)
        assert len(deps) == 1
        assert deps[0] == str(t1_db.id)

def test_query_route_authentication():
    """Verify that the FastAPI loopback endpoints reject requests without a valid token."""
    response = client.post(
        "/api/v1/brain/query",
        json={"query": "hello", "voice_mode": False}
    )
    assert response.status_code == 422  # FastAPI validation error status code for missing required headers

def test_query_route_success():
    """Verify that the query endpoint accepts authenticated requests and initiates plans."""
    # Read the active startup handshake token
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
        
    response = client.post(
        "/api/v1/brain/query",
        headers={"X-FATE-Token": token},
        json={"query": "Schedule meeting with Bob and email him", "voice_mode": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan_triggered"] is True
    assert data["plan_id"] is not None
    assert "scheduling" in data["response_text"].lower()
