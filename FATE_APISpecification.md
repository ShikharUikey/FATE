# Project FATE — API Specification
**Version:** 0.1.0 (Core)  
**Host Binding:** Local Loopback only (`127.0.0.1` / `localhost`)  
**Status:** Approved Endpoint Contract  

---

## 1. Local Security & Authentication Model

To prevent malicious local processes from accessing FATE's APIs:
1. **Loopback Lock:** The FastAPI backend daemon binds exclusively to the loopback interface (`127.0.0.1`). Any external request arriving from a network interface is dropped.
2. **Startup Handshake Token:**
   - At launch, the FastAPI backend generates a high-entropy cryptographically secure random token (64-character hex string).
   - The token is written to a temporary JSON configuration file within the user's home app directory (`~/.gemini/antigravity/fate_session.json`), which is restricted by OS filesystem permissions (`chmod 600`) to the current logged-in user.
   - The Tauri frontend client reads this file at startup and injects the token into all HTTP requests via the custom header: `X-FATE-Token: <token>`.
   - The token is validated for WebSocket handshakes using the query parameter: `ws://127.0.0.1:8000/ws/events?token=<token>`.

---

## 2. REST API Specification

### 2.1 AI Brain Interface

#### POST `/api/v1/brain/query`
Processes natural language user requests, returns assistant responses, and outlines generated plans if multi-step orchestration is triggered.

* **Request Headers:**
  * `X-FATE-Token: <token>`
  * `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "query": "Schedule a meeting with Bob tomorrow at 10 AM and email him the draft document",
    "voice_mode": false
  }
  ```
* **Response (Success - 200 OK):**
  ```json
  {
    "query_id": "8f8b8a89-2c2d-4e4f-8a8b-8c8d8e8f8a8b",
    "intent": "CreateMeetingAndEmail",
    "response_text": "I have created the meeting and sent the email draft to Bob.",
    "plan_triggered": true,
    "plan_id": "a9a8a7a6-b5b4-c3c2-d1d0-e9e8e7e6e5e4"
  }
  ```

---

### 2.2 Agent Orchestrator & Task Queue Interface

#### GET `/api/v1/orchestrator/tasks`
Retrieves a list of all items currently in the orchestrator scheduling queue.

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Response (200 OK):**
  ```json
  [
    {
      "id": "c1c2c3c4-d5d6-e7e8-f9f0-a1a2a3a4a5a6",
      "plan_id": "a9a8a7a6-b5b4-c3c2-d1d0-e9e8e7e6e5e4",
      "agent_name": "CalendarAgent",
      "command": "schedule_event",
      "status": "Success",
      "priority": "Normal",
      "dependencies": [],
      "error_message": null,
      "created_at": "2026-07-20T21:45:00Z"
    },
    {
      "id": "b1b2b3b4-c5c6-d7d8-e9e0-f1f2f3f4f5f6",
      "plan_id": "a9a8a7a6-b5b4-c3c2-d1d0-e9e8e7e6e5e4",
      "agent_name": "CommunicationAgent",
      "command": "send_email",
      "status": "Pending",
      "priority": "Normal",
      "dependencies": ["c1c2c3c4-d5d6-e7e8-f9f0-a1a2a3a4a5a6"],
      "error_message": null,
      "created_at": "2026-07-20T21:45:01Z"
    }
  ]
  ```

#### GET `/api/v1/orchestrator/tasks/{task_id}/status`
Retrieves the execution status of a single task block.

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Response (200 OK):**
  ```json
  {
    "task_id": "b1b2b3b4-c5c6-d7d8-e9e0-f1f2f3f4f5f6",
    "status": "Running",
    "retry_count": 0,
    "error_message": null
  }
  ```

#### POST `/api/v1/orchestrator/tasks/{task_id}/control`
Dispatches scheduling controls to alter execution paths (pause, resume, or cancel active execution steps).

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Request Body:**
  ```json
  {
    "action": "cancel" 
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "task_id": "b1b2b3b4-c5c6-d7d8-e9e0-f1f2f3f4f5f6",
    "action_triggered": "cancel",
    "success": true
  }
  ```

---

### 2.3 Plugin Manager Interface

#### GET `/api/v1/plugins`
Lists all installed plugins, version specifications, and runtime enable states.

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Response (200 OK):**
  ```json
  [
    {
      "id": "github-mcp-server",
      "name": "GitHub Integration",
      "version": "1.2.0",
      "is_enabled": true,
      "permissions": ["network_access", "secrets_read"]
    }
  ]
  ```

#### POST `/api/v1/plugins/install`
Triggers installation and signature verification loops for new plugins.

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Request Body:**
  ```json
  {
    "plugin_source": "/Users/user/Downloads/github-plugin.zip"
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "id": "github-mcp-server",
    "status": "Installed",
    "manifest_hash": "a8a9fa782b3d8c1992f0293da7e72b3819e902bcf928b18a28f8021a8d18a1a9"
  }
  ```

#### DELETE `/api/v1/plugins/{plugin_id}`
Unregisters and uninstalls a plugin from the local agent system directory.

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Response (200 OK):**
  ```json
  {
    "id": "github-mcp-server",
    "status": "Uninstalled"
  }
  ```

---

### 2.4 System Settings Interface

#### GET `/api/v1/settings`
Retrieves system-wide configurations, selected speech models, local paths, and security policy rules.

* **Request Headers:**
  * `X-FATE-Token: <token>`
* **Response (200 OK):**
  ```json
  {
    "active_llm_provider": "ollama",
    "active_model_name": "llama3",
    "voice_input_enabled": true,
    "log_retention_days": 30,
    "whitelisted_directories": [
      "/Users/user/Downloads",
      "/Users/user/Documents/FATE_Workspace"
    ]
  }
  ```

#### PATCH `/api/v1/settings`
Surgically updates configuration parameters.

* **Request Headers:**
  * `X-FATE-Token: <token>`
  * `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "active_llm_provider": "openai",
    "active_model_name": "gpt-4-turbo"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "status": "Updated",
    "settings": {
      "active_llm_provider": "openai",
      "active_model_name": "gpt-4-turbo",
      "voice_input_enabled": true,
      "log_retention_days": 30,
      "whitelisted_directories": [
        "/Users/user/Downloads",
        "/Users/user/Documents/FATE_Workspace"
      ]
    }
  }
  ```

---

## 3. WebSocket Real-Time Channels

### 3.1 Real-Time System Event Stream: `/ws/events`
Streams task state updates, agent executions, logs, and notification payloads dynamically.

* **Message Structure (JSON):**
  ```json
  {
    "event_type": "task_updated",
    "timestamp": "2026-07-20T21:45:02Z",
    "payload": {
      "task_id": "b1b2b3b4-c5c6-d7d8-e9e0-f1f2f3f4f5f6",
      "status": "Success",
      "agent_name": "CommunicationAgent"
    }
  }
  ```

### 3.2 Real-Time Audio Streaming Channel: `/ws/voice`
Transfers binary voice audio chunks. Raw 16kHz, 16-bit Mono PCM audio chunks are streamed client-to-server (for STT) and server-to-client (for TTS).

* **Message Structure:**
  * **Frame Header (First 4 bytes):** Packet definition flag (0x01: Audio Data, 0x02: Control Signal like Start/Stop speaking).
  * **Payload Data (Binary):** Raw PCM audio bytes.

---

## 4. Model Context Protocol (MCP) Integration

All tool integrations follow the Model Context Protocol standards. The Tool Gateway maps local command processes and registers them.

```
FATE Gateway (Client) ◄─── JSON-RPC over Stdio ───► MCP Server (Tool Host)
```

### 4.1 Schema registration (`tools/list` request)
Sent from FATE client to register the MCP server capabilities.

* **Request Schema:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }
  ```
* **Response Schema:**
  ```json
  {
    "jsonrpc": "2.0",
    "result": {
      "tools": [
        {
          "name": "execute_github_search",
          "description": "Searches repositories on GitHub matching query string parameters.",
          "inputSchema": {
            "type": "object",
            "properties": {
              "query": { "type": "string" }
            },
            "required": ["query"]
          }
        }
      ]
    },
    "id": 1
  }
  ```

### 4.2 Tool Execution (`tools/call` request)
Sent from FATE client to trigger tool actions.

* **Request Schema:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_github_search",
      "arguments": {
        "query": "Antigravity FATE"
      }
    },
    "id": 2
  }
  ```
* **Response Schema:**
  ```json
  {
    "jsonrpc": "2.0",
    "result": {
      "content": [
        {
          "type": "text",
          "text": "Repository 'Antigravity/FATE' found with 5 stars."
        }
      ]
    },
    "id": 2
  }
  ```
