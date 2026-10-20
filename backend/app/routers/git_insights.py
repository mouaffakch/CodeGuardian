import os
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from app.core.git_analyzer import git_analyzer
from app.core.bug_predictor import bug_predictor
from app.core.static_analyzer import static_analyzer
from app.config import WORKSPACE_ROOT

router = APIRouter(prefix="/api/git", tags=["Git Insights"])

@router.get("/repo-info")
def get_repo_info(repo_path: str = Query(default=None)):
    """Returns branch, latest commit, and remote information."""
    target = Path(repo_path) if repo_path else WORKSPACE_ROOT
    if not target.exists():
        raise HTTPException(status_code=400, detail="Target path does not exist")
    return git_analyzer.get_repo_info(str(target))

@router.get("/churn")
def get_churn_data(repo_path: str = Query(default=None), max_commits: int = 150):
    """Returns churn metrics (commits, churn lines, bug fix count) per file."""
    target = Path(repo_path) if repo_path else WORKSPACE_ROOT
    if not target.exists():
        raise HTTPException(status_code=400, detail="Target path does not exist")
    return git_analyzer.analyze_file_churn(str(target), max_commits=max_commits)
