from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.desktop_os.applications.manager import DesktopApplicationManager
from backend.app.desktop_os.windows.manager import DesktopWindowManager
from backend.app.desktop_os.filesystem.engine import DesktopFileSystemEngine
from backend.app.desktop_os.terminal.engine import DesktopTerminalEngine
from backend.app.desktop_os.monitor.system_monitor import DesktopSystemMonitor
from backend.app.desktop_os.clipboard.engine import DesktopClipboardEngine
from backend.app.desktop_os.automation.framework import DesktopAutomationFramework
from backend.app.desktop_os.notifications.manager import DesktopNotificationDeviceManager
from backend.app.desktop_os.permissions.guard import DesktopSecurityGuard

router = APIRouter(
    prefix="/api/v1/desktop",
    tags=["Desktop OS Agent"]
)

# Managers Singletons
app_mgr = DesktopApplicationManager()
win_mgr = DesktopWindowManager()
fs_engine = DesktopFileSystemEngine()
term_engine = DesktopTerminalEngine()
sys_monitor = DesktopSystemMonitor()
clipboard_engine = DesktopClipboardEngine()
automation_fw = DesktopAutomationFramework()
notify_mgr = DesktopNotificationDeviceManager()
security_guard = DesktopSecurityGuard()

class LaunchAppRequest(BaseModel):
    app_name: str

class CloseAppRequest(BaseModel):
    app_name: str
    force: Optional[bool] = False
    hitl_approved: Optional[bool] = False

class MoveWindowRequest(BaseModel):
    app_id: str
    x: int
    y: int
    width: int
    height: int

class FileCreateRequest(BaseModel):
    file_path: str
    content: Optional[str] = ""

class FileDeleteRequest(BaseModel):
    file_path: str
    hitl_approved: Optional[bool] = False

class TerminalExecuteRequest(BaseModel):
    cmd_str: str
    hitl_approved: Optional[bool] = False

class ClipboardWriteRequest(BaseModel):
    text: str

class OrganizeFolderRequest(BaseModel):
    target_dir: str

class SendNotificationRequest(BaseModel):
    title: str
    subtitle: str
    message: str

@router.post("/apps/launch", dependencies=[Depends(verify_session_token)])
async def launch_app(payload: LaunchAppRequest):
    """Launches desktop application (<300ms launch target)."""
    success = await app_mgr.launch_application(payload.app_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to launch application: {payload.app_name}")
    return {"status": "SUCCESS", "message": f"Launched {payload.app_name}"}

@router.post("/apps/close", dependencies=[Depends(verify_session_token)])
async def close_app(payload: CloseAppRequest):
    """Closes desktop application. Force quit requires HITL approval."""
    guard_res = security_guard.evaluate_action_risk(
        action_type="force_quit_app" if payload.force else "close_app",
        target=payload.app_name,
        hitl_approved=payload.hitl_approved or False
    )
    if not guard_res["allowed"]:
        return {"status": "BLOCKED", "reason": guard_res["reason"], "hitl_required": True}

    success = await app_mgr.close_application(payload.app_name, force=payload.force)
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/windows/move", dependencies=[Depends(verify_session_token)])
async def move_window(payload: MoveWindowRequest):
    """Moves and resizes target application window coordinates (<100ms switch)."""
    success = await win_mgr.move_and_resize_window(
        app_id=payload.app_id,
        x=payload.x,
        y=payload.y,
        width=payload.width,
        height=payload.height
    )
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/files/create", dependencies=[Depends(verify_session_token)])
async def create_file(payload: FileCreateRequest):
    """Creates a new file in host OS."""
    success = await fs_engine.create_file(payload.file_path, content=payload.content or "")
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/files/delete", dependencies=[Depends(verify_session_token)])
async def delete_file(payload: FileDeleteRequest):
    """Deletes a file. Requires HITL approval gate."""
    guard_res = security_guard.evaluate_action_risk(
        action_type="delete_file",
        target=payload.file_path,
        hitl_approved=payload.hitl_approved or False
    )
    if not guard_res["allowed"]:
        return {"status": "BLOCKED", "reason": guard_res["reason"], "hitl_required": True}

    success = await fs_engine.delete_file(payload.file_path, approved=True)
    return {"status": "SUCCESS" if success else "FAILED"}

@router.post("/terminal/execute", dependencies=[Depends(verify_session_token)])
async def execute_command(payload: TerminalExecuteRequest):
    """Executes terminal command. Dangerous command sequences require HITL approval."""
    return await term_engine.execute_command(payload.cmd_str, approved=payload.hitl_approved or False)

@router.get("/monitor/telemetry", dependencies=[Depends(verify_session_token)])
async def get_system_telemetry():
    """Queries real-time system metrics (CPU, RAM, Disk)."""
    return sys_monitor.get_system_telemetry()

@router.post("/clipboard/write", dependencies=[Depends(verify_session_token)])
async def write_clipboard(payload: ClipboardWriteRequest):
    """Writes text string into clipboard cache."""
    success = clipboard_engine.write_clipboard(payload.text)
    return {"status": "SUCCESS" if success else "FAILED"}

@router.get("/clipboard/read", dependencies=[Depends(verify_session_token)])
async def read_clipboard():
    """Reads current clipboard text contents."""
    return {"content": clipboard_engine.read_clipboard()}

@router.post("/automation/organize", dependencies=[Depends(verify_session_token)])
async def organize_folder(payload: OrganizeFolderRequest):
    """Triggers extension-specific folder organizer automation."""
    return await automation_fw.organize_folder(payload.target_dir)

@router.post("/notifications/send", dependencies=[Depends(verify_session_token)])
async def send_notification(payload: SendNotificationRequest):
    """Sends desktop notification popup banner."""
    success = await notify_mgr.send_notification(
        title=payload.title,
        subtitle=payload.subtitle,
        message=payload.message
    )
    return {"status": "SUCCESS" if success else "FAILED"}
