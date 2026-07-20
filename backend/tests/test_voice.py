import pytest
import json
import wave
import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.voice import SpeechToTextManager, TextToSpeechManager
from backend.app.core.security import SESSION_FILE

client = TestClient(app)

@pytest.mark.asyncio
async def test_stt_transcription_fallback():
    """Verify STT fallback returns mock transcriptions."""
    stt = SpeechToTextManager(model_size="tiny")
    # Empty bytes returns empty string
    assert await stt.transcribe(b"") == ""
    
    # Non-empty bytes trigger transcription
    res = await stt.transcribe(b"\x00\x00" * 1000)
    assert res == "Schedule meeting with Bob and email him"

@pytest.mark.asyncio
async def test_tts_wav_synthesis():
    """Verify TTS synthesis generates standard, playable WAV bytes."""
    tts = TextToSpeechManager()
    wav_bytes = await tts.synthesize("Hello FATE voice engine")
    assert len(wav_bytes) > 44  # WAV header is 44 bytes minimum
    
    # Read WAV container formatting properties
    wav_io = io.BytesIO(wav_bytes)
    with wave.open(wav_io, "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 16000

def test_speak_route():
    """Verify that POST /api/v1/voice/speak synthesizes speech."""
    with open(SESSION_FILE, "r") as f:
        token = json.load(f)["token"]
        
    response = client.post(
        "/api/v1/voice/speak",
        headers={"X-FATE-Token": token},
        json={"text": "Speaking aloud."}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 44

def test_voice_websocket():
    """Verify that WebSocket /ws/voice accepts connections and streams PCM."""
    # Test client websocket connection
    with client.websocket_connect("/ws/voice") as websocket:
        # Send raw 16kHz audio chunks (160,000 bytes = 5 seconds) to trigger transcription event
        websocket.send_bytes(b"\x00\x00" * 80000)
        
        # Read the STT transcription event response
        data = websocket.receive_json()
        assert data["event"] == "transcription"
        assert data["text"] == "Schedule meeting with Bob and email him"
        
        # Read the planning response event
        resp = websocket.receive_json()
        assert resp["event"] == "execution_response"
        assert resp["plan_triggered"] is True
        assert resp["plan_id"] is not None
        assert "scheduling" in resp["response_text"].lower()
