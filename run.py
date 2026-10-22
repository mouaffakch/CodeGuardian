import os
import sys
from pathlib import Path
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()

    root_dir = Path(__file__).resolve().parent
    backend_dir = root_dir / "backend"

    # Add backend directory to sys.path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Detect virtualenv python if run from global python
    venv_python = backend_dir / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = backend_dir / ".venv" / "bin" / "python"

    if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
        import subprocess
        cmd = [str(venv_python), str(backend_dir / "run_backend.py")]
        sys.exit(subprocess.call(cmd))
    else:
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        print(f"[*] Starting CodeGuardian Server on http://localhost:{port}")
        app_dir = str(backend_dir / "app")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            reload_dirs=[app_dir]
        )
