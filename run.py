import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

# Check venv python
venv_python = backend_dir / ".venv" / "Scripts" / "python.exe"
if not venv_python.exists():
    venv_python = backend_dir / ".venv" / "bin" / "python"

if venv_python.exists() and sys.executable != str(venv_python):
    # Re-launch with the venv python
    import subprocess
    cmd = [str(venv_python), str(backend_dir / "run_backend.py")]
    sys.exit(subprocess.call(cmd))
else:
    import uvicorn
    print("[*] Starting CodeGuardian on http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
