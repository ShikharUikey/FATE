import json
from uuid import uuid4
from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session
from backend.app.core.db import engine
from backend.app.security_engine.identity.models import AuditRecord

class ImmutableAuditLogger:
    """Immutable audit logging recorder mapping FATE operations and security parameters."""

    async def log_security_event(
        self,
        user_id: str,
        action: str,
        agent_id: Optional[str] = None,
        tool_id: Optional[str] = None,
        arguments: Optional[Dict[str, Any]] = None,
        result: str = "SUCCESS",
        risk_score: float = 0.0,
        hitl_approved: bool = False,
        duration_ms: int = 0,
        device_id: Optional[str] = None
    ) -> AuditRecord:
        """Saves a write-once immutable audit record in SQLite WAL database."""
        record = AuditRecord(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            agent_id=agent_id,
            tool_id=tool_id,
            action=action,
            arguments_json=json.dumps(arguments or {}),
            result=result,
            risk_score=risk_score,
            hitl_approved=hitl_approved,
            duration_ms=duration_ms,
            device_id=device_id
        )

        with Session(engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
