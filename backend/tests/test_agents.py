import os
import pytest
import shutil
from backend.app.agents.desktop_agent import DesktopAgent
from backend.app.agents.filesystem_agent import FileSystemAgent

@pytest.mark.asyncio
async def test_desktop_agent_terminal_command():
    """Verify that DesktopAgent executes terminal commands inside the workspace."""
    agent = DesktopAgent()
    res = await agent.execute_terminal_command("echo 'hello FATE'")
    assert res == "hello FATE"

@pytest.mark.asyncio
async def test_desktop_agent_running_apps():
    """Verify that DesktopAgent retrieves visible graphical apps or falls back to system processes."""
    agent = DesktopAgent()
    apps = await agent.get_running_processes()
    # On macOS, there should be at least some running processes or graphical apps listed
    assert isinstance(apps, list)
    assert len(apps) > 0

@pytest.mark.asyncio
async def test_filesystem_agent_duplicates_pruning():
    """Verify that FileSystemAgent walks directory paths, detects duplicates, and prunes them."""
    agent = FileSystemAgent()
    
    # Establish a temp test directory inside the project workspace
    sandbox = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi/test_sandbox"))
    os.makedirs(sandbox, exist_ok=True)
    
    try:
        # Create an original file
        file1 = os.path.join(sandbox, "original.txt")
        with open(file1, "w") as f:
            f.write("FATE unique observation content.")
            
        # Create two identical copies (duplicates)
        file2 = os.path.join(sandbox, "copy1.txt")
        file3 = os.path.join(sandbox, "copy2.txt")
        
        with open(file2, "w") as f:
            f.write("FATE unique observation content.")
        with open(file3, "w") as f:
            f.write("FATE unique observation content.")
            
        # Create a different file (not a duplicate)
        file4 = os.path.join(sandbox, "different.txt")
        with open(file4, "w") as f:
            f.write("Completely different file content.")

        # Execute duplicate deletion
        deleted = await agent.delete_duplicates(sandbox)
        
        # Verify exactly 2 files were deleted
        assert len(deleted) == 2
        assert file2 in deleted or file1 in deleted or file3 in deleted
        
        # Verify that remaining files inside the sandbox are original.txt and different.txt (total 2 files left)
        remaining = os.listdir(sandbox)
        assert len(remaining) == 2
        
        # Check files contents
        with open(os.path.join(sandbox, remaining[0]), "r") as f:
            c1 = f.read()
        with open(os.path.join(sandbox, remaining[1]), "r") as f:
            c2 = f.read()
        # Verify that both unique files contents are preserved
        assert c1 != c2
        
    finally:
        # Clean up the test sandbox directory
        shutil.rmtree(sandbox, ignore_errors=True)
