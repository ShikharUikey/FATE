import pytest
import os
import shutil
from backend.app.agents.calendar_agent import CalendarAgent
from backend.app.agents.communication_agent import CommunicationAgent
from backend.app.agents.coding_agent import CodingAgent

@pytest.mark.asyncio
async def test_calendar_agent_execution():
    """Verify that CalendarAgent handles event creation and agenda queries."""
    agent = CalendarAgent()
    
    # Create event
    created = await agent.create_event("Sprint Demo", "2026-07-22", "10:00 AM")
    assert created is True
    
    # List events
    events = await agent.list_events("2026-07-22")
    assert isinstance(events, list)
    assert len(events) > 0
    assert "title" in events[0]

@pytest.mark.asyncio
async def test_communication_agent_execution():
    """Verify that CommunicationAgent handles email drafting and contacts search."""
    agent = CommunicationAgent()
    
    # Send email trigger
    sent = await agent.send_email("alice@example.com", "Project Status Update", "FATE Core operational.")
    assert sent is True
    
    # Search contacts
    contacts = await agent.search_contacts("Bob")
    assert isinstance(contacts, list)
    assert len(contacts) > 0
    assert contacts[0]["email"] == "bob@example.com"

@pytest.mark.asyncio
async def test_coding_agent_execution():
    """Verify that CodingAgent parses Python AST code metrics, lints files, and applies patches."""
    agent = CodingAgent()
    sandbox = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi/test_code_sandbox"))
    os.makedirs(sandbox, exist_ok=True)
    file_path = os.path.join(sandbox, "sample.py")
    
    try:
        # Create a sample Python file
        code_content = "def test_func():\n    x = 10\n    return x;\n"
        await agent.apply_patch(file_path, code_content)
        assert os.path.exists(file_path)
        
        # Analyze code AST
        analysis = await agent.analyze_code(file_path)
        assert analysis["status"] == "success"
        assert "test_func" in analysis["functions"]
        
        # Lint file
        lint_issues = await agent.lint_file(file_path)
        assert isinstance(lint_issues, list)
        assert len(lint_issues) > 0  # Semicolon flagged
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)
