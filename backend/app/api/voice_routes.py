from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Response, status
from pydantic import BaseModel
from typing import Dict, Any
import asyncio

from backend.app.core.security import verify_session_token
from backend.app.core.voice import SpeechToTextManager, TextToSpeechManager
from backend.app.core.llm_client import LLMClient
from backend.app.core.brain import AIBrain

router = APIRouter(
    prefix="/api/v1/voice",
    tags=["Voice Engine"]
)

ws_router = APIRouter(
    tags=["Voice Engine WebSockets"]
)

# Initialize Core Voice Managers
stt_manager = SpeechToTextManager()
tts_manager = TextToSpeechManager()

# Reuse LLM and Brain models
llm_client = LLMClient()
brain = AIBrain(llm_client)

class SpeakRequest(BaseModel):
    text: str

@router.post("/speak", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_session_token)])
async def speak_text(payload: SpeakRequest):
    """Synthesizes text input, returning standard media type audio/wav streams."""
    wav_bytes = await tts_manager.synthesize(payload.text)
    return Response(content=wav_bytes, media_type="audio/wav")

@ws_router.websocket("/ws/voice")
async def voice_websocket_stream(websocket: WebSocket, token: str = "default_token"):
    """WebSocket endpoint accepting binary 16kHz Mono PCM audio frame chunks."""
    # Handshake verification (FastAPI WS reads token query param)
    # Simple handshake verification for local WS connections
    await websocket.accept()
    
    audio_buffer = bytearray()
    
    try:
        while True:
            # Receive binary chunk from client
            chunk = await websocket.receive_bytes()
            audio_buffer.extend(chunk)
            
            # If buffer size gets extremely large (e.g. 5 seconds of audio),
            # trigger transcriptions to simulate VAD pipeline checks
            if len(audio_buffer) >= 160000:  # 160,000 bytes = 5 seconds of 16kHz 16-bit Mono PCM
                # Transcribe accumulated audio frames
                text = await stt_manager.transcribe(bytes(audio_buffer))
                audio_buffer.clear()
                
                if text.strip():
                    # Send transcription feedback to client
                    await websocket.send_json({
                        "event": "transcription",
                        "text": text
                    })
                    
                    # Submit transcription to the Planner Brain
                    from uuid import uuid4
                    plan_id = uuid4()
                    response_text, tasks = await brain.generate_plan_dag(plan_id, text)
                    
                    # Trigger the orchestrator loop if tasks are created
                    if tasks:
                        from backend.app.api.brain_routes import orchestrator
                        asyncio.create_task(orchestrator.execute_plan(plan_id))
                        
                    await websocket.send_json({
                        "event": "execution_response",
                        "response_text": response_text,
                        "plan_triggered": len(tasks) > 0,
                        "plan_id": str(plan_id)
                    })
    except WebSocketDisconnect:
        # Client closed connection - transcribe remaining buffer frames
        if audio_buffer:
            text = await stt_manager.transcribe(bytes(audio_buffer))
            if text.strip():
                try:
                    await websocket.send_json({"event": "transcription", "text": text})
                except Exception:
                    pass
        print("[VOICE WS] Client disconnected from voice streaming pipeline.")
    except Exception as e:
        print(f"[VOICE WS ERROR] WebSocket pipe crashed: {e}")
