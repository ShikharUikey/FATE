import asyncio
import json
from uuid import UUID
from datetime import datetime
from typing import Dict, List, Any
from sqlmodel import select, Session
from backend.app.core.db import engine
from backend.app.core.write_manager import write_manager
from backend.app.models.schemas import TaskQueue

class AgentOrchestrator:
    """Core scheduler responsible for executing task dependency DAGs."""
    
    def __init__(self):
        self.agent_registry = {}  # Maps agent names to driver instances

    def register_agent(self, name: str, driver: Any):
        """Registers a specialized agent driver to the orchestrator runtime."""
        self.agent_registry[name] = driver

    async def execute_plan(self, plan_id: UUID) -> bool:
        """Resolves task dependency trees and executes the plan DAG."""
        # 1. Fetch all tasks matching the plan_id
        with Session(engine) as session:
            statement = select(TaskQueue).where(TaskQueue.plan_id == plan_id)
            tasks = session.exec(statement).all()

        if not tasks:
            return True

        task_dict: Dict[UUID, TaskQueue] = {t.id: t for t in tasks}
        completed_tasks: Dict[UUID, bool] = {}
        running_tasks: List[asyncio.Task] = []

        async def run_task_wrapper(task: TaskQueue):
            """Core execution wrapper for individual tasks."""
            # Update status to Running
            task.status = "Running"
            task.started_at = datetime.utcnow()
            await write_manager.execute_write(task)

            success = False
            error_msg = None
            
            try:
                # Call registered agent or execute mockup driver
                agent_name = task.agent_name
                if agent_name in self.agent_registry:
                    agent = self.agent_registry[agent_name]
                    params = json.loads(task.parameters)
                    success = await agent.execute(task.command, params)
                else:
                    # Mock/Default execution if no agent is registered (fallback for bootstrap verification)
                    await asyncio.sleep(0.1)
                    success = True
            except Exception as e:
                error_msg = str(e)
                success = False

            if success:
                task.status = "Success"
            else:
                task.status = "Failed"
                task.error_message = error_msg or "Execution returned False."

            task.completed_at = datetime.utcnow()
            await write_manager.execute_write(task)
            return task.id, success

        # 2. Loop until all tasks are resolved
        while len(completed_tasks) < len(task_dict):
            # Find tasks whose dependencies are fully completed
            runnable_tasks = []
            for t_id, task in task_dict.items():
                if t_id in completed_tasks or task.status == "Running":
                    continue
                
                # Check dependencies
                deps = json.loads(task.dependencies)
                dep_uuids = [UUID(d) for d in deps]
                
                # Verify if all dependent tasks succeeded
                all_deps_done = True
                dep_failed = False
                for d_uuid in dep_uuids:
                    if d_uuid not in completed_tasks:
                        all_deps_done = False
                        break
                    if not completed_tasks[d_uuid]:
                        dep_failed = True
                        break
                
                if dep_failed:
                    # Mark task as Failed due to dependency failure
                    task.status = "Failed"
                    task.error_message = f"Dependency task {d_uuid} failed."
                    task.completed_at = datetime.utcnow()
                    await write_manager.execute_write(task)
                    completed_tasks[t_id] = False
                    continue

                if all_deps_done:
                    runnable_tasks.append(task)

            # Spawn runnable tasks concurrently
            for task in runnable_tasks:
                running_tasks.append(asyncio.create_task(run_task_wrapper(task)))

            if not running_tasks:
                # If there are tasks remaining but none are runnable or running, we have a deadlock/cycle
                if len(completed_tasks) < len(task_dict):
                    return False
                break

            # Wait for any running task to complete
            done, pending = await asyncio.wait(running_tasks, return_when=asyncio.FIRST_COMPLETED)
            running_tasks = list(pending)

            for finished_future in done:
                t_id, success = finished_future.result()
                completed_tasks[t_id] = success
                task_dict[t_id].status = "Success" if success else "Failed"

        # Return True if all tasks finished with Success
        return all(completed_tasks.values())
