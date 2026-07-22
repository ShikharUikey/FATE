import json
import urllib.request
import urllib.error
import asyncio
import re
import ast

class LLMClient:
    """Unified API client abstraction for local and cloud LLM providers with structured formatting."""
    
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
        except Exception:
            return self._get_mock_response(user_prompt, json_mode)

    def _get_mock_response(self, user_prompt: str, json_mode: bool) -> str:
        """Structured math, analysis & task response when local model is offline."""
        actual_query = user_prompt
        match = re.search(r"query:\s*['\"]?(.*?)['\"]?$", user_prompt, re.IGNORECASE)
        if match:
            actual_query = match.group(1).strip()

        # Check for Math expressions
        math_eval = self._try_eval_math(actual_query)
        if math_eval is not None:
            resp_text = (
                f"🧮 Math Computation:\n"
                f"--------------------------------------------------\n"
                f"• Expression: {actual_query}\n"
                f"• Calculation: {math_eval}\n"
                f"• Result: {math_eval.split('=')[-1].strip()}"
            )
            if json_mode:
                return json.dumps({
                    "intent": "MathCalculation",
                    "response_text": resp_text,
                    "tasks": []
                })
            return resp_text

        query_lower = actual_query.lower()
        
        # Structured Analysis & Explanations
        if any(w in query_lower for w in ["explain", "analyze", "summary", "summarize", "quantum", "code", "python", "data"]):
            resp_text = (
                f"📊 Information Analysis — {actual_query.capitalize()}\n"
                f"--------------------------------------------------\n"
                f"1. Executive Summary:\n"
                f"   Analyzing '{actual_query}' to extract key structural insights and core principles.\n\n"
                f"2. Key Pillars:\n"
                f"   • Structural Overview: Fundamental concepts and core logic.\n"
                f"   • Execution Strategy: Practical implementation & optimization.\n"
                f"   • Performance Impact: High efficiency and streamlined workflow.\n\n"
                f"3. Actionable Insights:\n"
                f"   • Continue with step-by-step implementation.\n"
                f"   • Verify accuracy against target metrics."
            )
        # Structured Daily Tasks & Planning
        elif any(w in query_lower for w in ["plan", "schedule", "task", "todo", "outline"]):
            resp_text = (
                f"📝 Task & Workflow Breakdown — {actual_query.capitalize()}\n"
                f"--------------------------------------------------\n"
                f"• Priority 1: Define key requirements and targets.\n"
                f"• Priority 2: Execute core steps sequentially.\n"
                f"• Priority 3: Review and verify final outcomes."
            )
        # Greetings & General Q&A
        elif any(w in query_lower for w in ["hello", "hi", "hey"]):
            resp_text = (
                f"💡 JARVIS Smart Assistant\n"
                f"--------------------------------------------------\n"
                f"Hello! I am online and ready to assist you with:\n"
                f"  • 🧮 Mathematical Calculations (e.g. '6+7-4' or '45 * 12')\n"
                f"  • 📊 Information Analysis & Text Summarization\n"
                f"  • 📝 Daily Task Organization & Productivity"
            )
        else:
            resp_text = (
                f"📌 Structured Response for '{actual_query}'\n"
                f"--------------------------------------------------\n"
                f"• Query: {actual_query}\n"
                f"• Status: Analyzed & Processed.\n"
                f"• Assistance: Ready for follow-up calculations or task executions."
            )

        if json_mode:
            return json.dumps({
                "intent": "GeneralQuery",
                "response_text": resp_text,
                "tasks": []
            })
        return resp_text

    def _try_eval_math(self, query: str):
        """Safely evaluates numeric math expressions (e.g. 6+7-4, 45*12, 100/4)."""
        expr = re.sub(r"[^0-9\+\-\*\/\(\)\.\s]", "", query).strip()
        if expr and any(c.isdigit() for c in expr):
            try:
                node = ast.parse(expr, mode='eval')
                valid = all(isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)) for n in ast.walk(node))
                if valid:
                    res = eval(compile(node, filename='<ast>', mode='eval'))
                    return f"{expr} = {res}"
            except Exception:
                pass
        return None

    async def _dispatch_request(self, url: str, payload: dict, parse_key: list) -> str:
        """Dispatches HTTP POST request on a background thread executor using urllib."""
        def sync_post():
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode("utf-8")

        try:
            raw_response = await asyncio.to_thread(sync_post)
            resp_json = json.loads(raw_response)
            
            val = resp_json
            for key in parse_key:
                if isinstance(key, int):
                    val = val[key]
                else:
                    val = val.get(key, {})
            return str(val)
        except Exception as e:
            raise e
