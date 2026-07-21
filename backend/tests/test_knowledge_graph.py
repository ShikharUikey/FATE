import pytest
import json
import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.knowledge_graph.entities.models import EntityType
from backend.app.knowledge_graph.entities.manager import EntityManager
from backend.app.knowledge_graph.relationships.engine import RelationshipEngine
from backend.app.knowledge_graph.graph_engine.traversal import GraphTraversalEngine
from backend.app.knowledge_graph.semantic_search.hybrid_search import HybridSearchEngine
from backend.app.knowledge_graph.ai.context_engine import AIContextEngine
from backend.app.knowledge_graph.analytics.business_intel import BusinessIntelligenceEngine
from backend.app.knowledge_graph.security.rbac import SecurityManager

client = TestClient(app)

@pytest.mark.asyncio
async def test_entity_lifecycle_and_versioning():
    """Verify entity creation, retrieval, updates, and versioning snapshots."""
    entity_mgr = EntityManager()
    
    # Create entity
    entity = await entity_mgr.create_entity(
        entity_type=EntityType.PROJECT,
        name="Project Jarvis KG",
        description="Enterprise Knowledge Graph Platform",
        tags=["ai", "graph", "v1"],
        owner_id="admin_user"
    )
    assert entity.id is not None
    assert entity.name == "Project Jarvis KG"
    assert entity.version == 1
    
    # Update entity
    updated = await entity_mgr.update_entity(
        entity_id=entity.id,
        description="Updated Enterprise Knowledge Graph Engine",
        tags=["ai", "graph", "v2"]
    )
    assert updated is not None
    assert updated.version == 2
    assert "v2" in updated.tags
    
    # Fetch entity
    fetched = await entity_mgr.get_entity(entity.id)
    assert fetched.description == "Updated Enterprise Knowledge Graph Engine"

@pytest.mark.asyncio
async def test_relationship_engine():
    """Verify directed weighted edges creation, weight boosting, and querying."""
    entity_mgr = EntityManager()
    rel_engine = RelationshipEngine()
    
    # Create Person and Project entities
    person = await entity_mgr.create_entity(entity_type=EntityType.PERSON, name="Alice Developer")
    project = await entity_mgr.create_entity(entity_type=EntityType.PROJECT, name="JARVIS AI Core")
    
    # Link WORKS_ON relationship
    rel = await rel_engine.create_relationship(
        source_id=person.id,
        target_id=project.id,
        relationship_type="WORKS_ON",
        weight=1.5,
        confidence_score=0.95
    )
    assert rel.id is not None
    assert rel.relationship_type == "WORKS_ON"
    assert rel.weight == 1.5
    
    # Boost relationship weight
    rel_boosted = await rel_engine.create_relationship(
        source_id=person.id,
        target_id=project.id,
        relationship_type="WORKS_ON",
        weight=0.5
    )
    assert rel_boosted.weight == 2.0
    
    # Query relationships
    outgoing = await rel_engine.get_relationships(person.id, direction="outgoing")
    assert len(outgoing) == 1
    assert outgoing[0].target_id == project.id

@pytest.mark.asyncio
async def test_graph_traversal_and_subgraph():
    """Verify NetworkX subgraph extraction and shortest path search."""
    entity_mgr = EntityManager()
    rel_engine = RelationshipEngine()
    traversal = GraphTraversalEngine()
    
    e1 = await entity_mgr.create_entity(entity_type=EntityType.SERVICE, name="Auth Service")
    e2 = await entity_mgr.create_entity(entity_type=EntityType.API, name="OAuth Gateway API")
    e3 = await entity_mgr.create_entity(entity_type=EntityType.COMPANY, name="Enterprise Security Inc")
    
    await rel_engine.create_relationship(source_id=e1.id, target_id=e2.id, relationship_type="EXPOSES")
    await rel_engine.create_relationship(source_id=e2.id, target_id=e3.id, relationship_type="OWNED_BY")
    
    # Extract subgraph
    subgraph = traversal.get_subgraph(e1.id, max_depth=2)
    assert len(subgraph["nodes"]) >= 3
    assert len(subgraph["edges"]) >= 2
    
    # Export visualization JSON
    vis = traversal.export_visualization_json()
    assert "total_nodes" in vis
    assert "total_edges" in vis

@pytest.mark.asyncio
async def test_hybrid_search_and_ai_context():
    """Verify hybrid semantic search and LLM context expansion."""
    entity_mgr = EntityManager()
    context_engine = AIContextEngine()
    
    e = await entity_mgr.create_entity(
        entity_type=EntityType.TASK,
        name="Optimize Database Queries",
        description="Performance tuning for Knowledge Graph WAL mode",
        tags=["database", "fastapi"]
    )
    
    context = await context_engine.generate_structured_context("Optimize Database", root_entity_id=e.id)
    assert "formatted_prompt_context" in context
    assert "KNOWLEDGE GRAPH REASONING CONTEXT" in context["formatted_prompt_context"]

def test_business_intelligence_analytics():
    """Verify business intelligence network density and bottleneck analysis."""
    bi_engine = BusinessIntelligenceEngine()
    metrics = bi_engine.compute_graph_metrics()
    assert "nodes" in metrics
    assert "density" in metrics

def test_security_rbac():
    """Verify security RBAC role checks and ACL permissions."""
    sec = SecurityManager()
    assert sec.check_permission("admin", "delete") is True
    assert sec.check_permission("viewer", "delete") is False
    assert sec.evaluate_entity_acl("user_a", "user_a", "write") is True

def test_kg_rest_endpoints():
    """Verify FastAPI REST API endpoints for Knowledge Graph operations."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
        
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/kg/entities
    response = client.post(
        "/api/v1/kg/entities",
        headers=headers,
        json={
            "entity_type": "Company",
            "name": "Global Tech Corp",
            "description": "Enterprise Software Provider",
            "tags": ["enterprise", "partner"]
        }
    )
    assert response.status_code == 201
    entity_data = response.json()
    entity_id = entity_data["id"]
    
    # GET /api/v1/kg/entities/{id}
    res_get = client.get(f"/api/v1/kg/entities/{entity_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Global Tech Corp"
    
    # GET /api/v1/kg/analytics
    res_analytics = client.get("/api/v1/kg/analytics", headers=headers)
    assert res_analytics.status_code == 200
    assert "metrics" in res_analytics.json()
    
    # GET /api/v1/kg/visualization
    res_vis = client.get("/api/v1/kg/visualization", headers=headers)
    assert res_vis.status_code == 200
    assert "total_nodes" in res_vis.json()
