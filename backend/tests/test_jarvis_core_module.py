import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
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

client = TestClient(app)

@pytest.mark.asyncio
async def test_system_boot_manager():
    """Verify ordered 12-step boot process (<10s target)."""
    boot = SystemBootManager()
    res = await boot.execute_system_boot(boot_mode="NORMAL")
    
    assert res["status"] == "SYSTEM_READY"
    assert res["boot_time_seconds"] < 10.0
    assert res["total_steps_executed"] == 12

def test_jarvis_kernel():
    """Verify master kernel status and SLA metrics."""
    kernel = JARVISKernel()
    status = kernel.get_kernel_status()
    assert status["status"] == "ONLINE"
    assert status["managed_modules_count"] == 19

@pytest.mark.asyncio
async def test_module_registry_and_lifecycle():
    """Verify listing Modules 01-19 and lifecycle state transitions (<500ms target)."""
    reg = ModuleRegistryManager()
    modules = reg.list_registered_modules()
    assert len(modules) == 19
    
    lifecycle = ModuleLifecycleManager()
    trans = await lifecycle.transition_module_state("mod_02_brain", "RESTART")
    assert trans["status"] == "SUCCESS"
    assert trans["latency_ms"] < 500.0

def test_global_task_scheduler():
    """Verify task scheduler queue latency (<10ms target)."""
    scheduler = GlobalTaskScheduler()
    res = scheduler.schedule_task("task_001", priority_level="CRITICAL", task_type="INTERACTIVE")
    
    assert res["status"] == "SCHEDULED"
    assert res["scheduling_latency_ms"] < 10.0

def test_global_context_engine():
    """Verify unified cross-module global context retrieval."""
    ctx_engine = GlobalContextEngine()
    ctx = ctx_engine.get_unified_context()
    assert ctx["current_user"] == "Siddharth Uikey"
    assert ctx["active_agents_count"] > 0

@pytest.mark.asyncio
async def test_kernel_event_system():
    """Verify inter-module event bus routing (<20ms latency target)."""
    events = KernelEventSystem()
    res = await events.emit_kernel_event("MODULE_HEALTH_ALERT", "mod_14_cloud", {"cpu": 95})
    
    assert res["status"] == "DISPATCHED"
    assert res["latency_ms"] < 20.0

def test_kernel_observability_and_security():
    """Verify platform health audit and secure module verification."""
    observability = KernelObservabilityEngine()
    audit = observability.perform_system_health_audit()
    assert audit["overall_status"] == "HEALTHY"
    assert audit["active_modules_healthy_count"] == 19
    
    sec = KernelSecurityGuard()
    assert sec.verify_module_signature("mod_01_core") is True

def test_jarvis_cli_and_sdk():
    """Verify JARVIS CLI command execution and Python SDK client."""
    cli = JARVISCLI()
    res_status = cli.execute_command("status")
    assert "ONLINE" in res_status["output"]
    
    res_doc = cli.execute_command("doctor")
    assert "Doctor Diagnostics" in res_doc["output"]
    
    sdk = JARVISSDKClient()
    ping = sdk.ping_kernel()
    assert ping["status"] == "PONG"

def test_jarvis_core_rest_endpoints():
    """Verify FastAPI REST API endpoints for JARVIS Core OS Kernel."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/jarvis-core/boot
    res_boot = client.post("/api/v1/jarvis-core/boot", headers=headers, json={"boot_mode": "NORMAL"})
    assert res_boot.status_code == 200
    assert res_boot.json()["status"] == "SYSTEM_READY"
    
    # GET /api/v1/jarvis-core/kernel/status
    res_ks = client.get("/api/v1/jarvis-core/kernel/status", headers=headers)
    assert res_ks.status_code == 200
    assert res_ks.json()["managed_modules_count"] == 19
    
    # GET /api/v1/jarvis-core/modules
    res_mods = client.get("/api/v1/jarvis-core/modules", headers=headers)
    assert res_mods.status_code == 200
    assert len(res_mods.json()) == 19
    
    # POST /api/v1/jarvis-core/cli
    res_cli = client.post("/api/v1/jarvis-core/cli", headers=headers, json={"command": "doctor"})
    assert res_cli.status_code == 200
    assert "Doctor Diagnostics" in res_cli.json()["output"]
