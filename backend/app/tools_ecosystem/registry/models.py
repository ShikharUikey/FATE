from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Column, JSON

class ToolCategory(str, Enum):
    LOCAL_APP = "LocalApp"
    BROWSER = "BrowserAutomation"
    OPERATING_SYSTEM = "OperatingSystem"
    DEV_TOOL = "DevelopmentTool"
    AI_PROVIDER = "AIProvider"
    PRODUCTIVITY = "Productivity"
    COMMUNICATION = "Communication"
    DATABASE = "Database"
    CLOUD = "CloudPlatform"
    IOT = "IoT"
    MCP_SERVER = "MCPServer"

class ToolHealthStatus(str, Enum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    OFFLINE = "Offline"
    UNKNOWN = "Unknown"

class ToolRecord(SQLModel, table=True):
    __tablename__ = "tools_registry"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tool_id: str = Field(index=True, unique=True)  # e.g. "vscode_editor", "mcp_github_server", "docker_cli"
    name: str = Field(index=True)
    version: str = Field(default="1.0.0")
    description: str = Field(default="")
    provider: str = Field(default="local", index=True)
    category: ToolCategory = Field(index=True)
    capabilities: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    input_schema: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_schema: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    health_status: ToolHealthStatus = Field(default=ToolHealthStatus.HEALTHY)
    requires_hitl: bool = Field(default=False)  # Human-in-the-loop approval requirement flag
    permission_level: str = Field(default="standard")  # "read", "standard", "sensitive", "admin"
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
