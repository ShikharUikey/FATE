import json
import urllib.request
import urllib.error
import asyncio

class LLMClient:
    """Unified API client abstraction for local and cloud LLM providers."""
    
    def __init__(self, provider: str = "ollama", model_name: str = "llama3", api_key: str = ""):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        # Default local loopback endpoints
        self.endpoints = {
            "ollama": "http://127.0.0.1:11434/api/chat",
            "lm_studio": "http://127.0.0.1:1234/v1/chat/completions"
        }

    async def generate_response(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Asynchronously dispatches execution requests to the configured model provider."""
        try:
            # Setup payloads based on provider
            if self.provider == "ollama":
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False
                }
                if json_mode:
                    payload["format"] = "json"
                return await self._dispatch_request(self.endpoints["ollama"], payload, parse_key=["message", "content"])
            
            elif self.provider == "lm_studio":
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}
                return await self._dispatch_request(self.endpoints["lm_studio"], payload, parse_key=["choices", 0, "message", "content"])
            
            else:
                return self._get_mock_response(user_prompt, json_mode)
        except Exception as e:
            # Fall back to mock completions dynamically on network failures
            print(f"[LLM WARNING] Local provider offline: {e}. Falling back to mock completions.")
            return self._get_mock_response(user_prompt, json_mode)

    def _get_mock_response(self, user_prompt: str, json_mode: bool) -> str:
        """Fallback mock responses for testing and offline execution."""
        if json_mode:
            # Returns a structured mock plan if it detects planning/scheduling keywords
            if "plan" in user_prompt.lower() or "schedule" in user_prompt.lower() or "meeting" in user_prompt.lower():
                return json.dumps({
                    "intent": "CreateMeetingAndEmail",
                    "response_text": "I am scheduling the meeting and writing the email.",
                    "tasks": [
                        {"agent_name": "CalendarAgent", "command": "schedule_event", "parameters": json.dumps({"title": "Meeting with Bob", "time": "10:00"}), "dependencies": []},
                        {"agent_name": "CommunicationAgent", "command": "send_email", "parameters": json.dumps({"recipient": "bob@example.com", "subject": "Draft Review"}), "dependencies": [0]}
                    ]
                })
            return json.dumps({"intent": "Unknown", "response_text": "Mock response in JSON mode."})
        return "Mock response text."


    async def _dispatch_request(self, url: str, payload: dict, parse_key: list) -> str:
        """Dispatches HTTP POST request on a background thread executor using urllib."""
        def sync_post():
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.read().decode("utf-8")
            except urllib.error.URLError as e:
                # Return standard exception string to catch upstream
                raise Exception(f"HTTP request failed: {e.reason}")

        try:
            raw_response = await asyncio.to_thread(sync_post)
            resp_json = json.loads(raw_response)
            
            # Surgically traverse keys to retrieve the target string content
            val = resp_json
            for key in parse_key:
                if isinstance(key, int):
                    val = val[key]
                else:
                    val = val.get(key, {})
            return str(val)
        except Exception as e:
            # Return fallback mock string if local model is offline
            print(f"[LLM WARNING] Local provider offline: {e}. Falling back to mock mock completions.")
            raise e
