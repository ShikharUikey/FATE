from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Column, JSON

class IAMRole(str, Enum):
    OWNER = "Owner"
    ADMINISTRATOR = "Administrator"
    DEVELOPER = "Developer"
    OPERATOR = "Operator"
    VIEWER = "Viewer"
    GUEST = "Guest"

class IdentityRecord(SQLModel, table=True):
    __tablename__ = "iam_identities"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    identity_id: str = Field(index=True, unique=True)  # e.g., "user_siddharth", "agent_orchestrator", "service_db"
    name: str = Field(index=True)
    role: IAMRole = Field(default=IAMRole.OPERATOR)
    identity_type: str = Field(default="user")  # "user", "agent", "service", "plugin"
    permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    policies: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    max_token_budget: int = Field(default=100000)
    security_level: int = Field(default=2)  # 1 to 4 privilege levels
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AuditRecord(SQLModel, table=True):
    __tablename__ = "security_audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(index=True)
    agent_id: Optional[str] = Field(default=None, index=True)
    tool_id: Optional[str] = Field(default=None)
    action: str = Field(index=True)
    arguments_json: str = Field(default="{}")
    result: str = Field(default="SUCCESS")
    risk_score: float = Field(default=0.0)
    hitl_approved: bool = Field(default=False)
    duration_ms: int = Field(default=0)
    device_id: Optional[str] = Field(default=None)
