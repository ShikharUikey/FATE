from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.mcp.registry.models import MCPToolRecord, MCPToolCategory, MCPRiskLevel

class MCPToolRegistryManager:
    """Manages full lifecycle CRUD, category search, and risk-level indexing for MCP tools."""

    async def register_tool(
        self,
        tool_id: str,
        name: str,
        category: MCPToolCategory,
        description: str = "",
        version: str = "1.0.0",
        developer: str = "JARVIS Core",
        risk_level: MCPRiskLevel = MCPRiskLevel.LOW,
        required_permissions: Optional[List[str]] = None,
        auth_method: str = "none",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        requires_hitl: bool = False
    ) -> MCPToolRecord:
        """Registers or updates a tool entry in the MCP tool registry (<50ms lookup target)."""
        with Session(engine) as session:
            statement = select(MCPToolRecord).where(MCPToolRecord.tool_id == tool_id)
            existing = session.exec(statement).first()

            if existing:
                existing.name = name
                existing.description = description
                existing.version = version
                existing.developer = developer
                existing.category = category
                existing.risk_level = risk_level
                existing.required_permissions = required_permissions or existing.required_permissions
                existing.auth_method = auth_method
                existing.input_schema = input_schema or existing.input_schema
                existing.output_schema = output_schema or existing.output_schema
                existing.requires_hitl = requires_hitl
                existing.updated_at = datetime.utcnow()
                session.add(existing)
                session.commit()
                session.refresh(existing)
                return existing

            tool = MCPToolRecord(
                id=uuid4(),
                tool_id=tool_id,
                name=name,
                description=description,
                version=version,
                developer=developer,
                category=category,
                risk_level=risk_level,
                required_permissions=required_permissions or [],
                auth_method=auth_method,
                input_schema=input_schema or {},
                output_schema=output_schema or {},
                health_status="HEALTHY",
                requires_hitl=requires_hitl,
                is_enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(tool)
            session.commit()
            session.refresh(tool)
            return tool

    async def get_tool(self, tool_id: str) -> Optional[MCPToolRecord]:
        """Retrieves tool definition by tool_id (<50ms lookup target)."""
        with Session(engine) as session:
            statement = select(MCPToolRecord).where(MCPToolRecord.tool_id == tool_id)
            return session.exec(statement).first()

    async def search_tools(
        self,
        query: Optional[str] = None,
        category: Optional[MCPToolCategory] = None,
        risk_level: Optional[MCPRiskLevel] = None,
        limit: int = 50
    ) -> List[MCPToolRecord]:
        """Searches tools by keyword query, category, or risk level."""
        with Session(engine) as session:
            statement = select(MCPToolRecord).where(MCPToolRecord.is_enabled == True)
            if category:
                statement = statement.where(MCPToolRecord.category == category)
            if risk_level:
                statement = statement.where(MCPToolRecord.risk_level == risk_level)
            
            results = session.exec(statement.limit(limit)).all()
            if query:
                q_lower = query.lower()
                results = [
                    r for r in results 
                    if q_lower in r.name.lower() or q_lower in r.tool_id.lower() or q_lower in r.description.lower()
                ]
            return results

    async def unregister_tool(self, tool_id: str) -> bool:
        """Unregisters tool from MCP Registry."""
        with Session(engine) as session:
            statement = select(MCPToolRecord).where(MCPToolRecord.tool_id == tool_id)
            tool = session.exec(statement).first()
            if not tool:
                return False
            session.delete(tool)
            session.commit()
            return True
