import time
from typing import Dict, Any, List, Optional
from uuid import uuid4

class MobileDeviceManager:
    """Manages mobile device enrollment, status metrics, device lock, and HITL remote wipe actions."""

    def __init__(self):
        self._devices: Dict[str, Dict[str, Any]] = {
            "dev_android_01": {
                "device_id": "dev_android_01",
                "platform": "Android",
                "model": "Google Pixel 9 Pro",
                "os_version": "Android 15",
                "battery_health_percent": 98,
                "storage_available_gb": 128.5,
                "trust_level": "HIGH",
                "is_encrypted": True,
                "is_locked": False,
                "last_seen": time.time()
            },
            "dev_ios_01": {
                "device_id": "dev_ios_01",
                "platform": "iOS",
                "model": "iPhone 16 Pro Max",
                "os_version": "iOS 18.2",
                "battery_health_percent": 100,
                "storage_available_gb": 256.0,
                "trust_level": "HIGH",
                "is_encrypted": True,
                "is_locked": False,
                "last_seen": time.time()
            }
        }

    async def register_device(
        self,
        device_id: str,
        platform: str,
        model: str,
        os_version: str
    ) -> Dict[str, Any]:
        """Registers a new mobile device in FATE's mobile ecosystem."""
        record = {
            "device_id": device_id,
            "platform": platform,
            "model": model,
            "os_version": os_version,
            "battery_health_percent": 100,
            "storage_available_gb": 64.0,
            "trust_level": "MEDIUM",
            "is_encrypted": True,
            "is_locked": False,
            "last_seen": time.time()
        }
        self._devices[device_id] = record
        return record

    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Queries device status record by device_id."""
        return self._devices.get(device_id)

    async def list_registered_devices(self) -> List[Dict[str, Any]]:
        """Lists registered Android and iOS devices."""
        return list(self._devices.values())

    async def lock_device(self, device_id: str) -> bool:
        """Remotely locks a mobile device screen."""
        dev = self._devices.get(device_id)
        if not dev:
            return False
        dev["is_locked"] = True
        return True

    async def remote_wipe_device(self, device_id: str, hitl_approved: bool = False) -> Dict[str, Any]:
        """Remotely wipes a device. Requires explicit HITL user approval."""
        if not hitl_approved:
            return {
                "status": "BLOCKED",
                "reason": f"Remote wipe for [{device_id}] is a CRITICAL destructive action and requires HITL approval.",
                "hitl_required": True
            }

        dev = self._devices.get(device_id)
        if not dev:
            return {"status": "FAILED", "error": f"Device [{device_id}] not found."}

        self._devices.pop(device_id, None)
        return {"status": "WIPED", "device_id": device_id}
