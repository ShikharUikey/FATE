from typing import Dict, Any, List

class WebsiteMonitoringService:
    """Monitors price changes, stock status, documentation updates, and dispatches alert notifications."""

    def __init__(self):
        self._watch_list: Dict[str, Dict[str, Any]] = {}

    def register_monitor_target(
        self,
        url: str,
        selector: str,
        target_type: str = "price_drop",
        threshold_val: float = 0.0
    ) -> bool:
        """Registers a webpage element to watch for content or numerical changes."""
        self._watch_list[url] = {
            "url": url,
            "selector": selector,
            "target_type": target_type,
            "threshold_val": threshold_val,
            "last_value": None
        }
        return True

    def check_for_content_changes(self, url: str, current_value: str) -> Dict[str, Any]:
        """Compares current element content against baseline value and detects diff changes."""
        item = self._watch_list.get(url)
        if not item:
            return {"status": "NOT_MONITORED"}

        last_val = item["last_value"]
        item["last_value"] = current_value

        if last_val is not None and last_val != current_value:
            return {
                "status": "CHANGE_DETECTED",
                "url": url,
                "previous_value": last_val,
                "current_value": current_value,
                "alert_triggered": True
            }

        return {
            "status": "NO_CHANGE",
            "url": url,
            "alert_triggered": False
        }
