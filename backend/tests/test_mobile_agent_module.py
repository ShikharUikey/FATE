import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.mobile_agent.devices.manager import MobileDeviceManager
from backend.app.mobile_agent.notifications.notification_engine import MobileNotificationEngine
from backend.app.mobile_agent.automation.automation_framework import MobileAutomationFramework
from backend.app.mobile_agent.apps.app_integration import MobileAppIntegrationLayer
from backend.app.mobile_agent.sensors.sensor_engine import MobileSensorEngine
from backend.app.mobile_agent.synchronization.sync_engine import CrossDeviceSyncEngine
from backend.app.mobile_agent.security.security_guard import MobileSecurityGuard
from backend.app.mobile_agent.analytics.telemetry import MobileAnalyticsTelemetry

client = TestClient(app)

@pytest.mark.asyncio
async def test_mobile_device_registry():
    """Verify device registration, lock, and remote wipe HITL approval gating."""
    mgr = MobileDeviceManager()
    dev = await mgr.register_device("dev_test_01", "Android", "Pixel 9", "Android 15")
    
    assert dev["device_id"] == "dev_test_01"
    assert dev["platform"] == "Android"
    
    # Remote lock
    locked = await mgr.lock_device("dev_test_01")
    assert locked is True
    
    # Remote wipe without approval -> BLOCKED
    wipe_blocked = await mgr.remote_wipe_device("dev_test_01", hitl_approved=False)
    assert wipe_blocked["status"] == "BLOCKED"
    assert wipe_blocked["hitl_required"] is True
    
    # Remote wipe with approval -> WIPED
    wipe_ok = await mgr.remote_wipe_device("dev_test_01", hitl_approved=True)
    assert wipe_ok["status"] == "WIPED"

@pytest.mark.asyncio
async def test_mobile_notification_engine():
    """Verify cross-device notification sync (<100ms delivery target) and AI response suggestions."""
    notif = MobileNotificationEngine()
    res = await notif.push_notification(
        device_id="dev_ios_01",
        app_name="WhatsApp",
        title="Alex",
        body="Are you free for a meeting today?",
        priority="HIGH"
    )
    assert res["status"] == "DELIVERED"
    assert res["delivery_time_ms"] >= 0
    assert len(res["notification"]["suggested_replies"]) > 0

def test_mobile_automation_framework():
    """Verify driving/meeting mode triggers and geofence distance calculation."""
    auto = MobileAutomationFramework()
    
    # Driving mode trigger
    res_driving = auto.trigger_routine_mode("driving_mode", enabled=True)
    assert res_driving["status"] == "ACTIVATED"
    assert res_driving["profile_config"]["do_not_disturb"] is True
    
    # Geofence boundary evaluation
    geofence = auto.evaluate_geofence_trigger(28.6139, 77.2090, 28.6139, 77.2090, radius_meters=50.0)
    assert geofence["inside_geofence"] is True

@pytest.mark.asyncio
async def test_mobile_app_integration():
    """Verify contacts query, SMS dispatch, and reminder creation."""
    apps = MobileAppIntegrationLayer()
    
    contacts = await apps.get_contacts(query="Siddharth")
    assert len(contacts) == 1
    
    sms_res = await apps.send_sms_message("+919876543210", "Testing FATE Mobile Sync")
    assert sms_res["status"] == "SENT"
    
    rem_res = await apps.create_reminder("Review Mobile Code", "2026-07-22T18:00:00Z")
    assert rem_res["status"] == "CREATED"

def test_mobile_sensor_engine():
    """Verify hardware sensor telemetry snapshot (GPS, battery, motion state)."""
    sensors = MobileSensorEngine()
    telemetry = sensors.get_device_telemetry("dev_android_01")
    
    assert telemetry["device_id"] == "dev_android_01"
    assert "gps_location" in telemetry
    assert "battery" in telemetry

@pytest.mark.asyncio
async def test_cross_device_sync_engine():
    """Verify two-way data sync across desktop and mobile devices (<500ms sync target)."""
    sync = CrossDeviceSyncEngine()
    res = await sync.synchronize_payload(
        device_id="dev_ios_01",
        sync_type="clipboard",
        payload={"text": "Cross-device clipboard content"}
    )
    assert res["status"] == "SUCCESS"
    assert res["sync_duration_ms"] >= 0
    
    history = await sync.get_sync_history()
    assert len(history) == 1

def test_mobile_security_guard():
    """Verify biometric token validation and remote wipe security checks."""
    guard = MobileSecurityGuard()
    
    assert guard.verify_biometric_token("bio_valid_9921") is True
    assert guard.verify_biometric_token("invalid_token") is False
    
    wipe_perm = guard.evaluate_remote_wipe_permission("dev_android_01", hitl_approved=False)
    assert wipe_perm["allowed"] is False
    assert wipe_perm["hitl_required"] is True

def test_mobile_analytics():
    """Verify mobile dashboard telemetry metrics aggregation."""
    analytics = MobileAnalyticsTelemetry()
    summary = analytics.get_mobile_dashboard_analytics()
    
    assert summary["registered_devices_count"] == 2
    assert "sync_success_rate_percent" in summary

def test_mobile_rest_endpoints():
    """Verify FastAPI REST API endpoints for mobile device agent."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/mobile/devices/register
    res_reg = client.post(
        "/api/v1/mobile/devices/register",
        headers=headers,
        json={"device_id": "dev_test_mobile", "platform": "iOS", "model": "iPad Pro", "os_version": "iPadOS 18"}
    )
    assert res_reg.status_code == 200
    assert res_reg.json()["device_id"] == "dev_test_mobile"
    
    # GET /api/v1/mobile/devices
    res_list = client.get("/api/v1/mobile/devices", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 2
    
    # POST /api/v1/mobile/notifications/push
    res_push = client.post(
        "/api/v1/mobile/notifications/push",
        headers=headers,
        json={"device_id": "dev_test_mobile", "app_name": "Slack", "title": "Team", "body": "Deployment completed"}
    )
    assert res_push.status_code == 200
    assert res_push.json()["status"] == "DELIVERED"
    
    # GET /api/v1/mobile/analytics
    res_an = client.get("/api/v1/mobile/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "registered_devices_count" in res_an.json()
