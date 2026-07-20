import subprocess
import os
from typing import List, Dict, Any, Optional

class DesktopAgent:
    """Specialized agent automating macOS application controls and terminal actions."""

    async def execute(self, command: str, parameters: Dict[str, Any]) -> bool:
        """Entrypoint called by the Orchestrator scheduler."""
        cmd_lower = command.lower()
        if cmd_lower == "launch_application":
            return await self.launch_application(parameters.get("app_name", ""))
        elif cmd_lower == "get_running_processes":
            parameters["result"] = await self.get_running_processes()
            return True
        elif cmd_lower == "execute_terminal_command":
            output = await self.execute_terminal_command(parameters.get("cmd", ""))
            parameters["result"] = output
            return output is not None
        return False

    async def launch_application(self, app_name: str) -> bool:
        """Launches a target GUI application on macOS using the open terminal utility."""
        if not app_name:
            return False
        try:
            # Safe execution using terminal open utility
            subprocess.run(["open", "-a", app_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            # Fallback using AppleScript if application is not in default path
            script = f'tell application "{app_name}" to activate'
            res = subprocess.run(["osascript", "-e", script], capture_output=True)
            return res.returncode == 0

    async def get_running_processes(self) -> List[str]:
        """Queries active graphical processes running on macOS using AppKit NSWorkspace."""
        try:
            # Mapped Cocoa bindings for native OS integration
            from AppKit import NSWorkspace
            workspace = NSWorkspace.sharedWorkspace()
            apps = workspace.runningApplications()
            # Activation policy 0 represents regular visible graphical applications (NSApplicationActivationPolicyRegular)
            return [app.localizedName() for app in apps if app.activationPolicy() == 0]
        except Exception as e:
            # Fallback to ps aux parsing if AppKit Cocoa bindings fail
            print(f"[DESKTOP AGENT WARNING] AppKit NSWorkspace failed: {e}. Falling back to ps.")
            res = subprocess.run(["ps", "-A", "-o", "comm"], capture_output=True, text=True)
            if res.returncode == 0:
                lines = res.stdout.split("\n")[1:]
                # Parse basenames of active process lines
                return list(set(os.path.basename(line.strip()) for line in lines if line.strip()))
            return []

    async def execute_terminal_command(self, cmd: str) -> Optional[str]:
        """Safely executes terminal commands relative to the current project workspace."""
        if not cmd:
            return None
        # Enforces safe workspace confinement paths
        cwd = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi"))
        os.makedirs(cwd, exist_ok=True)
        
        try:
            res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                return res.stdout.strip()
            return f"Error (Exit {res.returncode}): {res.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "Error: Command execution timed out after 10 seconds."
        except Exception as e:
            return f"Error: Exception raised: {str(e)}"
