import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Defect, AnalysisRun, Project
from app.schemas import AIFixRequest, AIFixResponse, ApplyFixRequest, ApplyFixResponse
from app.core.ai_engine import ai_engine
from app.config import WORKSPACE_ROOT

router = APIRouter(prefix="/api/ai", tags=["AI Engine"])

@router.post("/fix", response_model=AIFixResponse)
def generate_ai_fix(req: AIFixRequest, db: Session = Depends(get_db)):
    """Generate an AI explanation, root cause analysis, code remediation, and unified diff."""
    snippet = req.code_snippet
    rule_id = req.rule_id
    description = req.description

    if req.defect_id:
        defect = db.query(Defect).filter(Defect.id == req.defect_id).first()
        if defect:
            if not snippet and defect.code_snippet:
                snippet = defect.code_snippet
            rule_id = rule_id or defect.rule_id
            description = description or defect.description

    if not snippet:
        raise HTTPException(status_code=400, detail="Code snippet is required for AI repair.")

    result = ai_engine.explain_and_fix(
        rule_id=rule_id or "GENERIC",
        title=rule_id,
        description=description,
        code_snippet=snippet,
        file_path=req.file_path or "",
        user_instructions=req.user_instructions
    )

    if req.defect_id:
        defect = db.query(Defect).filter(Defect.id == req.defect_id).first()
        if defect:
            defect.ai_explanation = result.get("explanation")
            defect.ai_suggested_fix = result.get("fixed_code")
            defect.ai_diff = result.get("diff")
            db.commit()

    return AIFixResponse(
        explanation=result.get("explanation", ""),
        root_cause=result.get("root_cause", ""),
        remediation_summary=result.get("remediation_summary", ""),
        fixed_code=result.get("fixed_code", ""),
        diff=result.get("diff", ""),
        confidence_score=result.get("confidence_score", 0.9),
        best_practices=result.get("best_practices", [])
    )

@router.post("/apply-fix", response_model=ApplyFixResponse)
def apply_fix_to_file(req: ApplyFixRequest, db: Session = Depends(get_db)):
    """
    Applies the AI suggested fix directly to the source code on disk.
    Creates an automatic backup file (.bak) before modifying.
    Marks the defect as RESOLVED.
    """
    defect = db.query(Defect).filter(Defect.id == req.defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")

    fixed_code = req.fixed_code or defect.ai_suggested_fix
    if not fixed_code:
        raise HTTPException(status_code=400, detail="No suggested fix available for this defect")

    run = db.query(AnalysisRun).filter(AnalysisRun.id == defect.run_id).first()
    project = db.query(Project).filter(Project.id == run.project_id).first() if run else None
    base_dir = Path(project.root_path) if project and project.root_path else WORKSPACE_ROOT

    target_file = Path(defect.file_path)
    if not target_file.is_absolute():
        target_file = (base_dir / target_file).resolve()

    if not target_file.is_file():
        alt_file = (WORKSPACE_ROOT / defect.file_path).resolve()
        if alt_file.is_file():
            target_file = alt_file
        else:
            raise HTTPException(status_code=404, detail=f"File not found on disk: {target_file}")

    try:
        backup_path = target_file.with_suffix(target_file.suffix + ".bak")
        shutil.copyfile(target_file, backup_path)

        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        original_snippet = defect.code_snippet
        if original_snippet and original_snippet.strip() in content:
            new_content = content.replace(original_snippet.strip(), fixed_code.strip(), 1)
        else:
            lines = content.splitlines()
            start = max(0, defect.line_number - 1)
            end = defect.end_line or (start + 1)
            lines[start:end] = fixed_code.splitlines()
            new_content = "\n".join(lines)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        defect.status = "RESOLVED"
        defect.ai_suggested_fix = fixed_code
        db.commit()

        return ApplyFixResponse(
            success=True,
            message=f"Le correctif a été appliqué avec succès sur '{target_file.name}'. Une sauvegarde a été créée.",
            file_path=str(target_file),
            backup_path=str(backup_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply fix: {str(e)}")
