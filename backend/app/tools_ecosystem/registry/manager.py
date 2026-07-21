from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.tools_ecosystem.registry.models import ToolRecord, ToolCategory, ToolHealthStatus

class ToolRegistryManager:
    """Global Registry Manager providing CRUD, indexing, and health updates for Universal Tools."""

    async def register_tool(
        self,
        tool_id: str,
        name: str,
        category: ToolCategory,
        description: str = "",
        provider: str = "local",
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        requires_hitl: bool = False,
        permission_level: str = "standard"
    ) -> ToolRecord:
        """Registers a new tool or updates existing tool definitions."""
        with Session(engine) as session:
            statement = select(ToolRecord).where(ToolRecord.tool_id == tool_id)
            existing = session.exec(statement).first()

            if existing:
                existing.name = name
                existing.description = description
                existing.version = version
                existing.category = category
                existing.provider = provider
                existing.capabilities = capabilities or existing.capabilities
                existing.input_schema = input_schema or existing.input_schema
                existing.output_schema = output_schema or existing.output_schema
                existing.requires_hitl = requires_hitl
                existing.permission_level = permission_level
                existing.updated_at = datetime.utcnow()
                session.add(existing)
                session.commit()
                session.refresh(existing)
                return existing

            tool = ToolRecord(
                id=uuid4(),
                tool_id=tool_id,
                name=name,
                version=version,
                description=description,
                provider=provider,
                category=category,
                capabilities=capabilities or [],
                input_schema=input_schema or {},
                output_schema=output_schema or {},
                health_status=ToolHealthStatus.HEALTHY,
                requires_hitl=requires_hitl,
                permission_level=permission_level,
                is_enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(tool)
            session.commit()
            session.refresh(tool)
            return tool

    async def get_tool(self, tool_id: str) -> Optional[ToolRecord]:
        """Retrieves tool record by string tool_id (<50ms target)."""
        with Session(engine) as session:
            statement = select(ToolRecord).where(ToolRecord.tool_id == tool_id)
            return session.exec(statement).first()

    async def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        provider: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[ToolRecord]:
        """Lists registered tools with filtering options."""
        with Session(engine) as session:
            statement = select(ToolRecord)
            if category:
                statement = statement.where(ToolRecord.category == category)
            if provider:
                statement = statement.where(ToolRecord.provider == provider)
            if enabled_only:
                statement = statement.where(ToolRecord.is_enabled == True)
            return session.exec(statement).all()

    async def unregister_tool(self, tool_id: str) -> bool:
        """Removes a tool from global registry."""
        with Session(engine) as session:
            statement = select(ToolRecord).where(ToolRecord.tool_id == tool_id)
            tool = session.exec(statement).first()
            if not tool:
                return False
            session.delete(tool)
            session.commit()
            return True

    async def update_health_status(self, tool_id: str, status: ToolHealthStatus) -> Optional[ToolRecord]:
        """Updates tool health status."""
        with Session(engine) as session:
            statement = select(ToolRecord).where(ToolRecord.tool_id == tool_id)
            tool = session.exec(statement).first()
            if not tool:
                return None
            tool.health_status = status
            tool.updated_at = datetime.utcnow()
            session.add(tool)
            session.commit()
            session.refresh(tool)
            return tool
