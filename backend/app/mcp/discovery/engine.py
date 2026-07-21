import shutil
import os
from typing import List, Dict, Any
from backend.app.mcp.registry.manager import MCPToolRegistryManager
from backend.app.mcp.registry.models import MCPToolCategory, MCPRiskLevel

class MCPDiscoveryEngine:
    """Auto-detects installed software, CLI binaries, cloud connections, and local MCP servers (<100ms discovery target)."""

    def __init__(self):
        self.registry_mgr = MCPToolRegistryManager()

    async def discover_all_capabilities(self) -> Dict[str, Any]:
        """Scans local operating system and environment for available tool capabilities."""
        discovered_tools = []

        # 1. Developer & OS CLI Binaries
        cli_catalog = [
            ("git", "Git VCS Control", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.LOW, ["repo_read", "commit"]),
            ("docker", "Docker Engine Manager", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.MEDIUM, ["container_exec"]),
            ("kubectl", "Kubernetes Cluster CLI", MCPToolCategory.CLOUD_SERVICES, MCPRiskLevel.HIGH, ["cluster_manage"]),
            ("aws", "AWS Cloud Services CLI", MCPToolCategory.CLOUD_SERVICES, MCPRiskLevel.HIGH, ["cloud_deploy"]),
            ("gh", "GitHub CLI", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.LOW, ["pr_manage", "issue_read"]),
            ("python3", "Python Interpreter", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.MEDIUM, ["script_exec"]),
            ("node", "Node.js JavaScript Runtime", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.MEDIUM, ["js_exec"])
        ]

        for binary, desc, category, risk, perms in cli_catalog:
            path = shutil.which(binary)
            if path:
                tool = await self.registry_mgr.register_tool(
                    tool_id=f"mcp_cli_{binary}",
                    name=f"MCP CLI: {binary}",
                    category=category,
                    description=desc,
                    risk_level=risk,
                    required_permissions=perms
                )
                discovered_tools.append({
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "type": "cli_binary",
                    "path": path
                })

        # 2. Local Applications
        local_apps = [
            ("VS Code", "vscode_ide", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.LOW),
            ("Google Chrome", "chrome_browser", MCPToolCategory.BROWSER_AUTOMATION, MCPRiskLevel.LOW),
            ("Slack", "slack_app", MCPToolCategory.COMMUNICATION, MCPRiskLevel.LOW),
            ("Postman", "postman_api", MCPToolCategory.DEVELOPER_TOOLS, MCPRiskLevel.LOW)
        ]

        for app_name, tool_id, cat, risk in local_apps:
            if os.path.exists(f"/Applications/{app_name}.app"):
                tool = await self.registry_mgr.register_tool(
                    tool_id=tool_id,
                    name=app_name,
                    category=cat,
                    description=f"Installed Desktop Application: {app_name}",
                    risk_level=risk
                )
                discovered_tools.append({
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "type": "desktop_app",
                    "path": f"/Applications/{app_name}.app"
                })

        # 3. Builtin Standard MCP Protocol Servers
        standard_servers = [
            ("mcp_server_filesystem", "MCP FileSystem Server", MCPToolCategory.OPERATING_SYSTEM, MCPRiskLevel.MEDIUM, ["fs_read", "fs_write"]),
            ("mcp_server_browser", "MCP Playwright Browser Server", MCPToolCategory.BROWSER_AUTOMATION, MCPRiskLevel.LOW, ["page_navigate", "form_fill"]),
            ("mcp_server_postgres", "MCP PostgreSQL Client Server", MCPToolCategory.DATABASES, MCPRiskLevel.HIGH, ["db_query", "table_modify"])
        ]

        for s_id, s_name, cat, risk, perms in standard_servers:
            tool = await self.registry_mgr.register_tool(
                tool_id=s_id,
                name=s_name,
                category=cat,
                description=f"Standard MCP Protocol Server: {s_name}",
                risk_level=risk,
                required_permissions=perms
            )
            discovered_tools.append({
                "tool_id": tool.tool_id,
                "name": tool.name,
                "type": "mcp_server",
                "path": "mcp://internal"
            })

        return {
            "total_discovered": len(discovered_tools),
            "tools": discovered_tools
        }
