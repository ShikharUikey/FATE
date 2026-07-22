#!/usr/bin/env python3
"""
FATE — Fully Automated Task Executive Unified CLI Manager
Usage:
    python3 fate.py chat    - Launch Interactive AI Chatbot Terminal
    python3 fate.py start   - Launch Backend (port 8000) & Frontend (port 1420)
    python3 fate.py stop    - Terminate running local host servers
    python3 fate.py test    - Execute backend unit test suite
    python3 fate.py status  - Check system daemon health and port statuses
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
    print("Running FATE Core Test Suite (Streamlined Chatbot Engine)...")
    pytest_bin = os.path.join(BACKEND_DIR, ".venv", "bin", "pytest")
    test_files = [
        "tests/test_core.py",
        "tests/test_brain.py",
        "tests/test_memory.py",
        "tests/test_agents.py",
        "tests/test_tools_ecosystem.py",
        "tests/test_chatbot_core.py"
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

def run_interactive_chat():
    """Runs interactive terminal chatbot shell."""
    print("\n🤖 JARVIS AI Chatbot Interactive Terminal Shell")
    print("--------------------------------------------------")
    print("Type your questions (Maths, Info Analysis, Everyday Tasks). Type 'exit' to quit.\n")
    
    # Ensure backend server is running or query internal brain directly
    py_bin = os.path.join(BACKEND_DIR, ".venv", "bin", "python")
    code_snippet = (
        "import asyncio\n"
        "from backend.app.core.llm_client import LLMClient\n"
        "from backend.app.core.brain import AIBrain\n"
        "from uuid import uuid4\n\n"
        "async def main():\n"
        "    brain = AIBrain(LLMClient())\n"
        "    while True:\n"
        "        try:\n"
        "            user_input = input('\\nUser > ').strip()\n"
        "            if user_input.lower() in ['exit', 'quit']:\n"
        "                break\n"
        "            if not user_input:\n"
        "                continue\n"
        "            res, tasks = await brain.generate_plan_dag(uuid4(), user_input)\n"
        "            print(f'\\nJARVIS > {res}')\n"
        "        except (KeyboardInterrupt, EOFError):\n"
        "            break\n\n"
        "asyncio.run(main())\n"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR
    subprocess.run([py_bin, "-c", code_snippet], cwd=ROOT_DIR, env=env)

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
    elif cmd in ["chat", "chatbot"]:
        run_interactive_chat()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)

if __name__ == "__main__":
    main()
