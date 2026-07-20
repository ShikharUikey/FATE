from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class CoreSettings(SQLModel, table=True):
    __tablename__ = "core_settings"
    key: str = Field(primary_key=True, max_length=255, index=True)
    value: str = Field(nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class RegisteredPlugins(SQLModel, table=True):
    __tablename__ = "registered_plugins"
    id: str = Field(primary_key=True, max_length=100, index=True)
    name: str = Field(nullable=False, max_length=255)
    version: str = Field(nullable=False, max_length=50)
    manifest_hash: str = Field(nullable=False, max_length=64)
    is_enabled: bool = Field(default=True, nullable=False)
    permissions: str = Field(nullable=False)  # JSON-serialized array
    settings: str = Field(default="{}", nullable=False)  # JSON-serialized key-value
    installed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class TaskQueue(SQLModel, table=True):
    __tablename__ = "task_queue"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    plan_id: UUID = Field(nullable=False, index=True)
    agent_name: str = Field(nullable=False, max_length=100)
    command: str = Field(nullable=False, max_length=255)
    parameters: str = Field(default="{}", nullable=False)  # JSON arguments
    status: str = Field(default="Pending", nullable=False, max_length=50, index=True)
    priority: str = Field(default="Normal", nullable=False, max_length=50)
    retry_count: int = Field(default=0, nullable=False)
    dependencies: str = Field(default="[]", nullable=False)  # JSON array of task UUIDs
    error_message: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    started_at: Optional[datetime] = Field(default=None, nullable=True)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

class MemoryNodes(SQLModel, table=True):
    __tablename__ = "memory_nodes"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    entity_name: str = Field(nullable=False, max_length=255, index=True)
    entity_type: str = Field(nullable=False, max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class MemoryEdges(SQLModel, table=True):
    __tablename__ = "memory_edges"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    source_node_id: UUID = Field(foreign_key="memory_nodes.id", nullable=False, index=True)
    target_node_id: UUID = Field(foreign_key="memory_nodes.id", nullable=False, index=True)
    relation_type: str = Field(nullable=False, max_length=100, index=True)
    weight: float = Field(default=1.0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class MemoryObservations(SQLModel, table=True):
    __tablename__ = "memory_observations"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    raw_text: str = Field(nullable=False)
    source: str = Field(default="user", nullable=False, max_length=100)
    importance_score: int = Field(default=1, nullable=False, index=True)
    embedding_id: str = Field(nullable=False, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class ExecutionTraces(SQLModel, table=True):
    __tablename__ = "execution_traces"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_query: str = Field(nullable=False)
    plan_dag: str = Field(nullable=False)  # JSON DAG
    outcome: str = Field(nullable=False, max_length=100, index=True)
    total_latency_ms: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

class AuditLogs(SQLModel, table=True):
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    trace_id: UUID = Field(foreign_key="execution_traces.id", nullable=False, index=True)
    actor: str = Field(nullable=False, max_length=100, index=True)
    action: str = Field(nullable=False, max_length=255)
    target_resource: str = Field(nullable=False, max_length=512)
    status: str = Field(nullable=False, max_length=50, index=True)
    details: Optional[str] = Field(default=None, nullable=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
