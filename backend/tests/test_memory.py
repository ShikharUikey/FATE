import pytest
import json
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.memory_graph import MemoryGraphManager
from backend.app.core.vector_db import VectorDBClient
from backend.app.core.security import SESSION_FILE

client = TestClient(app)

@pytest.mark.asyncio
async def test_memory_graph_operations():
    """Verify that MemoryGraphManager creates nodes and relationships correctly."""
    mgr = MemoryGraphManager()
    
    # Create two semantic nodes
    n1 = await mgr.get_or_create_node("Alice", "Person")
    n2 = await mgr.get_or_create_node("AcmeCorp", "Company")
    
    assert n1.entity_name == "Alice"
    assert n2.entity_name == "AcmeCorp"
    
    # Link Alice to AcmeCorp
    edge = await mgr.link_nodes(n1.id, n2.id, "works_at", weight=0.8)
    assert edge.relation_type == "works_at"
    assert edge.weight == 0.8
    
    # Query direct connections for Alice
    conns = mgr.query_connections(n1.id)
    assert len(conns) >= 1
    assert conns[0][0] == "AcmeCorp"
    assert conns[0][1] == "works_at"

def test_qdrant_vector_search():
    """Verify that local in-memory QdrantClient indexes and retrieves vectors successfully."""
    vdb = VectorDBClient()
    vdb.init_collections()
    
    point_id = str(uuid4())
    # 384 dimensions vector representation
    vector = [0.1] * 384
    payload = {"text": "Alice works at AcmeCorp", "category": "employment"}
    
    vdb.upsert_embedding("user_memories", point_id, vector, payload)
    
    # Query the collection
    results = vdb.search_similar("user_memories", vector, limit=1)
    assert len(results) == 1
    assert results[0]["category"] == "employment"
    assert results[0]["text"] == "Alice works at AcmeCorp"

def test_memory_routes_e2e():
    """Verify end-to-end operation of memory endpoints."""
    # Read session token
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
        
    headers = {"X-FATE-Token": token}
    
    # 1. Create source node
    r1 = client.post(
        "/api/v1/memory/node",
        headers=headers,
        json={"name": "Bob", "type": "Person"}
    )
    assert r1.status_code == 201
    node1_id = r1.json()["id"]
    
    # 2. Create target node
    r2 = client.post(
        "/api/v1/memory/node",
        headers=headers,
        json={"name": "Paris", "type": "Location"}
    )
    assert r2.status_code == 201
    node2_id = r2.json()["id"]
    
    # 3. Link Bob to Paris
    r3 = client.post(
        "/api/v1/memory/edge",
        headers=headers,
        json={
            "source_id": node1_id,
            "target_id": node2_id,
            "relation": "visited",
            "weight": 1.0
        }
    )
    assert r3.status_code == 201
    assert r3.json()["relation"] == "visited"
    
    # 4. Fetch connections
    r4 = client.get(
        "/api/v1/memory/connections",
        headers=headers,
        params={"node_id": node1_id}
    )
    assert r4.status_code == 200
    conns = r4.json()
    assert len(conns) >= 1
    assert conns[0]["target_name"] == "Paris"
    assert conns[0]["relation_type"] == "visited"
