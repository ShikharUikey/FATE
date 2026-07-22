from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.app.core.security import verify_session_token
from backend.app.gemini_live.voice_stream import GeminiLiveAudioStreamEngine
from backend.app.gemini_live.vision_screen import MultimodalVisionScreenAnalyzer
from backend.app.gemini_live.pc_automation import NativePCAutomationDriver
from backend.app.gemini_live.jarvis_bridge import GeminiLiveJARVISBridge
from backend.app.gemini_live.security import GeminiLiveSecurityGuard
from backend.app.gemini_live.analytics import GeminiLiveTelemetryEngine

router = APIRouter(
    prefix="/api/v1/gemini-live",
    tags=["Gemini Live Real-Time Voice & Multimodal Assistant (Mark XLIX Integration)"]
)

# Singletons
voice_stream = GeminiLiveAudioStreamEngine()
vision_screen = MultimodalVisionScreenAnalyzer()
pc_automation = NativePCAutomationDriver()
bridge = GeminiLiveJARVISBridge()
security = GeminiLiveSecurityGuard()
telemetry = GeminiLiveTelemetryEngine()

class ConnectStreamPayload(BaseModel):
    api_key: Optional[str] = "GEMINI_LIVE_DEFAULT_KEY"

class WebcamFramePayload(BaseModel):
    frame_base64: str

class OpenAppPayload(BaseModel):
    app_name: str

class YouTubePayload(BaseModel):
    query: str

class WallpaperPayload(BaseModel):
    image_path_or_url: str

class TimerPayload(BaseModel):
    label: str
    duration_seconds: int

@router.post("/connect", dependencies=[Depends(verify_session_token)])
async def connect_live_stream(payload: ConnectStreamPayload):
    """Establishes direct WebSocket session to Gemini Live API."""
    if not security.validate_api_key(payload.api_key or "GEMINI_LIVE_DEFAULT_KEY"):
        raise HTTPException(status_code=400, detail="Invalid Google AI Studio API Key")
    return await voice_stream.connect_live_stream()

@router.post("/vision/webcam", dependencies=[Depends(verify_session_token)])
async def analyze_webcam(payload: WebcamFramePayload):
    """Analyzes physical webcam frame (circuit components, wiring)."""
    return await vision_screen.analyze_webcam_frame(payload.frame_base64)

@router.post("/vision/screen", dependencies=[Depends(verify_session_token)])
async def analyze_screen():
    """Captures and processes desktop screen to troubleshoot code errors."""
    return await vision_screen.analyze_desktop_screen()

@router.post("/automation/open-app", dependencies=[Depends(verify_session_token)])
async def open_app(payload: OpenAppPayload):
    """Launches local OS desktop application."""
    return await pc_automation.open_application(payload.app_name)

@router.post("/automation/youtube", dependencies=[Depends(verify_session_token)])
async def play_youtube(payload: YouTubePayload):
    """Formats and opens YouTube video playback URL."""
    return await pc_automation.play_youtube_video(payload.query)

@router.get("/automation/weather", dependencies=[Depends(verify_session_token)])
async def check_weather(location: str = "Local"):
    """Checks live weather forecast."""
    return await pc_automation.check_live_weather(location=location)

@router.post("/automation/wallpaper", dependencies=[Depends(verify_session_token)])
async def change_wallpaper(payload: WallpaperPayload):
    """Changes desktop wallpaper background image."""
    return await pc_automation.change_desktop_wallpaper(payload.image_path_or_url)

@router.post("/automation/timer", dependencies=[Depends(verify_session_token)])
async def set_timer(payload: TimerPayload):
    """Sets local timer or reminder alert."""
    return await pc_automation.set_timer_or_reminder(payload.label, payload.duration_seconds)

@router.get("/analytics", dependencies=[Depends(verify_session_token)])
async def get_analytics():
    """Queries Gemini Live integration telemetry summary."""
    return telemetry.get_live_telemetry_summary()
