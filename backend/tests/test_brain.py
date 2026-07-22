import pytest
import json
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.llm_client import LLMClient
from backend.app.core.brain import AIBrain
from backend.app.core.security import SESSION_FILE

client = TestClient(app)

@pytest.mark.asyncio
async def test_llm_client_mock_mode():
    """Verify that the LLM client handles fallback outputs cleanly without dummy email hardcodes."""
    llm = LLMClient(provider="mock")
    res = await llm.generate_response("system", "Explain quantum computing", json_mode=True)
    parsed = json.loads(res)
    assert parsed["intent"] == "GeneralQuery"
    assert "Processed query" in parsed["response_text"] or "Quantum" in parsed["response_text"]

@pytest.mark.asyncio
async def test_ai_brain_math_and_query_generation():
    """Verify that the AI Brain compiles queries and handles direct math expressions."""
    llm = LLMClient(provider="mock")
    brain = AIBrain(llm)
    
    plan_id = uuid4()
    # Test math calculation direct evaluation
    resp_math, tasks_math = await brain.generate_plan_dag(plan_id, "6+7-4")
    assert "9" in resp_math
    assert len(tasks_math) == 0

    # Test general task query
    plan_id_2 = uuid4()
    resp_general, tasks_gen = await brain.generate_plan_dag(plan_id_2, "Analyze weekly progress report")
    assert "Processed query" in resp_general or "Analyze" in resp_general

def test_query_route_authentication():
    """Verify that FastAPI endpoints require a valid security token."""
    response = client.post(
        "/api/v1/brain/query",
        json={"query": "hello", "voice_mode": False}
    )
    assert response.status_code == 422

def test_query_route_success():
    """Verify that the query endpoint returns clean responses for user prompts."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
        
    response = client.post(
        "/api/v1/brain/query",
        headers={"X-FATE-Token": token},
        json={"query": "Calculate 45 * 12", "voice_mode": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert "540" in data["response_text"]
