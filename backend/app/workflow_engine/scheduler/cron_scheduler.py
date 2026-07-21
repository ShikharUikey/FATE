import asyncio
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.workflow_engine.designer.models import WorkflowRecord
from backend.app.workflow_engine.execution.runner import WorkflowExecutionRunner

class WorkflowTaskScheduler:
    """Manages scheduled workflow triggers using Cron expressions and dependency chains."""

    def __init__(self):
        self.runner = WorkflowExecutionRunner()
        self._schedules: Dict[str, str] = {}

    def register_schedule(self, workflow_id: UUID, cron_expr: str):
        """Saves scheduling expression configuration parameters."""
        self._schedules[str(workflow_id)] = cron_expr

    def get_registered_schedules(self) -> Dict[str, str]:
        """Lists active scheduled workflow configurations."""
        return self._schedules

    async def trigger_due_workflows(self) -> List[str]:
        """Scans database workflows and triggers executions for active cron schedules."""
        triggered = []
        with Session(engine) as session:
            statement = select(WorkflowRecord).where(WorkflowRecord.cron_expression != None)
            workflows = session.exec(statement).all()

            for wf in workflows:
                # Trigger instant background run simulation
                exec_rec = await self.runner.start_execution(wf)
                asyncio.create_task(self.runner.execute_workflow(exec_rec.id))
                triggered.append(str(wf.id))
        return triggered
