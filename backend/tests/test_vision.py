import pytest
import os
from backend.app.core.macos_accessibility import MacOSAccessibility
from backend.app.agents.vision_agent import VisionAgent

@pytest.mark.asyncio
async def test_macos_accessibility_capture_and_ocr():
    """Verify that MacOSAccessibility captures screen and performs text recognition."""
    acc = MacOSAccessibility()
    
    # Capture screen
    path = await acc.capture_screen()
    assert path is not None
    assert os.path.exists(path)
    
    # Recognize text on captured image
    blocks = await acc.recognize_text_on_screen(path)
    assert isinstance(blocks, list)
    assert len(blocks) > 0
    assert "text" in blocks[0]
    
    # Clean up temp screenshot
    if os.path.exists(path):
        os.remove(path)

@pytest.mark.asyncio
async def test_vision_agent_execution():
    """Verify that VisionAgent executes OCR recognition and click actions."""
    agent = VisionAgent()
    
    # Execute recognize_text command
    params = {}
    ok = await agent.execute("recognize_text", params)
    assert ok is True
    assert "result" in params
    assert len(params["result"]) > 0
    
    # Execute click_text_target command
    click_ok = await agent.click_text_target("DISPATCH")
    assert click_ok is True
