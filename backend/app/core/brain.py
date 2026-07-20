import json
from uuid import UUID, uuid4
from typing import List, Dict, Any, Tuple
from backend.app.core.llm_client import LLMClient
from backend.app.core.write_manager import write_manager
from backend.app.models.schemas import TaskQueue

class AIBrain:
    """Cognitive interface responsible for intent classification and plan generation."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_plan_dag(self, plan_id: UUID, query: str) -> Tuple[str, List[TaskQueue]]:
        """Parses the user query, generates a structured plan, and instantiates TaskQueue models."""
        system_prompt = (
            "You are FATE's cognitive planner. Deconstruct user queries into structured plans.\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            "  \"intent\": \"string\",\n"
            "  \"response_text\": \"string\",\n"
            "  \"tasks\": [\n"
            "    {\n"
            "      \"agent_name\": \"string\",\n"
            "      \"command\": \"string\",\n"
            "      \"parameters\": \"string (JSON-serialized key-value string)\",\n"
            "      \"dependencies\": [int (indices of parent tasks in this array)]\n"
            "    }\n"
            "  ]\n"
            "}\n"
        )
        
        user_prompt = f"Generate a plan for this user query: '{query}'"
        
        # Call LLM client (with JSON mode enabled)
        llm_response = await self.llm_client.generate_response(system_prompt, user_prompt, json_mode=True)
        
        try:
            plan_data = json.loads(llm_response)
        except Exception:
            # Fallback parser if JSON is corrupted
            return "Failed to parse plan structure.", []

        response_text = plan_data.get("response_text", "I'm executing your request.")
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
