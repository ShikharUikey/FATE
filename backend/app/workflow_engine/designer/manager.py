from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session, select
from backend.app.core.db import engine
from backend.app.workflow_engine.designer.models import WorkflowRecord, WorkflowStatus

class WorkflowDesignerManager:
    """Manages workflow creation, metadata configuration, updates, and templates bootstrap."""

    async def create_workflow(
        self,
        name: str,
        description: Optional[str] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        transitions: Optional[List[Dict[str, Any]]] = None,
        cron_expression: Optional[str] = None
    ) -> WorkflowRecord:
        """Saves a new workflow graph to SQLite database."""
        workflow = WorkflowRecord(
            id=uuid4(),
            name=name,
            description=description,
            status=WorkflowStatus.ACTIVE if cron_expression else WorkflowStatus.DRAFT,
            nodes=nodes or [],
            transitions=transitions or [],
            cron_expression=cron_expression,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        with Session(engine) as session:
            session.add(workflow)
            session.commit()
            session.refresh(workflow)
            return workflow

    async def get_workflow(self, workflow_id: UUID) -> Optional[WorkflowRecord]:
        """Retrieves a workflow by its unique UUID ID."""
        with Session(engine) as session:
            return session.get(WorkflowRecord, workflow_id)

    async def list_workflows(self) -> List[WorkflowRecord]:
        """Lists all registered workflow graphs."""
        with Session(engine) as session:
            statement = select(WorkflowRecord)
            return session.exec(statement).all()

    async def delete_workflow(self, workflow_id: UUID) -> bool:
        """Deletes a workflow graph from database."""
        with Session(engine) as session:
            workflow = session.get(WorkflowRecord, workflow_id)
            if not workflow:
                return False
            session.delete(workflow)
            session.commit()
            return True
