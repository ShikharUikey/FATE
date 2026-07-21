import os
import shutil
import subprocess
from typing import List, Dict, Any
from backend.app.tools_ecosystem.registry.manager import ToolRegistryManager
from backend.app.tools_ecosystem.registry.models import ToolCategory, ToolHealthStatus

class ToolDiscoveryEngine:
    """Auto-discovers installed local software, CLI tools, and MCP servers (<1s discovery target)."""

    def __init__(self):
        self.registry_mgr = ToolRegistryManager()

    async def run_auto_discovery(self) -> List[Dict[str, Any]]:
        """Scans host environment for binaries, tools, and MCP servers."""
        discovered = []

        # 1. Standard Developer CLI Tools
        cli_tools = [
            ("git", "Git Version Control", ToolCategory.DEV_TOOL),
            ("docker", "Docker Container Engine", ToolCategory.DEV_TOOL),
            ("code", "VS Code Editor CLI", ToolCategory.LOCAL_APP),
            ("python3", "Python Runtime", ToolCategory.DEV_TOOL),
            ("npm", "Node Package Manager", ToolCategory.DEV_TOOL),
            ("curl", "Network HTTP CLI", ToolCategory.OPERATING_SYSTEM),
            ("psql", "PostgreSQL Client", ToolCategory.DATABASE)
        ]

        for binary, desc, cat in cli_tools:
            path = shutil.which(binary)
            if path:
                tool = await self.registry_mgr.register_tool(
                    tool_id=f"cli_{binary}",
                    name=binary.capitalize(),
                    category=cat,
                    description=desc,
                    provider="local_cli",
                    capabilities=["execute_cli", "run_script"]
                )
                discovered.append({
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "path": path,
                    "status": "DISCOVERED"
                })

        # 2. macOS Application Bundles
        mac_apps = [
            ("Visual Studio Code", "vscode_app", ToolCategory.LOCAL_APP),
            ("Google Chrome", "chrome_browser", ToolCategory.BROWSER),
            ("Terminal", "mac_terminal", ToolCategory.LOCAL_APP),
            ("Docker", "docker_app", ToolCategory.DEV_TOOL),
            ("Slack", "slack_messenger", ToolCategory.COMMUNICATION),
            ("Discord", "discord_app", ToolCategory.COMMUNICATION)
        ]

        apps_dir = "/Applications"
        for app_name, tool_id, cat in mac_apps:
            app_path = os.path.join(apps_dir, f"{app_name}.app")
            if os.path.exists(app_path):
                tool = await self.registry_mgr.register_tool(
                    tool_id=tool_id,
                    name=app_name,
                    category=cat,
                    description=f"Local Application: {app_name}",
                    provider="macos_app",
                    capabilities=["gui_launch", "automation"]
                )
                discovered.append({
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "path": app_path,
                    "status": "DISCOVERED"
                })

        # 3. Builtin MCP Servers
        mcp_servers = [
            ("mcp_filesystem", "MCP FileSystem Server", ToolCategory.MCP_SERVER, ["read_file", "write_file", "list_dir"]),
            ("mcp_github", "MCP GitHub Server", ToolCategory.MCP_SERVER, ["query_issues", "create_pr", "search_repos"]),
            ("mcp_browser", "MCP Playwright Browser", ToolCategory.MCP_SERVER, ["navigate", "click", "screenshot"])
        ]

        for s_id, s_name, cat, caps in mcp_servers:
            tool = await self.registry_mgr.register_tool(
                tool_id=s_id,
                name=s_name,
                category=cat,
                description=f"Model Context Protocol Server: {s_name}",
                provider="mcp",
                capabilities=caps
            )
            discovered.append({
                "tool_id": tool.tool_id,
                "name": tool.name,
                "path": "mcp://internal",
                "status": "DISCOVERED"
            })

        return discovered
