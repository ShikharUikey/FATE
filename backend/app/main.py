import os
import secrets
import json
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FATE Core API Daemon",
    version="0.1.0",
    description="Local loopback API endpoints for Fully Automated Task Executive"
)

# CORS configurations - restricts origins strictly to Tauri's local schemes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_FILE = os.path.expanduser("~/.gemini/antigravity/fate_session.json")
STARTUP_TOKEN = ""

def initialize_security_token():
    """Generates a secure startup token and writes it locally for Tauri to read."""
    global STARTUP_TOKEN
    STARTUP_TOKEN = secrets.token_hex(32)
    
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"token": STARTUP_TOKEN}, f)
    
    # Restrict read/write permissions to the current OS user
    os.chmod(SESSION_FILE, 0o600)
    print(f"[SECURITY] Session handshake token written to {SESSION_FILE}")

initialize_security_token()

def verify_session_token(x_fate_token: str = Header(..., alias="X-FATE-Token")):
    """Dependency checker verifying that incoming requests supply the correct token."""
    if x_fate_token != STARTUP_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized local handshake token mismatch."
        )

@app.get("/api/v1/health", dependencies=[Depends(verify_session_token)])
async def get_health_status():
    """System health check endpoint."""
    return {"status": "online", "engine": "FATE Core v0.1.0"}
