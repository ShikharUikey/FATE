# Project FATE — Technology Stack Specification
**Version:** 0.1.0 (Core)  
**Target Platform:** macOS 15 Sequoia (Apple Silicon M-Series)  
**Status:** Approved Architectural Blueprint  

---

## 1. Core Languages & Runtime Environments

To meet the requirements of local-first execution, speed, and safety, Project FATE employs three core runtimes:

### 1.1 Python Runtime (Backend & Intelligence Layer)
* **Version:** Python 3.11.x (LTS)
* **Rationale:** Python 3.11 offers a 10-60% execution speedup over 3.10 and is widely supported by local machine learning, vector search, and OS accessibility libraries.
* **Package Manager:** `uv` (high-speed Rust-based Python package installer and virtual environment manager).

### 1.2 Node.js Runtime (Frontend Compilation Layer)
* **Version:** Node.js 20.x (LTS)
* **Rationale:** Provides the compilation environment for the Next.js user interface.
* **Package Manager:** `pnpm` (fast, disk-space-efficient package manager).

### 1.3 Rust Runtime (Desktop Application Shell)
* **Version:** Rust 1.75+
* **Rationale:** Used exclusively to compile the **Tauri v2** desktop binary, ensuring native platform performance and lightweight system interactions.

---

## 2. Web Frameworks & Desktop Application Shell

The user interface and backend APIs are decoupled, running locally inside a secure platform-native wrapper.

```
┌────────────────────────────────────────────────────────┐
│                        TAURI v2                        │
│                 (macOS WebKit WebView)                 │
│  ┌───────────────────────┐   ┌──────────────────────┐  │
│  │   Next.js Frontend    │◄─►│   FastAPI Backend    │  │
│  │    (Static HTML5)     │   │  (Uvicorn Loopback)  │  │
│  └───────────────────────┘   └──────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 2.1 Desktop Shell: Tauri v2
* **Framework:** Tauri v2
* **Rationale:** Tauri renders the user interface using the native macOS system web view (WebKit), producing lightweight binaries (~10-15MB) that consume less than 50MB of RAM when idle. This directly satisfies NFR-PER-005 and avoids the massive overhead of packaging Chromium (e.g. Electron).

### 2.2 Frontend Framework: Next.js
* **Framework:** Next.js 14.x (App Router, Static HTML Export)
* **Styling:** Vanilla CSS (satisfying standard UI constraints) for high-performance rendering and a custom typography system.

### 2.3 Backend API Server: FastAPI
* **Framework:** FastAPI 0.110.0+ (running on Uvicorn local loopback: `127.0.0.1`)
* **Rationale:** High-performance asynchronous API framework utilizing ASGI. It supports automatic OpenAPI schema generation, integrated Pydantic validations, and native Python coroutines.

---

## 3. Database Layer & Local Storage

Local data is structured, secure, and optimized for concurrent read/write activities.

### 3.1 Database ORM: SQLModel
* **Library:** SQLModel 0.0.16+
* **Rationale:** SQLModel merges SQLAlchemy (robust ORM execution) and Pydantic (data validation) into a single model declaration. This eliminates schema duplication between database tables and API models.

### 3.2 SQL Database Engine: SQLite 3.45+
* **Engine:** Local SQLite
* **Concurrency Configuration:**
  * **Write-Ahead Logging (WAL) Mode:** Enabled (`PRAGMA journal_mode=WAL;`), permitting concurrent read transactions during active writes.
  * **Centralized Write Queue:** A singleton `WriteManager` class running an asynchronous `asyncio.Queue` worker on a single thread. All write operations from agents must be pushed to this queue to prevent database lockups (`database is locked` errors).

### 3.3 Secrets Vault: Encrypted Local SQLite
* **Encryption Library:** `cryptography` (Python Fernet AES-256)
* **Storage:** Credentials, tokens, and keys are stored encrypted in a separate SQLite database file, with encryption keys secured via the macOS Keychain.

---

## 4. Local Machine Learning & Voice Engines

FATE executes all core cognitive and speech functions locally without requiring internet access.

### 4.1 Speech-to-Text (STT) Engine: Faster-Whisper
* **Model:** `faster-whisper` (CTranslate2 port of OpenAI's Whisper model)
* **Model Size:** `base` or `small` (quantized to `int8`) running locally.
* **Hardware Acceleration:** Executed on the Apple Silicon GPU/ANE (Apple Neural Engine) via CoreML or CPU-optimized ONNX threads.

### 4.2 Text-to-Speech (TTS) Engine: Piper
* **Engine:** `piper` (local fast neural text-to-speech)
* **Rationale:** Piper is written in C++ and outputs high-quality voice audio in real-time, requiring minimal CPU resources.
* **Backup:** Text-only interface in the Tauri console if audio output is unavailable.

### 4.3 Vector Search & Embeddings Engine: Qdrant Local Client
* **Vector DB:** Qdrant Client (running in local disk-backed storage mode)
* **Rationale:** Qdrant's Python client supports running a fully local, disk-persisted vector search database without requiring a background Docker engine. It handles hybrid keyword/semantic search and fast metadata filtering.
* **Embeddings Model:** `fastembed` (running the `sentence-transformers/all-MiniLM-L6-v2` model via ONNX runtime).

### 4.4 Large Language Model Abstraction Interface
* **Abstraction:** Custom lightweight client wrapper in Python.
* **Local Run:** Communicates with Ollama or LM Studio over local HTTP loopbacks.
* **Cloud Run:** Direct HTTP integrations with OpenAI, Anthropic, and Google Gemini API endpoints, accompanied by setup warning alerts.

---

## 5. Agent-Specific Technologies & Libraries

Every FATE Specialized Agent is backed by optimized macOS-native libraries:

| Agent | Library / Driver | Purpose |
| :--- | :--- | :--- |
| **Desktop Agent** | `PyObjC` (AppKit, PyWindow) | Native macOS Cocoa API bindings for window resizing, layout queries, and simulated events. |
| **Browser Agent** | `Playwright Python` | Headless/headed browser session driver for Chromium, Firefox, and WebKit. |
| **File System Agent**| Python `os`, `shutil`, `watchdog` | High-speed POSIX directory traversal and local change monitoring. |
| **Calendar Agent** | `google-auth`, `google-api-python-client`| Google Calendar sync via local OAuth 2.0 token ingestion. |
| **Communication Agent**| `google-api-python-client` | Gmail mailbox sync and drafts injection. |
| **Coding Agent** | `subprocess`, `GitPython` | Terminal control loops, linter logs parse utilities, and local Git actions. |
| **Vision Agent** | `PyObjC` (Apple Vision Framework) | Native Apple Silicon hardware-accelerated OCR and document text parsing (no external binary required). |

---

## 6. Sandboxing & Plugin Safety

### 6.1 Native Sandboxing (Primary)
* **Engine:** macOS `sandbox-exec` utility (App Sandbox profiles).
* **Rationale:** Leverages the native macOS kernel sandboxing mechanism to isolate third-party plugin directory operations, network sockets, and process boundaries without virtualization overhead.

### 6.2 Containerized Sandboxing (Optional)
* **Engine:** Docker Desktop (macOS virtualization).
* **Rationale:** Reserved exclusively for advanced developer workflows, isolated multi-process servers, or containerized testing pipelines.

---

## 7. Model Context Protocol (MCP)

* **Client SDK:** `@modelcontextprotocol/sdk` (Node.js) and `mcp` (Python).
* **Communication Transport:** JSON-RPC 2.0 over Stdio (standard input/output pipes) for local subprocess servers, and WebSocket transport for remote utility integrations.
