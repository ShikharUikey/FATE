import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE

client = TestClient(app)

def get_auth_headers():
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    return {"X-FATE-Token": token}

def test_chatbot_health():
    """Verify essential core health check endpoint."""
    headers = get_auth_headers()
    response = client.get("/api/v1/health", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_chatbot_query_maths_and_everyday_tasks():
    """Verify Chatbot handling mathematical questions and everyday tasks."""
    headers = get_auth_headers()
    
    # 1. Everyday task prompt
    res_task = client.post("/api/v1/brain/query", headers=headers, json={"query": "Help me summarize my daily schedule and format an email outline."})
    assert res_task.status_code == 200
    assert "response_text" in res_task.json()
    
    # 2. Maths evaluation prompt
    res_math = client.post("/api/v1/brain/query", headers=headers, json={"query": "Calculate 15% tip on a $120 bill and solve 45 * 12."})
    assert res_math.status_code == 200
    assert len(res_math.json()["query_id"]) > 0

def test_essential_endpoints_active_and_auxiliary_disabled():
    """Verify only essential Chatbot endpoints are mounted in main.py."""
    headers = get_auth_headers()
    
    # Essential active endpoints
    assert client.get("/api/v1/health", headers=headers).status_code == 200
    
    # Auxiliary endpoints are disabled/commented out for clean lightweight Chatbot focus
    res_aux_cloud = client.get("/api/v1/cloud/infrastructure/status", headers=headers)
    assert res_aux_cloud.status_code == 404
    
    res_aux_evolution = client.get("/api/v1/evolution-engine/analytics", headers=headers)
    assert res_aux_evolution.status_code == 404
