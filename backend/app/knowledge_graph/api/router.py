from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.app.core.security import verify_session_token
from backend.app.knowledge_graph.entities.models import EntityType, EntityRecord
from backend.app.knowledge_graph.entities.manager import EntityManager
from backend.app.knowledge_graph.relationships.engine import RelationshipEngine
from backend.app.knowledge_graph.graph_engine.traversal import GraphTraversalEngine
from backend.app.knowledge_graph.semantic_search.hybrid_search import HybridSearchEngine
from backend.app.knowledge_graph.ai.context_engine import AIContextEngine
from backend.app.knowledge_graph.analytics.business_intel import BusinessIntelligenceEngine
from backend.app.knowledge_graph.ai.resolution import EntityResolutionEngine

router = APIRouter(
    prefix="/api/v1/kg",
    tags=["Knowledge Graph Engine"]
)

# Managers Singletons
entity_mgr = EntityManager()
rel_engine = RelationshipEngine()
traversal_engine = GraphTraversalEngine()
search_engine = HybridSearchEngine()
context_engine = AIContextEngine()
bi_engine = BusinessIntelligenceEngine()
resolution_engine = EntityResolutionEngine()

class CreateEntityRequest(BaseModel):
    entity_type: EntityType
    name: str
    description: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[str] = "system"

class CreateRelationshipRequest(BaseModel):
    source_id: UUID
    target_id: UUID
    relationship_type: str
    weight: Optional[float] = 1.0
    confidence_score: Optional[float] = 1.0
    metadata_json: Optional[Dict[str, Any]] = None

class ContextRequest(BaseModel):
    query: str
    root_entity_id: Optional[UUID] = None
    max_hops: Optional[int] = 2

@router.post("/entities", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def create_entity(payload: CreateEntityRequest):
    """Creates a new Knowledge Graph entity record."""
    return await entity_mgr.create_entity(
        entity_type=payload.entity_type,
        name=payload.name,
        description=payload.description,
        metadata_json=payload.metadata_json,
        tags=payload.tags,
        owner_id=payload.owner_id or "system"
    )

@router.get("/entities/{entity_id}", dependencies=[Depends(verify_session_token)])
async def get_entity(entity_id: UUID):
    """Retrieves an entity by UUID (<100ms lookup target)."""
    entity = await entity_mgr.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.get("/entities", dependencies=[Depends(verify_session_token)])
async def list_entities(
    entity_type: Optional[EntityType] = Query(None),
    tag: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """Filters and lists Knowledge Graph entities."""
    return await entity_mgr.list_entities(entity_type=entity_type, tag=tag, limit=limit)

@router.post("/relationships", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def create_relationship(payload: CreateRelationshipRequest):
    """Establishes or updates a directional weighted relationship between entities."""
    return await rel_engine.create_relationship(
        source_id=payload.source_id,
        target_id=payload.target_id,
        relationship_type=payload.relationship_type,
        weight=payload.weight or 1.0,
        confidence_score=payload.confidence_score or 1.0,
        metadata_json=payload.metadata_json
    )

@router.get("/relationships/{entity_id}", dependencies=[Depends(verify_session_token)])
async def get_relationships(entity_id: UUID, direction: str = Query("both")):
    """Queries directional edges connected to an entity."""
    return await rel_engine.get_relationships(entity_id, direction=direction)

@router.get("/search", dependencies=[Depends(verify_session_token)])
async def hybrid_semantic_search(query: str, limit: int = Query(10, le=50)):
    """Executes hybrid vector + graph semantic search (<300ms target)."""
    return await search_engine.search(query, limit=limit)

@router.post("/context", dependencies=[Depends(verify_session_token)])
async def generate_ai_context(payload: ContextRequest):
    """Generates structured Knowledge Graph reasoning context for LLM prompts."""
    return await context_engine.generate_structured_context(
        query=payload.query,
        root_entity_id=payload.root_entity_id,
        max_hops=payload.max_hops or 2
    )

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_graph_analytics():
    """Returns network density, bottleneck analysis, and collaboration metrics."""
    metrics = bi_engine.compute_graph_metrics()
    bottlenecks = bi_engine.discover_project_bottlenecks()
    return {
        "metrics": metrics,
        "bottlenecks": bottlenecks
    }

@router.get("/visualization", dependencies=[Depends(verify_session_token)])
async def get_visualization_data():
    """Exports graph nodes and edges JSON for D3/vis.js interactive visualizers (<2s target)."""
    return traversal_engine.export_visualization_json()

@router.get("/resolution/duplicates", dependencies=[Depends(verify_session_token)])
async def detect_duplicates():
    """Scans Knowledge Graph to discover potential duplicate entities."""
    return await resolution_engine.detect_duplicates()
