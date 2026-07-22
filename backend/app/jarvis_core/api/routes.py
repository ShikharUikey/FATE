from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.jarvis_core.kernel.jarvis_kernel import JARVISKernel
from backend.app.jarvis_core.boot.boot_manager import SystemBootManager
from backend.app.jarvis_core.registry.module_registry import ModuleRegistryManager
from backend.app.jarvis_core.lifecycle.module_lifecycle import ModuleLifecycleManager
from backend.app.jarvis_core.scheduler.global_scheduler import GlobalTaskScheduler
from backend.app.jarvis_core.context.global_context import GlobalContextEngine
from backend.app.jarvis_core.events.kernel_event_system import KernelEventSystem
from backend.app.jarvis_core.configuration.config_manager import KernelConfigManager
from backend.app.jarvis_core.observability.kernel_observability import KernelObservabilityEngine
from backend.app.jarvis_core.plugins.plugin_loader import DynamicPluginLoader
from backend.app.jarvis_core.policy.kernel_policy_engine import KernelPolicyEngine
from backend.app.jarvis_core.security.kernel_security import KernelSecurityGuard
from backend.app.jarvis_core.backup.backup_recovery import BackupRecoveryEngine
from backend.app.jarvis_core.cli.jarvis_cli import JARVISCLI
from backend.app.jarvis_core.sdk.jarvis_sdk import JARVISSDKClient

router = APIRouter(
    prefix="/api/v1/jarvis-core",
    tags=["JARVIS Core Operating System (JARVIS Kernel)"]
)

# Managers Singletons
kernel = JARVISKernel()
boot_manager = SystemBootManager()
module_registry = ModuleRegistryManager()
lifecycle = ModuleLifecycleManager()
scheduler = GlobalTaskScheduler()
global_context = GlobalContextEngine()
kernel_events = KernelEventSystem()
config = KernelConfigManager()
observability = KernelObservabilityEngine()
plugins = DynamicPluginLoader()
policy = KernelPolicyEngine()
security = KernelSecurityGuard()
backup_engine = BackupRecoveryEngine()
cli = JARVISCLI()
sdk_client = JARVISSDKClient()

class BootPayload(BaseModel):
    boot_mode: Optional[str] = "NORMAL"

class ModuleStatePayload(BaseModel):
    module_id: str
    action: str

class ScheduleTaskPayload(BaseModel):
    task_id: str
    priority_level: Optional[str] = "HIGH"
    task_type: Optional[str] = "INTERACTIVE"

class EmitEventPayload(BaseModel):
    event_type: str
    source_module: str
    payload: Dict[str, Any]

class CLIPayload(BaseModel):
    command: str

@router.post("/boot", dependencies=[Depends(verify_session_token)])
async def execute_boot(payload: BootPayload):
    """Executes full system bootstrap flow (<10s target)."""
    return await boot_manager.execute_system_boot(boot_mode=payload.boot_mode or "NORMAL")

@router.get("/kernel/status", dependencies=[Depends(verify_session_token)])
async def get_kernel_status():
    """Queries master kernel operating status."""
    return kernel.get_kernel_status()

@router.get("/modules", dependencies=[Depends(verify_session_token)])
async def list_modules():
    """Lists registered ecosystem modules (Modules 01-19)."""
    return module_registry.list_registered_modules()

@router.post("/modules/state", dependencies=[Depends(verify_session_token)])
async def transition_module_state(payload: ModuleStatePayload):
    """Executes lifecycle action on target module (<500ms target)."""
    return await lifecycle.transition_module_state(module_id=payload.module_id, action=payload.action)

@router.post("/schedule", dependencies=[Depends(verify_session_token)])
async def schedule_task(payload: ScheduleTaskPayload):
    """Schedules task execution queue (<10ms target)."""
    return scheduler.schedule_task(
        task_id=payload.task_id,
        priority_level=payload.priority_level or "HIGH",
        task_type=payload.task_type or "INTERACTIVE"
    )

@router.get("/context", dependencies=[Depends(verify_session_token)])
async def get_unified_context():
    """Queries current global system state context."""
    return global_context.get_unified_context()

@router.post("/events/emit", dependencies=[Depends(verify_session_token)])
async def emit_kernel_event(payload: EmitEventPayload):
    """Dispatches prioritized kernel event message (<20ms target)."""
    return await kernel_events.emit_kernel_event(
        event_type=payload.event_type,
        source_module=payload.source_module,
        payload=payload.payload
    )

@router.get("/health", dependencies=[Depends(verify_session_token)])
async def get_system_health():
    """Runs platform-wide health & self-healing checks."""
    return observability.perform_system_health_audit()

@router.post("/backup", dependencies=[Depends(verify_session_token)])
async def execute_backup():
    """Triggers automated system-wide snapshot backup."""
    return await backup_engine.execute_system_backup()

@router.post("/cli", dependencies=[Depends(verify_session_token)])
async def execute_cli_command(payload: CLIPayload):
    """Executes JARVIS CLI command (status, health, modules, doctor)."""
    return cli.execute_command(payload.command)
