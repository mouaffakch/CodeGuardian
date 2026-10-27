from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db
from app.routers import scans, ai, git_insights, reports

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CodeGuardian — Détection intelligente des bugs, analyse statique, prédiction de risques et suggestions IA"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/health")
def health_check():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "docs_url": "/docs"
    }

app.include_router(scans.router)
app.include_router(ai.router)
app.include_router(git_insights.router)
app.include_router(reports.router)

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "docs_url": "/docs"
        }

