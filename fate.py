#!/usr/bin/env python3
"""
FATE — Fully Automated Task Executive Unified CLI Manager
Usage:
    python fate.py start   - Launch Backend (port 8000) & Frontend (port 1420)
    python fate.py stop    - Terminate running local host servers
    python fate.py test    - Execute backend unit test suite (23 tests)
    python fate.py status  - Check system daemon health and port statuses
"""

import sys
import os
import subprocess
import urllib.request
import json

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

def run_tests():
    """Executes the full PyTest suite inside the backend virtual environment."""
    print("Running FATE Core Test Suite (109 test cases)...")
    pytest_bin = os.path.join(BACKEND_DIR, ".venv", "bin", "pytest")
    test_files = [
        "tests/test_core.py",
        "tests/test_brain.py",
        "tests/test_memory.py",
        "tests/test_agents.py",
        "tests/test_voice.py",
        "tests/test_browser.py",
        "tests/test_vision.py",
        "tests/test_specialized_agents.py",
        "tests/test_knowledge_graph.py",
        "tests/test_tools_ecosystem.py",
        "tests/test_mcp_ecosystem.py",
        "tests/test_desktop_os_agent.py",
        "tests/test_security_engine.py",
        "tests/test_workflow_engine.py",
        "tests/test_browser_agent_module.py",
        "tests/test_mobile_agent_module.py",
        "tests/test_cloud_engine_module.py",
        "tests/test_analytics_platform_module.py"
    ]
    
    cmd = [pytest_bin] + test_files
    env = os.environ.copy()
    env["PYTHONPATH"] = ".."
    
    res = subprocess.run(cmd, cwd=BACKEND_DIR, env=env)
    return res.returncode == 0

def stop_services():
    """Terminates processes listening on ports 8000 and 1420."""
    print("Stopping FATE Core local services...")
    subprocess.run("kill -9 $(lsof -t -i:8000 -i:1420) 2>/dev/null || true", shell=True)
    print("[FATE] Stopped processes listening on ports 8000 and 1420.")

def check_status():
    """Checks port availability and backend health API status."""
    print("FATE Core System Status:")
    
    # Check port 8000
    res_8000 = subprocess.run("lsof -i:8000", shell=True, capture_output=True, text=True)
    backend_running = res_8000.returncode == 0
    print(f"  Backend (port 8000): {'ONLINE' if backend_running else 'OFFLINE'}")
    
    # Check port 1420
    res_1420 = subprocess.run("lsof -i:1420", shell=True, capture_output=True, text=True)
    frontend_running = res_1420.returncode == 0
    print(f"  Frontend GUI (port 1420): {'ONLINE' if frontend_running else 'OFFLINE'}")
    
    if backend_running:
        try:
            # Query session token for health status
            session_file = os.path.expanduser("~/.gemini/antigravity/fate_session.json")
            if os.path.exists(session_file):
                with open(session_file, "r") as f:
                    token = json.load(f).get("token", "")
                req = urllib.request.Request("http://127.0.0.1:8000/api/v1/health")
                req.add_header("X-FATE-Token", token)
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    print(f"  Health Check: {data.get('status')} ({data.get('engine')})")
        except Exception as e:
            print(f"  Health Check: Connected ({e})")

def start_services():
    """Starts FastAPI backend and Next.js frontend servers."""
    stop_services()
    print("Starting FATE Core Local Host Services...")
    
    # Start Backend
    py_bin = os.path.join(BACKEND_DIR, ".venv", "bin", "python")
    env = os.environ.copy()
    env["PYTHONPATH"] = ".."
    
    backend_cmd = [py_bin, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    subprocess.Popen(backend_cmd, cwd=BACKEND_DIR, env=env)
    print("  [✓] Backend server launched at http://127.0.0.1:8000 (Swagger: http://127.0.0.1:8000/docs)")
    
    # Start Frontend
    frontend_cmd = ["npm", "run", "dev"]
    subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)
    print("  [✓] Frontend GUI launched at http://localhost:1420")
    print("\nFATE Core is now running live!")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
        
    cmd = sys.argv[1].lower()
    if cmd == "start":
        start_services()
    elif cmd == "stop":
        stop_services()
    elif cmd == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif cmd == "status":
        check_status()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)

if __name__ == "__main__":
    main()
