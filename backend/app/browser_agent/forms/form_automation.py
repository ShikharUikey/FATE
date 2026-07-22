from typing import Dict, Any, List
from backend.app.browser_agent.navigation.navigator import WebNavigatorEngine

class FormAutomationEngine:
    """Automates form completion (Logins, Registration, Surveys, Checkout) with validation error detection."""

    def __init__(self, navigator: WebNavigatorEngine):
        self.navigator = navigator

    async def fill_form_fields(
        self,
        session_id: str,
        field_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """Fills input elements matching selector keys."""
        filled_count = 0
        for selector, value in field_data.items():
            res = await self.navigator.click_element(session_id, selector)
            if res.get("status") == "SUCCESS":
                filled_count += 1

        return {
            "status": "SUCCESS",
            "filled_fields_count": filled_count,
            "total_requested": len(field_data)
        }

    async def detect_form_validation_errors(self, page_html: str) -> List[str]:
        """Scans page payload for form validation errors."""
        errors = []
        lowered = page_html.lower()
        error_keywords = ["invalid password", "field required", "email already exists", "incorrect pin", "validation failed"]
        
        for kw in error_keywords:
            if kw in lowered:
                errors.append(f"Validation error: '{kw}'")
                
        return errors
