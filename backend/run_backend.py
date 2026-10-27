import os
import sys
from pathlib import Path
from multiprocessing import freeze_support
import uvicorn

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    freeze_support()
    port = int(os.getenv("PORT", 8000))
    app_dir = str(backend_dir / "app")
    print(f"[*] Starting CodeGuardian Server on http://localhost:{port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[app_dir]
    )
