# Project FATE (Fully Automated Task Executive)
> "From Intent to Execution."

FATE is a modular, agentic AI Operating System designed to run locally on macOS Apple Silicon, automating workflows, desktop applications, browsers, files, schedules, and developer actions.

---

## 1. Directory Structure

- `backend/`: FastAPI API loopback service and Specialized Agents (Python).
- `frontend/`: Next.js web settings console and speech indicators (TypeScript/HTML/CSS).
- `src-tauri/`: Tauri v2 Rust wrapper compiling the native desktop application shell.
- `FATE_SRS.md`: Canonical software requirements specification.
- `FATE_TechStack.md`: Frameworks, local ML models, and drivers definitions.
- `FATE_DatabaseDesign.md`: Relational SQLite WAL schemas and Qdrant collections.
- `FATE_APISpecification.md`: REST loopback endpoints and binary WebSocket specifications.

---

## 2. Prerequisites & Setup

### 2.1 Dependencies
Ensure you have the following runtimes installed on your macOS Sequoia workstation:
* **Python 3.11** (LTS)
* **Node.js 20** (LTS)
* **Rust 1.75+** (for Tauri Rust compilations)
* **uv** (for Python environment management: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
* **pnpm** (for Node package management: `npm install -g pnpm`)

### 2.2 Installation

1. **Backend Setup:**
   ```bash
   cd backend
   uv venv --python 3.11
   source .venv/bin/activate
   uv sync
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   pnpm install
   ```

3. **Tauri Rust Setup:**
   Ensure cargo is working locally. Run the dev server to verify:
   ```bash
   # Run from root directory
   pnpm tauri dev
   ```

---

## 3. Local Execution

To start the FATE Core system in development mode:
```bash
# Starts both Next.js frontend rendering and Tauri shell wrapper
pnpm tauri dev
```
The FastAPI backend service is spawned automatically by the Tauri client on startup.
