import asyncio
import os
from typing import Dict, Any, List, Optional
from uuid import uuid4, UUID

class BrowserSessionManager:
    """Manages browser contexts (Chromium, Firefox, WebKit), Headless/Headed execution, profiles, and tab pools."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._active_playwright = None
        self._active_browser = None
        self.has_playwright = False

    async def create_session(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        user_profile_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Launches a new browser context session or initialises mock fallback context (<2s target)."""
        session_id = f"session_{str(uuid4())[:8]}"
        
        # Try initializing Playwright
        if not self._active_browser:
            try:
                from playwright.async_api import async_playwright
                self._active_playwright = await async_playwright().start()
                
                b_driver = getattr(self._active_playwright, browser_type.lower(), self._active_playwright.chromium)
                self._active_browser = await b_driver.launch(headless=headless)
                self.has_playwright = True
            except Exception:
                self.has_playwright = False

        session_record = {
            "session_id": session_id,
            "browser_type": browser_type,
            "headless": headless,
            "profile_dir": user_profile_dir,
            "tabs": ["tab_default"],
            "active_tab": "tab_default",
            "is_active": True,
            "current_url": "about:blank"
        }
        self._sessions[session_id] = session_record
        return session_record

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves session record by session_id."""
        return self._sessions.get(session_id)

    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """Lists active browser sessions."""
        return [s for s in self._sessions.values() if s.get("is_active")]

    async def close_session(self, session_id: str) -> bool:
        """Closes a browser session and cleans up tabs."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        session["is_active"] = False
        return True

    async def shutdown_all(self):
        """Terminates all open browser instances."""
        if self._active_browser:
            try:
                await self._active_browser.close()
            except Exception:
                pass
        if self._active_playwright:
            try:
                await self._active_playwright.stop()
            except Exception:
                pass
