from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Session, select
from backend.app.core.db import engine

class RelationshipRecord(SQLModel, table=True):
    __tablename__ = "kg_relationships"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source_id: UUID = Field(index=True)
    target_id: UUID = Field(index=True)
    relationship_type: str = Field(index=True)  # e.g. WORKS_ON, USES, REPORTS_TO, PURCHASED, CONNECTED_TO, BELONGS_TO
    weight: float = Field(default=1.0)
    confidence_score: float = Field(default=1.0)
    metadata_json: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RelationshipEngine:
    """Intelligent Relationship Engine managing directed weighted edges with confidence scores and updates."""

    async def create_relationship(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: str,
        weight: float = 1.0,
        confidence_score: float = 1.0,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> RelationshipRecord:
        """Establishes or boosts a relationship between source and target entities (<150ms target)."""
        with Session(engine) as session:
            statement = select(RelationshipRecord).where(
                RelationshipRecord.source_id == source_id,
                RelationshipRecord.target_id == target_id,
                RelationshipRecord.relationship_type == relationship_type
            )
            existing = session.exec(statement).first()

            if existing:
                existing.weight += weight
                existing.confidence_score = min(1.0, (existing.confidence_score + confidence_score) / 2)
                existing.updated_at = datetime.utcnow()
                if metadata_json:
                    existing.metadata_json.update(metadata_json)
                session.add(existing)
                session.commit()
                session.refresh(existing)
                return existing

            rel = RelationshipRecord(
                id=uuid4(),
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                weight=weight,
                confidence_score=confidence_score,
                metadata_json=metadata_json or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(rel)
            session.commit()
            session.refresh(rel)
            return rel

    async def get_relationships(
        self,
        entity_id: UUID,
        direction: str = "both"  # "outgoing", "incoming", or "both"
    ) -> List[RelationshipRecord]:
        """Retrieves relationships connected to an entity."""
        with Session(engine) as session:
            if direction == "outgoing":
                statement = select(RelationshipRecord).where(RelationshipRecord.source_id == entity_id)
            elif direction == "incoming":
                statement = select(RelationshipRecord).where(RelationshipRecord.target_id == entity_id)
            else:
                statement = select(RelationshipRecord).where(
                    (RelationshipRecord.source_id == entity_id) | (RelationshipRecord.target_id == entity_id)
                )
            return session.exec(statement).all()

    async def delete_relationship(self, relationship_id: UUID) -> bool:
        """Deletes a target relationship edge."""
        with Session(engine) as session:
            rel = session.get(RelationshipRecord, relationship_id)
            if not rel:
                return False
            session.delete(rel)
            session.commit()
            return True
