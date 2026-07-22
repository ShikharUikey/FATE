import pytest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import SESSION_FILE
from backend.app.gemini_live.voice_stream import GeminiLiveAudioStreamEngine
from backend.app.gemini_live.vision_screen import MultimodalVisionScreenAnalyzer
from backend.app.gemini_live.pc_automation import NativePCAutomationDriver
from backend.app.gemini_live.jarvis_bridge import GeminiLiveJARVISBridge
from backend.app.gemini_live.security import GeminiLiveSecurityGuard
from backend.app.gemini_live.analytics import GeminiLiveTelemetryEngine

client = TestClient(app)

@pytest.mark.asyncio
async def test_gemini_live_audio_stream_engine():
    """Verify Gemini Live audio streaming session setup (<100ms processing delay)."""
    engine = GeminiLiveAudioStreamEngine(api_key="AIzaSyTestApiKey123")
    conn = await engine.connect_live_stream()
    assert conn["status"] == "CONNECTED"
    assert conn["latency_ms"] < 100.0
    
    stream = await engine.stream_audio_chunk(b"\x00\x01\x02\x03" * 100)
    assert stream["status"] == "STREAMING"
    assert stream["latency_ms"] < 100.0

@pytest.mark.asyncio
async def test_multimodal_vision_screen_analyzer():
    """Verify webcam frame inspection and desktop screen error troubleshooting."""
    analyzer = MultimodalVisionScreenAnalyzer()
    
    webcam = await analyzer.analyze_webcam_frame("fake_base64_frame")
    assert webcam["status"] == "ANALYZED"
    assert "Circuit Board" in webcam["detected_objects"]
    
    screen = await analyzer.analyze_desktop_screen()
    assert screen["status"] == "ANALYZED"
    assert screen["detected_app"] == "VS Code"

@pytest.mark.asyncio
async def test_native_pc_automation_driver():
    """Verify application launching, YouTube playback, weather, wallpaper, and timers."""
    driver = NativePCAutomationDriver()
    
    app_res = await driver.open_application("VS Code")
    assert app_res["status"] == "EXECUTED"
    
    yt_res = await driver.play_youtube_video("Iron Man Mark XXX JARVIS demo")
    assert yt_res["status"] == "EXECUTED"
    assert "youtube.com" in yt_res["target_url"]
    
    weather_res = await driver.check_live_weather("New York")
    assert weather_res["status"] == "SUCCESS"
    
    wp_res = await driver.change_desktop_wallpaper("/path/to/wallpaper.jpg")
    assert wp_res["status"] == "EXECUTED"
    
    timer_res = await driver.set_timer_or_reminder("Boil Eggs", 300)
    assert timer_res["status"] == "SCHEDULED"

def test_gemini_live_jarvis_bridge():
    """Verify bridging Gemini Live voice/vision intents to JARVIS Kernel & Desktop OS Agent."""
    bridge = GeminiLiveJARVISBridge()
    res = bridge.route_live_command_to_jarvis("open_application", {"app_name": "Terminal"})
    assert res["status"] == "BRIDGED"
    assert res["kernel_routed"] is True

def test_gemini_live_security_and_telemetry():
    """Verify Google AI Studio API key validation and telemetry summary."""
    sec = GeminiLiveSecurityGuard()
    assert sec.validate_api_key("AIzaSyValidKey123") is True
    
    telemetry = GeminiLiveTelemetryEngine()
    summary = telemetry.get_live_telemetry_summary()
    assert summary["avg_audio_stream_latency_ms"] < 100.0
    assert summary["pipeline_bypassed"] is True

def test_gemini_live_rest_endpoints():
    """Verify FastAPI REST API endpoints for Gemini Live Integration."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
    headers = {"X-FATE-Token": token}
    
    # POST /api/v1/gemini-live/connect
    res_conn = client.post("/api/v1/gemini-live/connect", headers=headers, json={"api_key": "AIzaSyTestKey"})
    assert res_conn.status_code == 200
    assert res_conn.json()["status"] == "CONNECTED"
    
    # POST /api/v1/gemini-live/vision/screen
    res_scr = client.post("/api/v1/gemini-live/vision/screen", headers=headers)
    assert res_scr.status_code == 200
    assert res_scr.json()["status"] == "ANALYZED"
    
    # POST /api/v1/gemini-live/automation/open-app
    res_app = client.post("/api/v1/gemini-live/automation/open-app", headers=headers, json={"app_name": "Xcode"})
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "EXECUTED"
    
    # POST /api/v1/gemini-live/automation/youtube
    res_yt = client.post("/api/v1/gemini-live/automation/youtube", headers=headers, json={"query": "FatihMakes Mark XXX"})
    assert res_yt.status_code == 200
    assert res_yt.json()["status"] == "EXECUTED"
    
    # GET /api/v1/gemini-live/analytics
    res_an = client.get("/api/v1/gemini-live/analytics", headers=headers)
    assert res_an.status_code == 200
    assert "avg_audio_stream_latency_ms" in res_an.json()
