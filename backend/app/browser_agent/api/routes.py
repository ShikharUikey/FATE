from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.browser_agent.sessions.manager import BrowserSessionManager
from backend.app.browser_agent.navigation.navigator import WebNavigatorEngine
from backend.app.browser_agent.dom.dom_engine import DOMIntelligenceEngine
from backend.app.browser_agent.forms.form_automation import FormAutomationEngine
from backend.app.browser_agent.scraping.scraper import WebScrapingEngine
from backend.app.browser_agent.monitoring.website_monitor import WebsiteMonitoringService
from backend.app.browser_agent.authentication.auth_manager import BrowserAuthManager
from backend.app.browser_agent.analytics.telemetry import BrowserAnalyticsTelemetry

router = APIRouter(
    prefix="/api/v1/browser",
    tags=["Web & Browser Automation Agent"]
)

# Managers Singletons
session_mgr = BrowserSessionManager()
navigator = WebNavigatorEngine(session_mgr)
dom_engine = DOMIntelligenceEngine()
form_auto = FormAutomationEngine(navigator)
scraper = WebScrapingEngine()
monitor_svc = WebsiteMonitoringService()
auth_mgr = BrowserAuthManager()
telemetry = BrowserAnalyticsTelemetry()

class CreateSessionRequest(BaseModel):
    browser_type: Optional[str] = "chromium"
    headless: Optional[bool] = True

class NavigateRequest(BaseModel):
    session_id: str
    url: str

class ClickRequest(BaseModel):
    session_id: str
    selector: str

class FormFillRequest(BaseModel):
    session_id: str
    field_data: Dict[str, str]

class ScrapeTableRequest(BaseModel):
    html_content: str

class MonitorRegisterRequest(BaseModel):
    url: str
    selector: str
    target_type: Optional[str] = "price_drop"

@router.post("/sessions", dependencies=[Depends(verify_session_token)])
async def create_session(payload: CreateSessionRequest):
    """Launches browser session context (<2s target)."""
    return await session_mgr.create_session(
        browser_type=payload.browser_type or "chromium",
        headless=payload.headless if payload.headless is not None else True
    )

@router.get("/sessions", dependencies=[Depends(verify_session_token)])
async def list_sessions():
    """Lists active browser sessions."""
    return await session_mgr.list_active_sessions()

@router.post("/navigate", dependencies=[Depends(verify_session_token)])
async def navigate_to(payload: NavigateRequest):
    """Navigates browser to URL (<2s target)."""
    return await navigator.navigate_to(payload.session_id, payload.url)

@router.post("/click", dependencies=[Depends(verify_session_token)])
async def click_element(payload: ClickRequest):
    """Clicks target DOM element (<200ms target)."""
    return await navigator.click_element(payload.session_id, payload.selector)

@router.post("/forms/fill", dependencies=[Depends(verify_session_token)])
async def fill_form(payload: FormFillRequest):
    """Fills form input fields."""
    return await form_auto.fill_form_fields(payload.session_id, payload.field_data)

@router.post("/scrape/table", dependencies=[Depends(verify_session_token)])
async def scrape_table(payload: ScrapeTableRequest):
    """Extracts structured JSON tabular data from page HTML."""
    return scraper.extract_structured_table(payload.html_content)

@router.post("/monitor/register", dependencies=[Depends(verify_session_token)])
async def register_monitor(payload: MonitorRegisterRequest):
    """Registers website change monitor target."""
    success = monitor_svc.register_monitor_target(
        url=payload.url,
        selector=payload.selector,
        target_type=payload.target_type or "price_drop"
    )
    return {"status": "SUCCESS" if success else "FAILED"}

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics_metrics():
    """Queries dashboard performance latency summary."""
    return telemetry.get_performance_summary()
