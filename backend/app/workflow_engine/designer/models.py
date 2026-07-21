from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Column, JSON

class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class WorkflowRecord(SQLModel, table=True):
    __tablename__ = "workflow_records"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT)
    
    # Store workflow graph as a list of nodes and links
    nodes: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    transitions: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    
    cron_expression: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowExecutionRecord(SQLModel, table=True):
    __tablename__ = "workflow_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workflow_id: UUID = Field(index=True)
    status: WorkflowStatus = Field(default=WorkflowStatus.RUNNING)
    current_node_id: Optional[str] = Field(default=None)
    
    # Variables and outputs state
    variables: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    checkpoints: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    
    error_message: Optional[str] = Field(default=None)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
