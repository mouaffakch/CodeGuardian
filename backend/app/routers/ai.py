from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Defect
from app.schemas import AIFixRequest, AIFixResponse
from app.core.ai_engine import ai_engine

router = APIRouter(prefix="/api/ai", tags=["AI Engine"])

@router.post("/fix", response_model=AIFixResponse)
def generate_ai_fix(req: AIFixRequest, db: Session = Depends(get_db)):
    """Generate an AI explanation, root cause analysis, code remediation, and unified diff."""
    # If defect_id was provided and snippet is empty, load from database
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

    # If associated with a DB defect, optionally persist the fix
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
