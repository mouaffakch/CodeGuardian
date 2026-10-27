import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, AnalysisRun, Defect, HotspotRisk, DuplicationBlock
from app.schemas import (
    ScanRequest,
    AnalysisRunResponse,
    AnalysisRunDetailResponse,
    DashboardSummaryResponse,
    DefectSchema,
    HotspotRiskSchema,
    DuplicationBlockSchema
)
from app.core.static_analyzer import static_analyzer
from app.core.duplication_detector import duplication_detector
from app.core.git_analyzer import git_analyzer
from app.core.bug_predictor import bug_predictor
from app.core.ai_engine import ai_engine
from app.core.sca_scanner import sca_scanner
from app.config import WORKSPACE_ROOT

router = APIRouter(prefix="/api/scans", tags=["Scans"])

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".next", ".system_generated", "brain"
}
SUPPORTED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".sql"}

@router.post("/run", response_model=AnalysisRunDetailResponse)
def run_scan(req: ScanRequest, db: Session = Depends(get_db)):
    """Triggers static analysis, duplication scanning, Git history churn, and AI bug prediction."""
    start_time = time.time()
    
    target_dir = Path(req.target_path) if req.target_path else WORKSPACE_ROOT
    if not target_dir.is_absolute():
        target_dir = (WORKSPACE_ROOT / target_dir).resolve()

    if not target_dir.exists():
        raise HTTPException(status_code=400, detail=f"Target path does not exist: {target_dir}")

    project_name = req.project_name or target_dir.name
    project = db.query(Project).filter(Project.root_path == str(target_dir)).first()
    if not project:
        project = Project(name=project_name, root_path=str(target_dir))
        db.add(project)
        db.commit()
        db.refresh(project)

    repo_info = git_analyzer.get_repo_info(str(target_dir))
    branch = repo_info.get("branch", "main")
    commit_hash = repo_info.get("commit_hash", "HEAD")
    churn_data = git_analyzer.analyze_file_churn(str(target_dir))

    changed_files = set(git_analyzer.get_changed_files(str(target_dir))) if req.diff_only else None

    file_contents: Dict[str, str] = {}
    file_metrics: Dict[str, Dict[str, Any]] = {}
    file_defects: Dict[str, List[Dict[str, Any]]] = {}
    total_loc = 0
    all_defects: List[Dict[str, Any]] = []

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

        for file in files:
            file_ext = Path(file).suffix.lower()
            if file_ext not in SUPPORTED_EXTENSIONS:
                continue

            full_path = os.path.join(root, file)
            rel_check = os.path.relpath(full_path, target_dir).replace("\\", "/")
            if changed_files is not None and rel_check not in changed_files:
                continue

            try:
                if os.path.getsize(full_path) > 2 * 1024 * 1024:
                    continue
            except OSError:
                continue

            res = static_analyzer.analyze_file(full_path, root_dir=str(target_dir))
            rel_p = res["file_path"]
            all_defects.extend(res["defects"])
            file_defects[rel_p] = res["defects"]
            file_metrics[rel_p] = res["metrics"]
            total_loc += res["metrics"].get("loc", 0)

            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    file_contents[rel_p] = f.read()
            except Exception:
                pass

    sca_findings = sca_scanner.scan_directory(str(target_dir))
    all_defects.extend(sca_findings)

    dup_result = duplication_detector.find_duplications(file_contents)
    duplication_blocks = dup_result["blocks"]
    duplication_percentage = dup_result["duplication_percentage"]

    for dup in duplication_blocks:
        all_defects.append({
            "file_path": dup["file_a"],
            "line_number": dup["start_line_a"],
            "end_line": dup["end_line_a"],
            "rule_id": "DUP001",
            "title": f"Code Duplication Clone ({dup['line_count']} lines)",
            "description": f"Duplicated code block matching {dup['file_b']} (lines {dup['start_line_b']}-{dup['end_line_b']}). Refactor into a shared utility function.",
            "category": "DUPLICATION",
            "severity": "MEDIUM",
            "code_snippet": dup["snippet"]
        })

    hotspots_result = bug_predictor.predict_hotspots(file_metrics, churn_data, file_defects)

    critical_count = sum(1 for d in all_defects if d["severity"] == "CRITICAL")
    high_count = sum(1 for d in all_defects if d["severity"] == "HIGH")
    medium_count = sum(1 for d in all_defects if d["severity"] == "MEDIUM")
    low_count = sum(1 for d in all_defects if d["severity"] == "LOW")

    if req.include_ai_fixes:
        for defect in all_defects:
            if defect["severity"] in ("CRITICAL", "HIGH") or len(all_defects) <= 15:
                snippet = defect.get("code_snippet") or ""
                if snippet:
                    ai_res = ai_engine.explain_and_fix(
                        rule_id=defect["rule_id"],
                        title=defect["title"],
                        description=defect["description"],
                        code_snippet=snippet,
                        file_path=defect["file_path"]
                    )
                    defect["ai_explanation"] = ai_res.get("explanation")
                    defect["ai_suggested_fix"] = ai_res.get("fixed_code")
                    defect["ai_diff"] = ai_res.get("diff")

    deductions = (critical_count * 15.0) + (high_count * 8.0) + (medium_count * 3.0) + (low_count * 1.0)
    deductions += (duplication_percentage * 1.2)
    health_score = max(5.0, min(100.0, 100.0 - deductions))

    duration_ms = int((time.time() - start_time) * 1000)

    run = AnalysisRun(
        project_id=project.id,
        branch=branch,
        commit_hash=commit_hash,
        status="COMPLETED",
        total_files=len(file_metrics),
        lines_of_code=total_loc,
        total_issues=len(all_defects),
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        duplication_percentage=duplication_percentage,
        health_score=round(health_score, 1),
        duration_ms=duration_ms
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    defect_records = []
    for d in all_defects:
        defect_obj = Defect(
            run_id=run.id,
            file_path=d["file_path"],
            line_number=d["line_number"],
            end_line=d.get("end_line"),
            rule_id=d["rule_id"],
            title=d["title"],
            description=d["description"],
            category=d.get("category", "BUG"),
            severity=d.get("severity", "MEDIUM"),
            code_snippet=d.get("code_snippet"),
            ai_explanation=d.get("ai_explanation"),
            ai_suggested_fix=d.get("ai_suggested_fix"),
            ai_diff=d.get("ai_diff")
        )
        defect_records.append(defect_obj)
    db.add_all(defect_records)

    hotspot_records = []
    for h in hotspots_result:
        hotspot_obj = HotspotRisk(
            run_id=run.id,
            file_path=h["file_path"],
            risk_score=h["risk_score"],
            risk_level=h["risk_level"],
            churn_lines=h["churn_lines"],
            commit_count=h["commit_count"],
            bug_fix_count=h["bug_fix_count"],
            cyclomatic_complexity=h["cyclomatic_complexity"],
            maintainability_index=h["maintainability_index"],
            reasons_json=json.dumps(h["reasons"])
        )
        hotspot_records.append(hotspot_obj)
    db.add_all(hotspot_records)

    dup_records = []
    for b in duplication_blocks:
        dup_obj = DuplicationBlock(
            run_id=run.id,
            content_hash=b["hash"],
            file_a=b["file_a"],
            start_line_a=b["start_line_a"],
            end_line_a=b["end_line_a"],
            file_b=b["file_b"],
            start_line_b=b["start_line_b"],
            end_line_b=b["end_line_b"],
            line_count=b["line_count"],
            snippet=b.get("snippet")
        )
        dup_records.append(dup_obj)
    db.add_all(dup_records)

    db.commit()

    return get_run_detail(run.id, db)

@router.get("", response_model=List[AnalysisRunResponse])
def list_scans(limit: int = 20, db: Session = Depends(get_db)):
    """List recent scan executions."""
    runs = db.query(AnalysisRun).order_by(AnalysisRun.created_at.desc()).limit(limit).all()
    return runs

@router.get("/{run_id}", response_model=AnalysisRunDetailResponse)
def get_run_detail(run_id: int, db: Session = Depends(get_db)):
    """Get full details of a specific analysis run."""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    defects = db.query(Defect).filter(Defect.run_id == run_id).all()
    hotspots = db.query(HotspotRisk).filter(HotspotRisk.run_id == run_id).all()
    duplications = db.query(DuplicationBlock).filter(DuplicationBlock.run_id == run_id).all()

    hotspot_schemas = []
    for h in hotspots:
        try:
            reasons = json.loads(h.reasons_json)
        except Exception:
            reasons = []
        hotspot_schemas.append(HotspotRiskSchema(
            id=h.id,
            file_path=h.file_path,
            risk_score=h.risk_score,
            risk_level=h.risk_level,
            churn_lines=h.churn_lines,
            commit_count=h.commit_count,
            bug_fix_count=h.bug_fix_count,
            cyclomatic_complexity=h.cyclomatic_complexity,
            maintainability_index=h.maintainability_index,
            reasons=reasons
        ))

    return AnalysisRunDetailResponse(
        id=run.id,
        project_id=run.project_id,
        branch=run.branch,
        commit_hash=run.commit_hash,
        status=run.status,
        total_files=run.total_files,
        lines_of_code=run.lines_of_code,
        total_issues=run.total_issues,
        critical_count=run.critical_count,
        high_count=run.high_count,
        medium_count=run.medium_count,
        low_count=run.low_count,
        duplication_percentage=run.duplication_percentage,
        health_score=run.health_score,
        duration_ms=run.duration_ms,
        created_at=run.created_at,
        error_message=run.error_message,
        defects=[DefectSchema.model_validate(d) for d in defects],
        hotspots=hotspot_schemas,
        duplications=[DuplicationBlockSchema.model_validate(b) for b in duplications]
    )

@router.get("/dashboard/stats", response_model=DashboardSummaryResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Computes global aggregated statistics for dashboard."""
    total_projects = db.query(Project).count()
    total_scans = db.query(AnalysisRun).count()
    recent_runs = db.query(AnalysisRun).order_by(AnalysisRun.created_at.desc()).limit(5).all()

    latest_run = recent_runs[0] if recent_runs else None
    latest_health_score = latest_run.health_score if latest_run else 100.0

    category_counts = {"BUG": 0, "SECURITY": 0, "BAD_PRACTICE": 0, "COMPLEXITY": 0, "DUPLICATION": 0}
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    high_risk_files = 0
    total_critical = 0
    total_high = 0
    total_dup = 0

    if latest_run:
        total_critical = latest_run.critical_count
        total_high = latest_run.high_count
        total_dup = db.query(DuplicationBlock).filter(DuplicationBlock.run_id == latest_run.id).count()

        defects = db.query(Defect).filter(Defect.run_id == latest_run.id).all()
        for d in defects:
            cat = d.category.upper() if d.category else "BUG"
            sev = d.severity.upper() if d.severity else "MEDIUM"
            category_counts[cat] = category_counts.get(cat, 0) + 1
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        high_risk_files = db.query(HotspotRisk).filter(
            HotspotRisk.run_id == latest_run.id,
            HotspotRisk.risk_level.in_(["CRITICAL", "HIGH"])
        ).count()

    return DashboardSummaryResponse(
        total_projects=total_projects,
        total_scans=total_scans,
        latest_health_score=latest_health_score,
        total_critical_bugs=total_critical,
        total_high_bugs=total_high,
        total_duplications=total_dup,
        high_risk_files_count=high_risk_files,
        category_breakdown=category_counts,
        severity_breakdown=severity_counts,
        recent_runs=[AnalysisRunResponse.model_validate(r) for r in recent_runs]
    )
