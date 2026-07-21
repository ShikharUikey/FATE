from typing import Dict, Any, List, Optional
import json

class MCPProtocolHandler:
    """Model Context Protocol (MCP) Client/Server JSON-RPC protocol handler."""

    def format_jsonrpc_response(self, msg_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Formats standard MCP JSON-RPC 2.0 success response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }

    def format_jsonrpc_error(self, msg_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Formats standard MCP JSON-RPC 2.0 error response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def handle_mcp_message(self, message_payload: Dict[str, Any], registered_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processes incoming MCP JSON-RPC protocol messages (`tools/list`, `tools/call`, `initialize`)."""
        msg_id = message_payload.get("id")
        method = message_payload.get("method")

        if method == "initialize":
            return self.format_jsonrpc_response(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "FATE Universal MCP Engine",
                    "version": "0.1.0"
                }
            })

        elif method == "tools/list":
            mcp_tools = []
            for t in registered_tools:
                mcp_tools.append({
                    "name": t.get("tool_id"),
                    "description": t.get("description"),
                    "inputSchema": t.get("input_schema", {
                        "type": "object",
                        "properties": {}
                    })
                })
            return self.format_jsonrpc_response(msg_id, {"tools": mcp_tools})

        elif method == "tools/call":
            params = message_payload.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            return self.format_jsonrpc_response(msg_id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"Executed MCP Tool [{name}] with args: {json.dumps(args)}"
                    }
                ],
                "isError": False
            })

        else:
            return self.format_jsonrpc_error(msg_id, -32601, f"Method not found: {method}")
