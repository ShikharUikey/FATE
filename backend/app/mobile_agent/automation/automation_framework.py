from typing import Dict, Any, List

class MobileAutomationFramework:
    """Automates mobile routines: Morning routine, Driving mode, Meeting mode, Battery saver, and Geofence rules."""

    def trigger_routine_mode(self, mode_name: str, enabled: bool = True) -> Dict[str, Any]:
        """Toggles mobile contextual mode profile settings."""
        mode_clean = mode_name.lower().replace(" ", "_")
        
        profiles = {
            "driving_mode": {"do_not_disturb": True, "auto_reply_sms": True, "bluetooth_audio": True},
            "meeting_mode": {"do_not_disturb": True, "vibrate_only": True, "auto_decline_calls": False},
            "morning_routine": {"read_schedule": True, "play_news_briefing": True, "adjust_thermostat": True},
            "battery_saver": {"background_sync": False, "lower_brightness": True, "disable_5g": True}
        }

        config = profiles.get(mode_clean, {"enabled": enabled})
        return {
            "status": "ACTIVATED" if enabled else "DEACTIVATED",
            "mode": mode_clean,
            "profile_config": config
        }

    def evaluate_geofence_trigger(
        self,
        current_lat: float,
        current_lng: float,
        target_lat: float,
        target_lng: float,
        radius_meters: float = 100.0
    ) -> Dict[str, Any]:
        """Evaluates if location coordinates lie inside geofence boundary radius."""
        # Simple Euclidean distance approximation
        lat_diff = (current_lat - target_lat) * 111000
        lng_diff = (current_lng - target_lng) * 111000
        dist_approx = (lat_diff**2 + lng_diff**2) ** 0.5

        inside = dist_approx <= radius_meters
        return {
            "inside_geofence": inside,
            "distance_meters": round(dist_approx, 1),
            "triggered_action": "ENTER_OFFICE_ROUTINE" if inside else "NONE"
        }
