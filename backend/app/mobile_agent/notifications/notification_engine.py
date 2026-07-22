import time
from typing import Dict, Any, List, Optional

class MobileNotificationEngine:
    """Synchronizes cross-device mobile notifications (<100ms delivery target) and generates AI response suggestions."""

    def __init__(self):
        self._notification_feed: List[Dict[str, Any]] = []

    async def push_notification(
        self,
        device_id: str,
        app_name: str,
        title: str,
        body: str,
        priority: str = "NORMAL"
    ) -> Dict[str, Any]:
        """Pushes a mobile notification record into cross-device feed (<100ms target)."""
        start_time = time.time()
        record = {
            "notification_id": f"notif_{int(time.time()*1000)}",
            "device_id": device_id,
            "app_name": app_name,
            "title": title,
            "body": body,
            "priority": priority.upper(),
            "timestamp": time.time(),
            "suggested_replies": self._generate_ai_replies(body)
        }
        self._notification_feed.append(record)
        delivery_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "DELIVERED",
            "delivery_time_ms": delivery_time_ms,
            "notification": record
        }

    def _generate_ai_replies(self, message_body: str) -> List[str]:
        """Generates quick AI response options based on message intent."""
        lowered = message_body.lower()
        if "?" in message_body or "meeting" in lowered or "when" in lowered:
            return ["I'll check my calendar and let you know.", "Sounds good!", "Can we connect at 4 PM?"]
        elif "urgent" in lowered or "asap" in lowered:
            return ["On it right now!", "Will resolve immediately."]
        return ["Thanks!", "Got it.", "Will review shortly."]

    async def get_recent_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent cross-device notifications."""
        return list(reversed(self._notification_feed[-limit:]))
