import time
from typing import Dict, Any, List

class AnalyticsAlertManager:
    """Dispatches alert notifications for SLA breaches, cloud budget thresholds, and security incidents."""

    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []

    def dispatch_alert(
        self,
        alert_category: str,
        title: str,
        message: str,
        severity: str = "WARNING"
    ) -> Dict[str, Any]:
        """Dispatches analytical alert event."""
        alert_id = f"alt_{int(time.time()*1000)}"
        record = {
            "alert_id": alert_id,
            "category": alert_category,
            "title": title,
            "message": message,
            "severity": severity.upper(),
            "timestamp": time.time()
        }
        self._alerts.append(record)
        return {"status": "DISPATCHED", "alert": record}

    def list_active_alerts(self) -> List[Dict[str, Any]]:
        """Lists active analytical alerts."""
        return list(reversed(self._alerts))
