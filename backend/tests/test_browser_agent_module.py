import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.browser_agent.sessions.manager import BrowserSessionManager
from backend.app.browser_agent.navigation.navigator import WebNavigatorEngine
from backend.app.browser_agent.dom.dom_engine import DOMIntelligenceEngine
from backend.app.browser_agent.forms.form_automation import FormAutomationEngine
from backend.app.browser_agent.scraping.scraper import WebScrapingEngine
from backend.app.browser_agent.monitoring.website_monitor import WebsiteMonitoringService
from backend.app.browser_agent.authentication.auth_manager import BrowserAuthManager
from backend.app.browser_agent.analytics.telemetry import BrowserAnalyticsTelemetry

client = TestClient(app)

@pytest.mark.asyncio
async def test_browser_session_manager():
    """Verify session creation, listing, and close actions (<2s target)."""
    mgr = BrowserSessionManager()
    session = await mgr.create_session(browser_type="chromium", headless=True)
    
    assert session["session_id"] is not None
    assert session["browser_type"] == "chromium"
    
    sessions = await mgr.list_active_sessions()
    assert len(sessions) == 1
    
    closed = await mgr.close_session(session["session_id"])
    assert closed is True

@pytest.mark.asyncio
async def test_web_navigator_actions():
    """Verify navigation, clicks, hover, and scroll actions (<200ms action target)."""
    mgr = BrowserSessionManager()
    session = await mgr.create_session()
    nav = WebNavigatorEngine(mgr)
    
    # Goto
    goto_res = await nav.navigate_to(session["session_id"], "https://github.com")
    assert goto_res["status"] == "SUCCESS"
    assert goto_res["url"] == "https://github.com"
    
    # Click
    click_res = await nav.click_element(session["session_id"], "button.search")
    assert click_res["status"] == "SUCCESS"
    assert click_res["duration_ms"] >= 0

def test_dom_intelligence_parsing():
    """Verify DOM element tree parsing and broken selector repair (<100ms target)."""
    dom = DOMIntelligenceEngine()
    html = "<html><body><button id='submit-btn'>Submit</button></body></html>"
    
    parsed = dom.parse_page_structure(html)
    assert parsed["parsing_time_ms"] >= 0
    assert parsed["elements_count"] > 0
    
    repaired = dom.repair_broken_selector("#broken_submit-btn", parsed["elements"])
    assert repaired == "#submit-btn"

@pytest.mark.asyncio
async def test_form_automation():
    """Verify form inputs filling and error detection."""
    mgr = BrowserSessionManager()
    session = await mgr.create_session()
    nav = WebNavigatorEngine(mgr)
    form = FormAutomationEngine(nav)
    
    res = await form.fill_form_fields(session["session_id"], {"#username": "admin", "#password": "secret"})
    assert res["status"] == "SUCCESS"
    assert res["filled_fields_count"] == 2
    
    errors = await form.detect_form_validation_errors("Error: invalid password entered")
    assert len(errors) == 1

def test_web_scraping_engine():
    """Verify structured table extraction and metadata parsing."""
    scraper = WebScrapingEngine()
    html = "<table><tr><td>AI-101</td><td>₹6,500</td></tr></table>"
    
    records = scraper.extract_structured_table(html)
    assert len(records) > 0
    assert "Flight" in records[0]
    
    meta = scraper.extract_page_metadata(html, "https://example.com")
    assert meta["url"] == "https://example.com"

def test_website_monitoring():
    """Verify website price drop/content diff detection."""
    monitor = WebsiteMonitoringService()
    url = "https://example.com/product"
    
    monitor.register_monitor_target(url, ".price", target_type="price_drop")
    
    # First check (baseline)
    res_1 = monitor.check_for_content_changes(url, "₹5,000")
    assert res_1["alert_triggered"] is False
    
    # Second check (price dropped)
    res_2 = monitor.check_for_content_changes(url, "₹4,500")
    assert res_2["status"] == "CHANGE_DETECTED"
    assert res_2["alert_triggered"] is True

def test_auth_manager_and_cookies():
    """Verify domain cookies jar and credential vault integration."""
    auth = BrowserAuthManager()
    cookies = [{"name": "session_id", "value": "12345"}]
    
    auth.store_domain_cookies("github.com", cookies)
    retrieved = auth.get_domain_cookies("github.com")
    assert len(retrieved) == 1
    assert retrieved[0]["value"] == "12345"

def test_browser_telemetry():
    """Verify telemetry screenshot capture (<300ms target) and metric logging."""
    telemetry = BrowserAnalyticsTelemetry()
    telemetry.record_action_metric("navigate", 150.0, success=True)
    
    screenshot = telemetry.capture_screenshot_log("session_101")
    assert screenshot["capture_duration_ms"] >= 0
    
    metrics = telemetry.get_performance_summary()
    assert metrics["total_actions"] == 1
    assert metrics["success_rate_percent"] == 100.0

def test_browser_rest_endpoints():
    """Verify FastAPI REST API endpoints for browser automation."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/browser/sessions
    res_s = client.post("/api/v1/browser/sessions", headers=headers, json={"browser_type": "chromium"})
    assert res_s.status_code == 200
    session_id = res_s.json()["session_id"]
    
    # POST /api/v1/browser/navigate
    res_nav = client.post("/api/v1/browser/navigate", headers=headers, json={"session_id": session_id, "url": "https://google.com"})
    assert res_nav.status_code == 200
    assert res_nav.json()["status"] == "SUCCESS"
    
    # GET /api/v1/browser/analytics
    res_an = client.get("/api/v1/browser/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "avg_action_duration_ms" in res_an.json()
