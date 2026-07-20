import pytest
from backend.app.agents.browser_agent import BrowserAgent

@pytest.mark.asyncio
async def test_browser_agent_mock_actions():
    """Verify that BrowserAgent falls back to mock navigation and scraping if Playwright is offline."""
    agent = BrowserAgent()
    
    # Verify navigation works (returns true)
    success = await agent.navigate_to("https://github.com")
    assert success is True
    
    # Verify input fill works
    fill_ok = await agent.fill_input("input[name=q]", "pytest")
    assert fill_ok is True
    
    # Verify click works
    click_ok = await agent.click_element("button.search")
    assert click_ok is True
    
    # Verify text extraction returns fallback mock string
    content = await agent.get_page_content()
    assert "Mock Page Extraction" in content
    
    # Clean up browser session
    await agent.close()
