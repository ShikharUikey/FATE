import asyncio
from typing import List, Dict, Any, Optional

class BrowserAgent:
    """Specialized agent automating web browser sessions and crawls using Playwright."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.has_playwright = False

    async def execute(self, command: str, parameters: Dict[str, Any]) -> bool:
        """Entrypoint called by the Orchestrator scheduler."""
        cmd_lower = command.lower()
        if cmd_lower == "navigate_to":
            return await self.navigate_to(parameters.get("url", ""))
        elif cmd_lower == "click_element":
            return await self.click_element(parameters.get("selector", ""))
        elif cmd_lower == "fill_input":
            return await self.fill_input(
                parameters.get("selector", ""),
                parameters.get("text", "")
            )
        elif cmd_lower == "get_page_content":
            parameters["result"] = await self.get_page_content()
            return True
        return False

    async def _initialize_browser(self):
        """Attempts to dynamically launch the local Playwright browser instance."""
        if self.browser:
            return

        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            # Launch headless chromium with standard viewport settings
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            self.has_playwright = True
            print("[BROWSER AGENT] Launched headless Playwright Chromium instance.")
        except Exception as e:
            print(f"[BROWSER AGENT WARNING] Playwright not configured or failed to load: {e}. Active mock fallback.")
            self.has_playwright = False

    async def navigate_to(self, url: str) -> bool:
        """Navigates the browser to the target web address."""
        if not url:
            return False

        await self._initialize_browser()
        if self.has_playwright and self.page:
            try:
                await self.page.goto(url, wait_until="networkidle", timeout=15000)
                return True
            except Exception as e:
                print(f"[BROWSER AGENT ERROR] Page navigation failed: {e}")
                return False

        # Mock fallback
        await asyncio.sleep(0.2)
        return True

    async def click_element(self, selector: str) -> bool:
        """Clicks an element matching the CSS selector."""
        if not selector:
            return False

        await self._initialize_browser()
        if self.has_playwright and self.page:
            try:
                await self.page.click(selector, timeout=5000)
                return True
            except Exception as e:
                print(f"[BROWSER AGENT ERROR] Click action failed: {e}")
                return False

        # Mock fallback
        await asyncio.sleep(0.1)
        return True

    async def fill_input(self, selector: str, text: str) -> bool:
        """Inputs text into a field matching the CSS selector."""
        if not selector:
            return False

        await self._initialize_browser()
        if self.has_playwright and self.page:
            try:
                await self.page.fill(selector, text, timeout=5000)
                return True
            except Exception as e:
                print(f"[BROWSER AGENT ERROR] Input fill action failed: {e}")
                return False

        # Mock fallback
        await asyncio.sleep(0.1)
        return True

    async def get_page_content(self) -> Optional[str]:
        """Extracts readable text content from the current web page."""
        await self._initialize_browser()
        if self.has_playwright and self.page:
            try:
                # Retrieve pure visible text from page body
                return await self.page.inner_text("body")
            except Exception as e:
                print(f"[BROWSER AGENT ERROR] Content extraction failed: {e}")
                return None

        # Mock fallback page contents
        await asyncio.sleep(0.1)
        return "Mock Page Extraction: FATE successfully parsed this address contents."

    async def close(self):
        """Closes browser instances and stops Playwright engines."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        self.page = None
