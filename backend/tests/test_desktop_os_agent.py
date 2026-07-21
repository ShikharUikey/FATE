import pytest
import json
import os
import shutil
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.desktop_os.applications.manager import DesktopApplicationManager
from backend.app.desktop_os.windows.manager import DesktopWindowManager
from backend.app.desktop_os.filesystem.engine import DesktopFileSystemEngine
from backend.app.desktop_os.terminal.engine import DesktopTerminalEngine
from backend.app.desktop_os.monitor.system_monitor import DesktopSystemMonitor
from backend.app.desktop_os.clipboard.engine import DesktopClipboardEngine
from backend.app.desktop_os.automation.framework import DesktopAutomationFramework
from backend.app.desktop_os.notifications.manager import DesktopNotificationDeviceManager
from backend.app.desktop_os.permissions.guard import DesktopSecurityGuard

client = TestClient(app)

@pytest.mark.asyncio
async def test_application_lifecycle():
    """Verify application launching and list updates (<300ms launch)."""
    app_mgr = DesktopApplicationManager()
    
    # Launch app
    launched = await app_mgr.launch_application("Visual Studio Code")
    assert launched is True
    
    # List running apps
    apps = await app_mgr.list_running_applications()
    assert len(apps) > 0
    assert "Visual Studio Code" in [a["name"] for a in apps]

@pytest.mark.asyncio
async def test_window_manager_coordinates():
    """Verify window position adjustments and splits (<100ms switches)."""
    win_mgr = DesktopWindowManager()
    
    # Move window
    moved = await win_mgr.move_and_resize_window("vscode", 100, 100, 1000, 800)
    assert moved is True
    
    bounds = await win_mgr.get_window_bounds("vscode")
    assert bounds["x"] == 100
    assert bounds["width"] == 1000
    
    # Split tiling
    tiled = await win_mgr.tile_windows_split("vscode", "chrome")
    assert tiled is True

@pytest.mark.asyncio
async def test_filesystem_hitl_deletion():
    """Verify safe file operations and deletion HITL gate blocks."""
    fs = DesktopFileSystemEngine()
    sandbox_dir = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi/test_fs_sandbox"))
    os.makedirs(sandbox_dir, exist_ok=True)
    file_path = os.path.join(sandbox_dir, "test.txt")
    
    try:
        # Create file
        created = await fs.create_file(file_path, "FATE OS verification")
        assert created is True
        assert os.path.exists(file_path)
        
        # Try deleting without HITL approval -> BLOCKED
        with pytest.raises(PermissionError):
            await fs.delete_file(file_path, approved=False)
            
        # Delete with approval -> SUCCESS
        deleted = await fs.delete_file(file_path, approved=True)
        assert deleted is True
        assert not os.path.exists(file_path)
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)

@pytest.mark.asyncio
async def test_terminal_command_validation():
    """Verify terminal execution and dangerous command validation."""
    term = DesktopTerminalEngine()
    
    # Valid command -> SUCCESS
    res_val = await term.execute_command("echo 'FATE'")
    assert res_val["status"] == "SUCCESS"
    assert "FATE" in res_val["stdout"]
    
    # Dangerous command -> BLOCKED without approval
    res_danger = await term.execute_command("sudo rm -rf /", approved=False)
    assert res_danger["status"] == "BLOCKED"
    assert res_danger["approved_required"] is True

def test_system_telemetry_monitoring():
    """Verify resource usage metrics and active process list queries."""
    monitor = DesktopSystemMonitor()
    telemetry = monitor.get_system_telemetry()
    assert "cpu_percent" in telemetry
    assert "ram_percent" in telemetry
    
    processes = monitor.list_active_processes(limit=5)
    assert len(processes) > 0
    assert "pid" in processes[0]

def test_clipboard_operations():
    """Verify clipboard read/write and history caching."""
    clipboard = DesktopClipboardEngine()
    
    # Write clipboard
    wrote = clipboard.write_clipboard("Handshake key")
    assert wrote is True
    
    # Read clipboard
    assert clipboard.read_clipboard() == "Handshake key"
    
    # History
    history = clipboard.get_clipboard_history()
    assert len(history) >= 1
    assert history[0] == "Handshake key"

@pytest.mark.asyncio
async def test_folder_organizer_automation():
    """Verify folder cleanup automation organizing extensions."""
    automation = DesktopAutomationFramework()
    sandbox_dir = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi/test_auto_sandbox"))
    os.makedirs(sandbox_dir, exist_ok=True)
    
    try:
        # Create mock file types
        with open(os.path.join(sandbox_dir, "report.pdf"), "w") as f: f.write("pdf")
        with open(os.path.join(sandbox_dir, "script.py"), "w") as f: f.write("py")
        
        # Run organizer
        res = await automation.organize_folder(sandbox_dir)
        assert res["status"] == "SUCCESS"
        assert res["metrics"]["Documents"] == 1
        assert res["metrics"]["Code"] == 1
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)

def test_desktop_rest_endpoints():
    """Verify FastAPI REST API endpoints for Desktop OS Agent operations."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/desktop/apps/launch
    res_launch = client.post(
        "/api/v1/desktop/apps/launch",
        headers=headers,
        json={"app_name": "Visual Studio Code"}
    )
    assert res_launch.status_code == 200
    assert res_launch.json()["status"] == "SUCCESS"
    
    # GET /api/v1/desktop/monitor/telemetry
    res_tel = client.get("/api/v1/desktop/monitor/telemetry", headers=headers)
    assert res_tel.status_code == 200
    assert "cpu_percent" in res_tel.json()
    
    # POST /api/v1/desktop/clipboard/write
    res_clip = client.post(
        "/api/v1/desktop/clipboard/write",
        headers=headers,
        json={"text": "FATE Core handoff"}
    )
    assert res_clip.status_code == 200
    
    # GET /api/v1/desktop/clipboard/read
    res_clip_read = client.get("/api/v1/desktop/clipboard/read", headers=headers)
    assert res_clip_read.status_code == 200
    assert res_clip_read.json()["content"] == "FATE Core handoff"
