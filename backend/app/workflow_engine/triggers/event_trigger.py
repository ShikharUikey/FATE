from typing import Dict, Any, List
from uuid import UUID
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.workflow_engine.designer.models import WorkflowRecord
from backend.app.workflow_engine.execution.runner import WorkflowExecutionRunner

class EventTriggerEngine:
    """Processes signals from operating system, calendar, database, and voice commands."""

    def __init__(self):
        self.runner = WorkflowExecutionRunner()

    async def process_event(self, event_type: str, payload: Dict[str, Any]) -> List[str]:
        """Matches incoming signals against workflow triggers and initiates executions."""
        triggered_executions = []
        
        # Query workflows that match description or trigger rules
        with Session(engine) as session:
            statement = select(WorkflowRecord)
            workflows = session.exec(statement).all()

            for wf in workflows:
                # Mock match logic: if event type matches description or keyword in name
                if event_type.lower() in wf.name.lower() or (wf.description and event_type.lower() in wf.description.lower()):
                    exec_rec = await self.runner.start_execution(wf, initial_vars={"trigger_event": payload})
                    await self.runner.execute_workflow(exec_rec.id)
                    triggered_executions.append(str(exec_rec.id))
                    
        return triggered_executions
