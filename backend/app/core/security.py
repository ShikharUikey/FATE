import os
import secrets
import json
from fastapi import Header, HTTPException, status

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

def verify_session_token(x_fate_token: str = Header(..., alias="X-FATE-Token")):
    """Dependency checker verifying that incoming requests supply the correct token."""
    global STARTUP_TOKEN
    if not STARTUP_TOKEN:
        # Load from file if initialized by another import route
        try:
            with open(SESSION_FILE, "r") as f:
                STARTUP_TOKEN = json.load(f).get("token", "")
        except Exception:
            pass
            
    if x_fate_token != STARTUP_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized local handshake token mismatch."
        )
