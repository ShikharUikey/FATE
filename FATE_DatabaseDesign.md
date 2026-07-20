# Project FATE — Database Design Specification
**Version:** 0.1.0 (Core)  
**Database Engines:** SQLite 3.45+ (Relational/Graph) & Qdrant Client (Vector Storage)  
**Status:** Approved Schema Blueprint  

---

## 1. SQLite Relational Database Architecture

FATE uses SQLite 3.45+ as its primary relational engine, configured in **Write-Ahead Logging (WAL) Mode** to support concurrent reads and serialized writes. All database writes are managed by a centralized, single-threaded asynchronous worker queue.

### 1.1 SQLModel Classes & Schemas

The following sections define the SQLModel schemas for the core configuration, execution tracking, memory graph, and audit logging layers.

```
                  ┌──────────────────────┐
                  │    core_settings     │
                  └──────────────────────┘
                  ┌──────────────────────┐
                  │  registered_plugins  │
                  └──────────────────────┘
                             ▲
                             │ (plugin_id)
                  ┌──────────┴───────────┐
                  │      task_queue      │
                  └──────────────────────┘
                             ▲
                             │ (trace_id)
                  ┌──────────┴───────────┐
                  │   execution_traces   │
                  └──────────────────────┘
                             ▲
                             │ (trace_id)
                  ┌──────────┴───────────┐
                  │      audit_logs      │
                  └──────────────────────┘
                             ▲
                             │ (node_id)
                  ┌──────────┴───────────┐
                  │     memory_nodes     │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼ (source_node)                   ▼ (target_node)
  ┌───────────────────┐             ┌───────────────────┐
  │   memory_edges    │             │   memory_edges    │
  └───────────────────┘             └───────────────────┘
```

---

## 2. Core Configuration & Settings Layer

### 2.1 table: `core_settings`
Stores FATE system-wide variables and operational key-value settings.

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class CoreSettings(SQLModel, table=True):
    __tablename__ = "core_settings"
    
    key: str = Field(primary_key=True, max_length=255, index=True)
    value: str = Field(nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### 2.2 table: `registered_plugins`
Registers active plugins, safety scopes, and individual user-defined configuration JSONs.

```python
class RegisteredPlugins(SQLModel, table=True):
    __tablename__ = "registered_plugins"
    
    id: str = Field(primary_key=True, max_length=100, index=True)
    name: str = Field(nullable=False, max_length=255)
    version: str = Field(nullable=False, max_length=50)
    manifest_hash: str = Field(nullable=False, max_length=64)
    is_enabled: bool = Field(default=True, nullable=False)
    permissions: str = Field(nullable=False)  # JSON-serialized array of requested system permissions
    settings: str = Field(default="{}", nullable=False)  # JSON-serialized key-value plugin options
    installed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

---

## 3. Tasks & Execution Scheduling Layer

### 3.1 table: `task_queue`
Manages task dependencies, scheduling states, and execution histories inside the Agent Orchestrator.

```python
from uuid import UUID, uuid4

class TaskQueue(SQLModel, table=True):
    __tablename__ = "task_queue"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    plan_id: UUID = Field(nullable=False, index=True)
    agent_name: str = Field(nullable=False, max_length=100)
    command: str = Field(nullable=False, max_length=255)
    parameters: str = Field(default="{}", nullable=False)  # JSON-serialized arguments
    status: str = Field(default="Pending", nullable=False, max_length=50, index=True)  # Pending, Running, Success, Failed, Suspended
    priority: str = Field(default="Normal", nullable=False, max_length=50)  # Critical, High, Normal, Low, Background
    retry_count: int = Field(default=0, nullable=False)
    dependencies: str = Field(default="[]", nullable=False)  # JSON-serialized array of parent Task UUIDs
    error_message: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    started_at: Optional[datetime] = Field(default=None, nullable=True)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)
```

---

## 4. Memory Graph Layer (Relational Semantic Index)

To map human-like associations (e.g., "Alice works on FATE", "FATE is a Project"), FATE builds a semantic graph using relational node and edge tables.

### 4.1 table: `memory_nodes`
Stores entities (subjects/objects) inside the Memory Engine.

```python
class MemoryNodes(SQLModel, table=True):
    __tablename__ = "memory_nodes"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    entity_name: str = Field(nullable=False, max_length=255, index=True)
    entity_type: str = Field(nullable=False, max_length=100, index=True)  # User, Contact, Project, File, Location, Preference, Fact
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### 4.2 table: `memory_edges`
Stores directional semantic relationships (links/predicates) between nodes.

```python
class MemoryEdges(SQLModel, table=True):
    __tablename__ = "memory_edges"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    source_node_id: UUID = Field(foreign_key="memory_nodes.id", nullable=False, index=True)
    target_node_id: UUID = Field(foreign_key="memory_nodes.id", nullable=False, index=True)
    relation_type: str = Field(nullable=False, max_length=100, index=True)  # likes, works_on, contact_of, located_at, knows
    weight: float = Field(default=1.0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### 4.3 table: `memory_observations`
Contains the raw natural language sentences that spawned the graph nodes. Used for history lookups.

```python
class MemoryObservations(SQLModel, table=True):
    __tablename__ = "memory_observations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    raw_text: str = Field(nullable=False)
    source: str = Field(default="user", nullable=False, max_length=100)  # user, email_agent, browser_agent
    importance_score: int = Field(default=1, nullable=False, index=True)  # 1 to 4 scale
    embedding_id: str = Field(nullable=False, max_length=100)  # Maps to Qdrant vector UUID
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

---

## 5. Audit Log & Execution Trace Layer

Designed to ensure transparency and accountability. An automatic partition pruning loop runs in the background to purge logs older than the user-configured retention threshold (default: 30 days).

### 5.1 table: `execution_traces`
Records incoming high-level user prompts and the resulting plans generated by the AI Brain.

```python
class ExecutionTraces(SQLModel, table=True):
    __tablename__ = "execution_traces"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_query: str = Field(nullable=False)
    plan_dag: str = Field(nullable=False)  # JSON-serialized plan schema representation
    outcome: str = Field(nullable=False, max_length=100, index=True)  # Success, Failed, Cancelled
    total_latency_ms: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
```

### 5.2 table: `audit_logs`
Chronologically captures tool executions, permission approvals, and security block alerts.

```python
class AuditLogs(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trace_id: UUID = Field(foreign_key="execution_traces.id", nullable=False, index=True)
    actor: str = Field(nullable=False, max_length=100, index=True)  # core, plugin_id, agent_name
    action: str = Field(nullable=False, max_length=255)  # file_delete, send_mail, execute_shell
    target_resource: str = Field(nullable=False, max_length=512)  # file path, email address, URL
    status: str = Field(nullable=False, max_length=50, index=True)  # Allowed, Blocked, Failed
    details: Optional[str] = Field(default=None, nullable=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
```

---

## 6. SQLite Concurrency Control: Asynchronous Write Manager

To prevent database contention (`sqlite3.OperationalError: database is locked`) under parallel execution loops, FATE implements a centralized asynchronous connection manager:

```python
import asyncio
from sqlmodel import Session, create_engine

# Database Engine Setup (WAL mode forced)
DATABASE_URL = "sqlite:///fate_core.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

with engine.connect() as conn:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

class WriteManager:
    """Centralized, thread-safe asynchronous SQLite writer queue."""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None

    async def start(self):
        self.worker_task = asyncio.create_task(self._process_writes())

    async def execute_write(self, model_instance: SQLModel):
        """Pushes a SQLModel object into the queue and waits for execution."""
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((model_instance, future))
        return await future

    async def _process_writes(self):
        while True:
            model_instance, future = await self.queue.get()
            try:
                # Synchronous database write transaction
                with Session(engine) as session:
                    session.add(model_instance)
                    session.commit()
                    session.refresh(model_instance)
                future.set_result(model_instance)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()
```

---

## 7. Vector Database Collections (Qdrant Client)

FATE isolates its semantic storage into two distinct collections in Qdrant (local disk-backed storage mode).

### 7.1 Collection: `user_memories`
* **Purpose:** Stores vector embeddings of natural language user observations for semantic recall.
* **Vector Dimension:** 384 (derived from `all-MiniLM-L6-v2` embedding model).
* **Distance Metric:** Cosine Distance.
* **Payload Fields:**
  * `observation_id` (string/UUID): Maps directly to `memory_observations.id`.
  * `raw_text` (string): The natural language observation.
  * `importance` (int): Observation score (1 to 4).
  * `timestamp` (int): Unix epoch timestamp.

### 7.2 Collection: `document_chunks`
* **Purpose:** Stores vector embeddings of split text chunks from local documents for RAG lookups.
* **Vector Dimension:** 384 (derived from `all-MiniLM-L6-v2` embedding model).
* **Distance Metric:** Cosine Distance.
* **Payload Fields:**
  * `document_id` (string/UUID): Unique ID for the document source.
  * `chunk_index` (int): Index of the text segment.
  * `file_path` (string): Absolute local file system location of the document.
  * `file_hash` (string): SHA-256 hash of file content.
  * `text` (string): Raw text snippet of the chunk.
  * `created_at` (int): Unix epoch timestamp of indexing.
