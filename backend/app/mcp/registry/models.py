from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field, Column, JSON

class MCPRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MCPToolCategory(str, Enum):
    OPERATING_SYSTEM = "OperatingSystem"
    DEVELOPER_TOOLS = "DeveloperTools"
    PRODUCTIVITY = "Productivity"
    COMMUNICATION = "Communication"
    CLOUD_SERVICES = "CloudServices"
    AI_SERVICES = "AIServices"
    DATABASES = "Databases"
    BROWSER_AUTOMATION = "BrowserAutomation"
    IOT_DEVICES = "IoTDevices"
    CUSTOM_PLUGIN = "CustomPlugin"

class MCPToolRecord(SQLModel, table=True):
    __tablename__ = "mcp_tools_registry"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tool_id: str = Field(index=True, unique=True)
    name: str = Field(index=True)
    description: str = Field(default="")
    version: str = Field(default="1.0.0")
    developer: str = Field(default="JARVIS Core")
    category: MCPToolCategory = Field(index=True)
    risk_level: MCPRiskLevel = Field(default=MCPRiskLevel.LOW)
    required_permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    auth_method: str = Field(default="none")  # "none", "api_key", "oauth2", "jwt"
    input_schema: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_schema: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    health_status: str = Field(default="HEALTHY")
    requires_hitl: bool = Field(default=False)
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MCPPluginRecord(SQLModel, table=True):
    __tablename__ = "mcp_plugins"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    plugin_id: str = Field(index=True, unique=True)
    name: str = Field(index=True)
    version: str = Field(default="1.0.0")
    author: str = Field(default="Community")
    description: str = Field(default="")
    is_verified: bool = Field(default=True)
    is_installed: bool = Field(default=False)
    dependencies: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    rating: float = Field(default=5.0)
    installed_at: Optional[datetime] = Field(default=None)
