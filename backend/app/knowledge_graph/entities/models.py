from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Column, JSON

class EntityType(str, Enum):
    PERSON = "Person"
    COMPANY = "Company"
    EMPLOYEE = "Employee"
    CUSTOMER = "Customer"
    TEAM = "Team"
    DEPARTMENT = "Department"
    PROJECT = "Project"
    TASK = "Task"
    MEETING = "Meeting"
    EVENT = "Event"
    NOTE = "Note"
    EMAIL = "Email"
    FILE = "File"
    API = "API"
    PRODUCT = "Product"
    SERVICE = "Service"
    WORKFLOW = "Workflow"
    AGENT = "Agent"
    PLUGIN = "Plugin"

class EntityRecord(SQLModel, table=True):
    __tablename__ = "kg_entities"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entity_type: EntityType = Field(index=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    owner_id: Optional[str] = Field(default="system", index=True)
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EntityVersionRecord(SQLModel, table=True):
    __tablename__ = "kg_entity_versions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    entity_id: UUID = Field(index=True)
    version: int = Field(index=True)
    snapshot_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    changed_at: datetime = Field(default_factory=datetime.utcnow)
