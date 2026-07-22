import json
import re
import ast
from uuid import UUID, uuid4
from typing import List, Dict, Any, Tuple
from backend.app.core.llm_client import LLMClient
from backend.app.core.write_manager import write_manager
from backend.app.models.schemas import TaskQueue

class AIBrain:
    """Cognitive interface responsible for intent classification, math evaluation, and plan generation."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def _eval_math_direct(self, query: str) -> str:
        """Directly evaluates mathematical expressions (e.g. 6+7-4, 45*12)."""
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

    async def generate_plan_dag(self, plan_id: UUID, query: str) -> Tuple[str, List[TaskQueue]]:
        """Parses the user query, generates a structured plan, and instantiates TaskQueue models."""
        # 1. Quick Math Evaluation Check
        math_result = self._eval_math_direct(query)
        if math_result is not None:
            return f"Result: {math_result}", []

        # 2. General Query & Planning Prompt
        system_prompt = (
            "You are FATE's cognitive planner. Deconstruct user queries into structured plans.\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            "  \"intent\": \"string\",\n"
            "  \"response_text\": \"string\",\n"
            "  \"tasks\": []\n"
            "}\n"
        )
        
        user_prompt = f"Generate response for query: '{query}'"
        
        # Call LLM client (with JSON mode enabled)
        llm_response = await self.llm_client.generate_response(system_prompt, user_prompt, json_mode=True)
        
        try:
            plan_data = json.loads(llm_response)
        except Exception:
            return f"Processed query: '{query}'. How else can I help?", []

        response_text = plan_data.get("response_text", f"Processed query: '{query}'.")
        tasks_raw = plan_data.get("tasks", [])
        
        # Create mapping to convert relative array indices to actual database UUIDs
        task_uuids: Dict[int, UUID] = {}
        task_models: List[TaskQueue] = []
        
        # First pass: Allocate UUIDs to each task
        for idx in range(len(tasks_raw)):
            task_uuids[idx] = uuid4()

        # Second pass: Instantiate SQLModel tasks with actual dependency UUID strings
        for idx, task_raw in enumerate(tasks_raw):
            raw_deps = task_raw.get("dependencies", [])
            resolved_deps = [str(task_uuids[dep_idx]) for dep_idx in raw_deps if dep_idx in task_uuids]
            
            task = TaskQueue(
                id=task_uuids[idx],
                plan_id=plan_id,
                agent_name=task_raw.get("agent_name"),
                command=task_raw.get("command"),
                parameters=task_raw.get("parameters", "{}"),
                dependencies=json.dumps(resolved_deps),
                status="Pending"
            )
            task_models.append(task)

        # Commit tasks to the database via WriteManager
        for task in task_models:
            await write_manager.execute_write(task)

        return response_text, task_models
