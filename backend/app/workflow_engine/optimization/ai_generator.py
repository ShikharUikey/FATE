import re
from typing import Dict, Any, List

class AIWorkflowGenerator:
    """Parses natural language prompt strings and generates structured workflow JSON graphs."""

    def generate_workflow_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Converts user query prompt text to structured node-transitions list schema."""
        clean_prompt = prompt.lower()
        nodes = [{"id": "start", "type": "Start"}]
        transitions = []
        
        # Parse targets using regex
        if "email" in clean_prompt:
            nodes.append({"id": "read_emails", "type": "APIRequest", "properties": {"endpoint": "/api/v1/communication/emails"}})
        if "calendar" in clean_prompt or "meeting" in clean_prompt:
            nodes.append({"id": "read_calendar", "type": "APIRequest", "properties": {"endpoint": "/api/v1/calendar/events"}})
        if "github" in clean_prompt:
            nodes.append({"id": "read_github", "type": "APIRequest", "properties": {"endpoint": "/api/v1/github/activity"}})
        
        # Add LLM Summarization node
        if "summarize" in clean_prompt or "digest" in clean_prompt or "briefing" in clean_prompt:
            nodes.append({"id": "summarize", "type": "LLMPrompt", "properties": {"prompt": prompt}})
            
        # Add notify alert
        if "notify" in clean_prompt or "tell" in clean_prompt or "voice" in clean_prompt or "brief" in clean_prompt:
            nodes.append({"id": "notify", "type": "Notification", "properties": {"method": "voice"}})
            
        nodes.append({"id": "end", "type": "End"})

        # Build sequential links
        for i in range(len(nodes) - 1):
            transitions.append({
                "from": nodes[i]["id"],
                "to": nodes[i+1]["id"]
            })

        return {
            "name": "AI Generated Pipeline",
            "description": f"Generated from prompt: '{prompt}'",
            "nodes": nodes,
            "transitions": transitions
        }
