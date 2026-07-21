import subprocess
import os
import shlex
from typing import Dict, Any, Tuple

class DesktopTerminalEngine:
    """Executes terminal commands and validates privileged/dangerous command payloads."""

    def __init__(self):
        self._command_history = []

    def validate_command(self, cmd_str: str) -> Tuple[bool, str]:
        """Validates if a command contains dangerous or privileged flags (e.g. sudo, rm -rf, chmod 777)."""
        tokens = shlex.split(cmd_str)
        if not tokens:
            return True, "OK"

        dangerous_keywords = ["sudo", "chmod", "chown", "mkfs", "dd", "shutdown", "reboot"]
        for token in tokens:
            if token.lower() in dangerous_keywords:
                return False, f"Command contains privileged keyword: '{token}'"

            # Check for rm -rf or similar wildcard deletion patterns
            if token.lower() == "rm" and any(arg.startswith("-") and "r" in arg and "f" in arg for arg in tokens):
                return False, "Command contains dangerous recursive force-delete flag: 'rm -rf'"

        return True, "OK"

    async def execute_command(self, cmd_str: str, approved: bool = False) -> Dict[str, Any]:
        """Runs a terminal command in the shell environment."""
        valid, msg = self.validate_command(cmd_str)
        
        # Block if invalid/privileged command is run without HITL approval
        if not valid and not approved:
            return {
                "status": "BLOCKED",
                "error": f"Execution blocked: {msg}. Requires explicit user approval.",
                "approved_required": True
            }

        self._command_history.append(cmd_str)
        try:
            res = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30.0
            )
            return {
                "status": "SUCCESS",
                "return_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT",
                "error": "Execution timed out (30s threshold exceeded)."
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
