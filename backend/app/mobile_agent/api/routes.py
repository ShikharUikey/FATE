from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.mobile_agent.devices.manager import MobileDeviceManager
from backend.app.mobile_agent.notifications.notification_engine import MobileNotificationEngine
from backend.app.mobile_agent.automation.automation_framework import MobileAutomationFramework
from backend.app.mobile_agent.apps.app_integration import MobileAppIntegrationLayer
from backend.app.mobile_agent.sensors.sensor_engine import MobileSensorEngine
from backend.app.mobile_agent.synchronization.sync_engine import CrossDeviceSyncEngine
from backend.app.mobile_agent.security.security_guard import MobileSecurityGuard
from backend.app.mobile_agent.analytics.telemetry import MobileAnalyticsTelemetry

router = APIRouter(
    prefix="/api/v1/mobile",
    tags=["Mobile Device Agent"]
)

# Managers Singletons
device_mgr = MobileDeviceManager()
notif_engine = MobileNotificationEngine()
auto_framework = MobileAutomationFramework()
app_layer = MobileAppIntegrationLayer()
sensor_engine = MobileSensorEngine()
sync_engine = CrossDeviceSyncEngine()
security_guard = MobileSecurityGuard()
telemetry = MobileAnalyticsTelemetry()

class RegisterDeviceRequest(BaseModel):
    device_id: str
    platform: str
    model: str
    os_version: str

class PushNotificationRequest(BaseModel):
    device_id: str
    app_name: str
    title: str
    body: str
    priority: Optional[str] = "NORMAL"

class TriggerRoutineRequest(BaseModel):
    mode_name: str
    enabled: Optional[bool] = True

class SyncPayloadRequest(BaseModel):
    device_id: str
    sync_type: str
    payload: Dict[str, Any]

class RemoteWipeRequest(BaseModel):
    device_id: str
    hitl_approved: Optional[bool] = False

@router.post("/devices/register", dependencies=[Depends(verify_session_token)])
async def register_device(payload: RegisterDeviceRequest):
    """Registers mobile device in FATE ecosystem."""
    return await device_mgr.register_device(
        device_id=payload.device_id,
        platform=payload.platform,
        model=payload.model,
        os_version=payload.os_version
    )

@router.get("/devices", dependencies=[Depends(verify_session_token)])
async def list_devices():
    """Lists registered Android and iOS devices."""
    return await device_mgr.list_registered_devices()

@router.post("/notifications/push", dependencies=[Depends(verify_session_token)])
async def push_notification(payload: PushNotificationRequest):
    """Pushes notification to cross-device feed (<100ms target)."""
    return await notif_engine.push_notification(
        device_id=payload.device_id,
        app_name=payload.app_name,
        title=payload.title,
        body=payload.body,
        priority=payload.priority or "NORMAL"
    )

@router.post("/automation/routine", dependencies=[Depends(verify_session_token)])
async def trigger_routine(payload: TriggerRoutineRequest):
    """Activates mobile routine mode (driving_mode, meeting_mode, morning_routine, battery_saver)."""
    return auto_framework.trigger_routine_mode(
        mode_name=payload.mode_name,
        enabled=payload.enabled if payload.enabled is not None else True
    )

@router.get("/sensors/{device_id}", dependencies=[Depends(verify_session_token)])
async def get_sensor_telemetry(device_id: str):
    """Queries hardware sensor telemetry snapshot."""
    return sensor_engine.get_device_telemetry(device_id)

@router.post("/sync", dependencies=[Depends(verify_session_token)])
async def synchronize_payload(payload: SyncPayloadRequest):
    """Performs cross-device data synchronization (<500ms target)."""
    return await sync_engine.synchronize_payload(
        device_id=payload.device_id,
        sync_type=payload.sync_type,
        payload=payload.payload
    )

@router.post("/devices/wipe", dependencies=[Depends(verify_session_token)])
async def remote_wipe_device(payload: RemoteWipeRequest):
    """Remotely wipes a mobile device. Requires HITL approval."""
    guard_res = security_guard.evaluate_remote_wipe_permission(
        device_id=payload.device_id,
        hitl_approved=payload.hitl_approved or False
    )
    if not guard_res["allowed"]:
        return {"status": "BLOCKED", "reason": guard_res["reason"], "hitl_required": True}

    return await device_mgr.remote_wipe_device(payload.device_id, hitl_approved=True)

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics():
    """Queries mobile dashboard fleet telemetry metrics."""
    return telemetry.get_mobile_dashboard_analytics()
