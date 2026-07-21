from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session, select, text
from backend.app.core.db import engine
from backend.app.knowledge_graph.entities.models import EntityRecord, EntityVersionRecord, EntityType

class EntityManager:
    """Manages full lifecycle CRUD, versioning, and queries for Knowledge Graph entities."""

    async def create_entity(
        self,
        entity_type: EntityType,
        name: str,
        description: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        owner_id: str = "system"
    ) -> EntityRecord:
        """Creates a new knowledge entity and records version 1 history snapshot."""
        entity = EntityRecord(
            id=uuid4(),
            entity_type=entity_type,
            name=name,
            description=description,
            metadata_json=metadata_json or {},
            tags=tags or [],
            owner_id=owner_id,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        with Session(engine) as session:
            session.add(entity)
            # Create version 1 record
            version_rec = EntityVersionRecord(
                entity_id=entity.id,
                version=1,
                snapshot_data={
                    "name": entity.name,
                    "description": entity.description,
                    "metadata_json": entity.metadata_json,
                    "tags": entity.tags
                },
                changed_at=datetime.utcnow()
            )
            session.add(version_rec)
            session.commit()
            session.refresh(entity)
            return entity

    async def get_entity(self, entity_id: UUID) -> Optional[EntityRecord]:
        """Retrieves a single entity by UUID (<100ms lookup target)."""
        with Session(engine) as session:
            return session.get(EntityRecord, entity_id)

    async def update_entity(
        self,
        entity_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[EntityRecord]:
        """Updates entity fields and stores incremental version snapshot."""
        with Session(engine) as session:
            entity = session.get(EntityRecord, entity_id)
            if not entity:
                return None

            if name is not None:
                entity.name = name
            if description is not None:
                entity.description = description
            if metadata_json is not None:
                entity.metadata_json.update(metadata_json)
            if tags is not None:
                entity.tags = tags

            entity.version += 1
            entity.updated_at = datetime.utcnow()
            session.add(entity)

            # Persist new version snapshot
            version_rec = EntityVersionRecord(
                entity_id=entity.id,
                version=entity.version,
                snapshot_data={
                    "name": entity.name,
                    "description": entity.description,
                    "metadata_json": entity.metadata_json,
                    "tags": entity.tags
                },
                changed_at=datetime.utcnow()
            )
            session.add(version_rec)
            session.commit()
            session.refresh(entity)
            return entity

    async def delete_entity(self, entity_id: UUID) -> bool:
        """Deletes an entity and cleans up associated records."""
        with Session(engine) as session:
            entity = session.get(EntityRecord, entity_id)
            if not entity:
                return False
            session.delete(entity)
            # Remove version history
            statement = select(EntityVersionRecord).where(EntityVersionRecord.entity_id == entity_id)
            versions = session.exec(statement).all()
            for v in versions:
                session.delete(v)
            session.commit()
            return True

    async def list_entities(
        self,
        entity_type: Optional[EntityType] = None,
        tag: Optional[str] = None,
        owner_id: Optional[str] = None,
        limit: int = 100
    ) -> List[EntityRecord]:
        """Filters entities by entity_type, tag, or owner_id."""
        with Session(engine) as session:
            statement = select(EntityRecord)
            if entity_type:
                statement = statement.where(EntityRecord.entity_type == entity_type)
            if owner_id:
                statement = statement.where(EntityRecord.owner_id == owner_id)
            
            results = session.exec(statement.limit(limit)).all()
            if tag:
                results = [e for e in results if tag in e.tags]
            return results
