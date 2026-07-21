from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.mcp.registry.models import MCPPluginRecord

class MCPPluginMarketplace:
    """Manages Plugin Store catalog, verification signatures, installations & updates."""

    async def list_marketplace_plugins(self, query: Optional[str] = None) -> List[MCPPluginRecord]:
        """Lists plugins available in the marketplace catalog."""
        # Seed default verified plugins if empty
        with Session(engine) as session:
            count = len(session.exec(select(MCPPluginRecord)).all())
            if count == 0:
                defaults = [
                    MCPPluginRecord(plugin_id="plugin_github", name="GitHub Integration", author="JARVIS Team", description="Automates pull requests, issues, and commits", is_verified=True, rating=4.9),
                    MCPPluginRecord(plugin_id="plugin_jira", name="Jira Workspace Manager", author="Atlassian", description="Tracks tickets and sprint backlogs", is_verified=True, rating=4.7),
                    MCPPluginRecord(plugin_id="plugin_spotify", name="Spotify Media Controller", author="Community", description="Control music playback and playlists", is_verified=True, rating=4.5)
                ]
                for d in defaults:
                    session.add(d)
                session.commit()

            statement = select(MCPPluginRecord)
            results = session.exec(statement).all()
            if query:
                q = query.lower()
                results = [r for r in results if q in r.name.lower() or q in r.description.lower()]
            return results

    async def install_plugin(self, plugin_id: str) -> Optional[MCPPluginRecord]:
        """Installs a plugin into the local JARVIS environment."""
        with Session(engine) as session:
            statement = select(MCPPluginRecord).where(MCPPluginRecord.plugin_id == plugin_id)
            plugin = session.exec(statement).first()
            if not plugin:
                return None
            plugin.is_installed = True
            plugin.installed_at = datetime.utcnow()
            session.add(plugin)
            session.commit()
            session.refresh(plugin)
            return plugin
