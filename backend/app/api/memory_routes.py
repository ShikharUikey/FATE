from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from backend.app.core.security import verify_session_token
from backend.app.core.memory_graph import MemoryGraphManager
from backend.app.core.vector_db import VectorDBClient

router = APIRouter(
    prefix="/api/v1/memory",
    tags=["Memory Engine"]
)

graph_manager = MemoryGraphManager()
vector_client = VectorDBClient()

class NodeCreateRequest(BaseModel):
    name: str
    type: str

class NodeResponse(BaseModel):
    id: str
    name: str
    type: str

class LinkRequest(BaseModel):
    source_id: UUID
    target_id: UUID
    relation: str
    weight: Optional[float] = 1.0

class LinkResponse(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    relation: str
    weight: float

class ConnectionItem(BaseModel):
    target_name: str
    relation_type: str
    weight: float

class VectorSearchRequest(BaseModel):
    collection: str
    vector: List[float]
    limit: Optional[int] = 5

class VectorUpsertRequest(BaseModel):
    collection: str
    point_id: str
    vector: List[float]
    payload: Dict[str, Any]

@router.post("/node", response_model=NodeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def create_node(payload: NodeCreateRequest):
    """Creates a semantic graph node in SQLite."""
    node = await graph_manager.get_or_create_node(payload.name, payload.type)
    return NodeResponse(id=str(node.id), name=node.entity_name, type=node.entity_type)

@router.post("/edge", response_model=LinkResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_session_token)])
async def link_nodes(payload: LinkRequest):
    """Links two semantic nodes in SQLite with a directional edge."""
    try:
        edge = await graph_manager.link_nodes(
            payload.source_id, 
            payload.target_id, 
            payload.relation, 
            payload.weight or 1.0
        )
        return LinkResponse(
            edge_id=str(edge.id),
            source_id=str(edge.source_node_id),
            target_id=str(edge.target_node_id),
            relation=edge.relation_type,
            weight=edge.weight
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to link nodes: {str(e)}"
        )

@router.get("/connections", response_model=List[ConnectionItem], status_code=status.HTTP_200_OK, dependencies=[Depends(verify_session_token)])
async def get_connections(node_id: UUID):
    """Retrieves all outgoing direct links for a given node ID."""
    conns = graph_manager.query_connections(node_id)
    return [ConnectionItem(target_name=n, relation_type=r, weight=w) for n, r, w in conns]

@router.post("/search", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK, dependencies=[Depends(verify_session_token)])
async def search_vector_memories(payload: VectorSearchRequest):
    """Queries Qdrant vector database returning similar text segment payloads."""
    try:
        results = vector_client.search_similar(payload.collection, payload.vector, payload.limit or 5)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Qdrant vector query failed: {str(e)}"
        )

@router.post("/upsert", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_session_token)])
async def upsert_vector_memory(payload: VectorUpsertRequest):
    """Indexes a text chunk embedding vector into Qdrant."""
    try:
        vector_client.upsert_embedding(
            payload.collection, 
            payload.point_id, 
            payload.vector, 
            payload.payload
        )
        return {"status": "success", "point_id": payload.point_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Qdrant index operation failed: {str(e)}"
        )
