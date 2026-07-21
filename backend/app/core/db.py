import os
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = os.path.abspath(os.path.expanduser("~/.gemini/antigravity/fate_core.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create the engine with thread sharing enabled for asynchronous support
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

from sqlalchemy import text

def init_db():
    """Configures the database, activates WAL mode, and initializes tables."""
    with engine.connect() as conn:
        # Enforce WAL mode for safe concurrent reads
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA synchronous=NORMAL;"))
    
    # Import schemas here to register with SQLModel
    from backend.app.models.schemas import (
        CoreSettings, RegisteredPlugins, TaskQueue,
        MemoryNodes, MemoryEdges, MemoryObservations,
        ExecutionTraces, AuditLogs
    )
    from backend.app.knowledge_graph.entities.models import EntityRecord, EntityVersionRecord
    from backend.app.knowledge_graph.relationships.engine import RelationshipRecord
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency provider yielding active SQLite sessions."""
    with Session(engine) as session:
        yield session
