from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.security_engine.identity.models import IdentityRecord, IAMRole

class IdentityRegistryManager:
    """Manages identity lifecycle registry, access scopes, and agent budgets."""

    async def register_identity(
        self,
        identity_id: str,
        name: str,
        role: IAMRole,
        identity_type: str = "user",
        permissions: Optional[List[str]] = None,
        policies: Optional[Dict[str, Any]] = None,
        max_token_budget: int = 100000,
        security_level: int = 2
    ) -> IdentityRecord:
        """Registers a new identity profile in FATE's Zero Trust ecosystem."""
        with Session(engine) as session:
            statement = select(IdentityRecord).where(IdentityRecord.identity_id == identity_id)
            existing = session.exec(statement).first()

            if existing:
                existing.name = name
                existing.role = role
                existing.identity_type = identity_type
                existing.permissions = permissions or existing.permissions
                existing.policies = policies or existing.policies
                existing.max_token_budget = max_token_budget
                existing.security_level = security_level
                existing.updated_at = datetime.utcnow()
                session.add(existing)
                session.commit()
                session.refresh(existing)
                return existing

            identity = IdentityRecord(
                id=uuid4(),
                identity_id=identity_id,
                name=name,
                role=role,
                identity_type=identity_type,
                permissions=permissions or [],
                policies=policies or {},
                max_token_budget=max_token_budget,
                security_level=security_level,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(identity)
            session.commit()
            session.refresh(identity)
            return identity

    async def get_identity(self, identity_id: str) -> Optional[IdentityRecord]:
        """Retrieves identity profile by identity_id."""
        with Session(engine) as session:
            statement = select(IdentityRecord).where(IdentityRecord.identity_id == identity_id)
            return session.exec(statement).first()

    async def revoke_identity(self, identity_id: str) -> bool:
        """Deactivates an identity profile."""
        with Session(engine) as session:
            statement = select(IdentityRecord).where(IdentityRecord.identity_id == identity_id)
            identity = session.exec(statement).first()
            if not identity:
                return False
            identity.is_active = False
            identity.updated_at = datetime.utcnow()
            session.add(identity)
            session.commit()
            return True
