import os
import pytest
import asyncio
import json
from uuid import uuid4
from sqlmodel import Session, select
from backend.app.core.db import init_db, engine
from backend.app.core.write_manager import write_manager
from backend.app.core.orchestrator import AgentOrchestrator
from backend.app.models.schemas import CoreSettings, TaskQueue

from sqlalchemy import text

# Configure the SQLite database setup for tests
init_db()

@pytest.mark.asyncio
async def test_database_wal_mode():
    """Verify that the database is running in WAL mode."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA journal_mode;")).fetchone()
        assert result[0].lower() == "wal"

@pytest.mark.asyncio
async def test_write_manager_concurrency():
    """Verify thread-safe concurrent database writes using the WriteManager queue."""
    # Start the WriteManager queue worker loop
    await write_manager.start()
    
    import uuid
    run_id = uuid.uuid4().hex[:8]
    
    # Push concurrent writes
    tasks = []
    for i in range(10):
        setting = CoreSettings(key=f"test_key_{run_id}_{i}", value=f"test_val_{i}")
        tasks.append(write_manager.execute_write(setting))
        
    results = await asyncio.gather(*tasks)
    assert len(results) == 10
    
    # Read values back to verify persistence
    with Session(engine) as session:
        statement = select(CoreSettings).where(CoreSettings.key.like(f"test_key_{run_id}_%"))
        records = session.exec(statement).all()
        assert len(records) == 10

@pytest.mark.asyncio
async def test_orchestrator_scheduling_dag():
    """Verify DAG dependency resolution and task scheduling order."""
    plan_id = uuid4()
    
    # Write three mock tasks where Task 3 depends on Task 1 and Task 2
    task1 = TaskQueue(
        plan_id=plan_id,
        agent_name="MockAgent",
        command="action1",
        parameters="{}",
        status="Pending",
        priority="Normal",
        dependencies="[]"
    )
    task2 = TaskQueue(
        plan_id=plan_id,
        agent_name="MockAgent",
        command="action2",
        parameters="{}",
        status="Pending",
        priority="Normal",
        dependencies="[]"
    )
    
    # Save first two to resolve their IDs
    await write_manager.execute_write(task1)
    await write_manager.execute_write(task2)
    
    task3 = TaskQueue(
        plan_id=plan_id,
        agent_name="MockAgent",
        command="action3",
        parameters="{}",
        status="Pending",
        priority="Normal",
        dependencies=json.dumps([str(task1.id), str(task2.id)])
    )
    await write_manager.execute_write(task3)

    # Instantiate Orchestrator and register a Mock Agent
    class MockAgentDriver:
        async def execute(self, command: str, params: dict) -> bool:
            await asyncio.sleep(0.05)
            return True

    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("MockAgent", MockAgentDriver())
    
    # Execute the plan
    success = await orchestrator.execute_plan(plan_id)
    assert success is True
    
    # Verify DB states
    with Session(engine) as session:
        statement = select(TaskQueue).where(TaskQueue.plan_id == plan_id)
        results = session.exec(statement).all()
        assert len(results) == 3
        for task in results:
            assert task.status == "Success"
            assert task.started_at is not None
            assert task.completed_at is not None
