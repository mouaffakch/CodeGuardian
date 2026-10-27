import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("CODEGUARDIAN_DB_URL", f"sqlite:///{DATA_DIR / 'codeguardian.db'}")

class Settings(BaseModel):
    app_name: str = "CodeGuardian"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    db_url: str = DATABASE_URL
    
    max_cyclomatic_complexity: int = 10
    max_function_lines: int = 40
    max_file_lines: int = 500
    max_cognitive_complexity: int = 15
    max_nesting_depth: int = 4
    min_duplication_lines: int = 6
    
    ai_provider: str = os.getenv("AI_PROVIDER", "auto")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

settings = Settings()
