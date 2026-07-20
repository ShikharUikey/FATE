from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.core.write_manager import write_manager
from backend.app.models.schemas import MemoryNodes, MemoryEdges

class MemoryGraphManager:
    """Manager for FATE's semantic node-edge graph persistence in SQLite."""

    async def get_or_create_node(self, entity_name: str, entity_type: str) -> MemoryNodes:
        """Retrieves an existing node or instantiates a new node in SQLite WAL."""
        with Session(engine) as session:
            statement = select(MemoryNodes).where(
                MemoryNodes.entity_name == entity_name,
                MemoryNodes.entity_type == entity_type
            )
            node = session.exec(statement).first()
            
        if node:
            return node
            
        new_node = MemoryNodes(
            id=uuid4(),
            entity_name=entity_name,
            entity_type=entity_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await write_manager.execute_write(new_node)
        return new_node

    async def link_nodes(self, source_id: UUID, target_id: UUID, relation: str, weight: float = 1.0) -> MemoryEdges:
        """Establishes or updates a weighted directional edge link between two nodes."""
        with Session(engine) as session:
            statement = select(MemoryEdges).where(
                MemoryEdges.source_node_id == source_id,
                MemoryEdges.target_node_id == target_id,
                MemoryEdges.relation_type == relation
            )
            edge = session.exec(statement).first()
            
        if edge:
            # Boost the relation weight if observation is repeated
            edge.weight = max(edge.weight, weight)
            edge.updated_at = datetime.utcnow()
            await write_manager.execute_write(edge)
            return edge
            
        new_edge = MemoryEdges(
            id=uuid4(),
            source_node_id=source_id,
            target_node_id=target_id,
            relation_type=relation,
            weight=weight,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await write_manager.execute_write(new_edge)
        return new_edge

    def query_connections(self, node_id: UUID) -> List[Tuple[str, str, float]]:
        """Queries SQLite returning all direct neighbors, relation types, and edge weights."""
        with Session(engine) as session:
            # Query outgoing links
            statement = select(MemoryEdges, MemoryNodes).join(
                MemoryNodes, MemoryEdges.target_node_id == MemoryNodes.id
            ).where(MemoryEdges.source_node_id == node_id)
            
            results = session.exec(statement).all()
            connections = []
            for edge, node in results:
                connections.append((node.entity_name, edge.relation_type, edge.weight))
            return connections
