from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.security import initialize_security_token, verify_session_token
from backend.app.core.db import init_db
from backend.app.api.brain_routes import router as brain_router
from backend.app.api.memory_routes import router as memory_router
from backend.app.api.voice_routes import router as voice_router, ws_router as voice_ws_router
from backend.app.knowledge_graph.api.router import router as kg_router
from backend.app.tools_ecosystem.api.router import router as tools_router
from backend.app.mcp.api.routes import router as mcp_router
from backend.app.desktop_os.api.routes import router as desktop_router

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

# Initialize startup security handshake token
initialize_security_token()

# Initialize Database tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include routers
app.include_router(brain_router)
app.include_router(memory_router)
app.include_router(voice_router)
app.include_router(voice_ws_router)
app.include_router(kg_router)
app.include_router(tools_router)
app.include_router(mcp_router)
app.include_router(desktop_router)

@app.get("/api/v1/health", dependencies=[Depends(verify_session_token)])
async def get_health_status():
    """System health check endpoint."""
    return {"status": "online", "engine": "FATE Core v0.1.0"}

