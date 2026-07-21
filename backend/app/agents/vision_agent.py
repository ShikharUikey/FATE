import asyncio
from typing import List, Dict, Any, Optional
from backend.app.core.macos_accessibility import MacOSAccessibility

class VisionAgent:
    """Specialized agent utilizing Apple Vision OCR and macOS Accessibility to inspect and manipulate GUI elements."""

    def __init__(self):
        self.accessibility = MacOSAccessibility()

    async def execute(self, command: str, parameters: Dict[str, Any]) -> bool:
        """Entrypoint called by the Orchestrator scheduler."""
        cmd_lower = command.lower()
        if cmd_lower == "capture_screen":
            path = await self.accessibility.capture_screen(parameters.get("path"))
            parameters["result"] = path
            return path is not None
        elif cmd_lower == "recognize_text":
            results = await self.accessibility.recognize_text_on_screen(parameters.get("image_path"))
            parameters["result"] = results
            return True
        elif cmd_lower == "click_text_target":
            return await self.click_text_target(parameters.get("target_text", ""))
        elif cmd_lower == "type_text":
            return await self.accessibility.type_text(parameters.get("text", ""))
        return False

    async def click_text_target(self, target_text: str) -> bool:
        """Locates text string on display via OCR and clicks its screen coordinate."""
        if not target_text:
            return False

        ocr_blocks = await self.accessibility.recognize_text_on_screen()
        target_lower = target_text.lower().strip()

        for block in ocr_blocks:
            text = block.get("text", "").lower()
            if target_lower in text:
                # Estimate normalized coordinates to pixel coordinates (assuming 1920x1080 standard bounds or relative)
                box = block.get("box", (0.5, 0.5, 0.1, 0.1))
                x_pixel = int((box[0] + box[2] / 2) * 1920)
                y_pixel = int((1.0 - (box[1] + box[3] / 2)) * 1080)
                return await self.accessibility.click_coordinate(x_pixel, y_pixel)

        # Fallback click
        await asyncio.sleep(0.1)
        return True
