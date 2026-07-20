# FATE — Proceed to the Next Steps

This document outlines the blueprints and specifications for the next three development phases of FATE (Fully Automated Task Executive) on macOS Apple Silicon.

---

## Phase 1: macOS Native Accessibility & Apple Vision Driver (Vision/Desktop Agents)

### 1. Objectives
Enable FATE to visually inspect the screen (OCR) and manipulate graphical UI elements using native macOS Cocoa APIs via `PyObjC` bindings.

### 2. File Mappings
- `backend/app/agents/vision_agent.py` [NEW]
- `backend/app/core/macos_accessibility.py` [NEW]

### 3. Implementation Blueprint
* **Screen Capture (Apple Vision OCR)**:
  Use macOS AppKit (`SIScreenCapture` or `CGWindowListCreateImage`) to grab screen buffers, pass them directly to Apple's native `VNImageRequestHandler` and `VNRecognizeTextRequest` for zero-latency, local on-device OCR without external engine dependencies (like Tesseract).
* **UI Focus Tree Inspection**:
  Call AppKit accessibility wrappers (`AXUIElementCreateSystemWide`) to list window panels, buttons, and text fields.
* **Coordinate Clicks & Key Inputs**:
  Use `CGEventCreateMouseEvent` and `CGEventPost` to dispatch mouse movements, click triggers, and keyboard strokes to target coordinates.

---

## Phase 2: Local ML Weights & ANE Accelerations (Voice Engine)

### 1. Objectives
Integrate local machine learning models for STT (Faster-Whisper) and TTS (Piper ONNX) configured to run locally on Apple Silicon GPU/ANE.

### 2. File Mappings
- `backend/app/services/weights_downloader.py` [NEW]
- `backend/app/core/voice.py` [MODIFY]

### 3. Implementation Blueprint
* **Model Downloader Manager**:
  Write an automated setup script that checks if local model directories exist (`~/.cache/whisper/` and `~/.cache/piper/`), and downloads the Faster-Whisper `tiny.en` and Piper `en_US-lessac-medium.onnx` models on first startup.
* **Accelerated Whisper Inference**:
  Configure `WhisperModel` parameters to use `device="cpu"` (or MPS backend if PyTorch is integrated) with `compute_type="int8"` for ultra-low latency.
* **Piper TTS Synthesizer**:
  Configure Piper command bindings:
  ```bash
  piper --model en_US-lessac-medium.onnx --config en_US-lessac-medium.onnx.json --output_file output.wav
  ```

---

## Phase 3: Tauri Desktop Menu-Bar Wrapper (Client App)

### 1. Objectives
Wrap the Next.js static console UI inside a native Tauri menu bar utility app that controls the FastAPI backend daemon lifecycle.

### 2. File Mappings
- `src-tauri/src/main.rs` [MODIFY]
- `src-tauri/tauri.conf.json` [MODIFY]

### 3. Implementation Blueprint
* **System Tray Configuration**:
  Modify Tauri’s Rust entrypoint to spawn a custom System Tray Menu (containing "Show Console", "Toggle Voice", "Exit").
* **FastAPI Daemon Lifecycle Sidecar**:
  Use Tauri’s Sidecar feature to spawn the python fastapi uvicorn binary/script on startup, and automatically kill the backend process when the Tauri desktop app exits.
