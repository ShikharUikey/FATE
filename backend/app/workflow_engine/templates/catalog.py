from typing import Dict, Any, List

class WorkflowTemplatesCatalog:
    """Pre-built workflow node templates catalog for FATE platform operations."""

    @staticmethod
    def get_templates() -> Dict[str, Dict[str, Any]]:
        """Returns standard preconfigured templates."""
        return {
            "morning_briefing": {
                "name": "Morning Briefing Digest",
                "description": "Summarizes email, today's schedule, and GitHub updates.",
                "nodes": [
                    {"id": "start", "type": "Start"},
                    {"id": "read_emails", "type": "APIRequest", "properties": {"endpoint": "/api/v1/communication/emails"}},
                    {"id": "read_calendar", "type": "APIRequest", "properties": {"endpoint": "/api/v1/calendar/events"}},
                    {"id": "summarize", "type": "LLMPrompt", "properties": {"prompt": "Summarize these details..."}},
                    {"id": "notify", "type": "Notification", "properties": {"method": "voice"}},
                    {"id": "end", "type": "End"}
                ],
                "transitions": [
                    {"from": "start", "to": "read_emails"},
                    {"from": "read_emails", "to": "read_calendar"},
                    {"from": "read_calendar", "to": "summarize"},
                    {"from": "summarize", "to": "notify"},
                    {"from": "notify", "to": "end"}
                ]
            },
            "daily_backup": {
                "name": "Daily SQLite Backup",
                "description": "Compresses database and transfers snapshot archives.",
                "nodes": [
                    {"id": "start", "type": "Start"},
                    {"id": "backup_db", "type": "FileOperation", "properties": {"action": "compress"}},
                    {"id": "upload_cloud", "type": "APIRequest", "properties": {"endpoint": "/api/v1/tools/execute"}},
                    {"id": "end", "type": "End"}
                ],
                "transitions": [
                    {"from": "start", "to": "backup_db"},
                    {"from": "backup_db", "to": "upload_cloud"},
                    {"from": "upload_cloud", "to": "end"}
                ]
            }
        }
