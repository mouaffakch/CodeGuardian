import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisRun, Defect, HotspotRisk, DuplicationBlock

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/{run_id}/export")
def export_report(run_id: int, format: str = "markdown", db: Session = Depends(get_db)):
    """Exports the analysis run in markdown, html, or json format."""
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    defects = db.query(Defect).filter(Defect.run_id == run_id).all()
    hotspots = db.query(HotspotRisk).filter(HotspotRisk.run_id == run_id).all()
    duplications = db.query(DuplicationBlock).filter(DuplicationBlock.run_id == run_id).all()

    if format.lower() == "json":
        data = {
            "run_id": run.id,
            "project_id": run.project_id,
            "branch": run.branch,
            "commit": run.commit_hash,
            "health_score": run.health_score,
            "total_issues": run.total_issues,
            "critical_count": run.critical_count,
            "high_count": run.high_count,
            "medium_count": run.medium_count,
            "low_count": run.low_count,
            "duplication_percentage": run.duplication_percentage,
            "defects": [{
                "file": d.file_path, "line": d.line_number, "rule": d.rule_id,
                "title": d.title, "severity": d.severity, "category": d.category
            } for d in defects],
            "hotspots": [{
                "file": h.file_path, "score": h.risk_score, "level": h.risk_level,
                "commits": h.commit_count, "bug_fixes": h.bug_fix_count
            } for h in hotspots]
        }
        return Response(content=json.dumps(data, indent=2), media_type="application/json")

    elif format.lower() == "html":
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CodeGuardian Security & Quality Audit Report - #{run.id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }}
        h1, h2 {{ color: #38bdf8; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
        .CRITICAL {{ background: #dc2626; color: white; }}
        .HIGH {{ background: #ea580c; color: white; }}
        .MEDIUM {{ background: #d97706; color: white; }}
        .LOW {{ background: #2563eb; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #334155; text-align: left; }}
        th {{ background: #1e293b; color: #94a3b8; }}
        .score {{ font-size: 3rem; font-weight: bold; color: {'#22c55e' if run.health_score >= 80 else '#eab308' if run.health_score >= 60 else '#ef4444'}; }}
    </style>
</head>
<body>
    <h1>🛡️ CodeGuardian Analysis Report</h1>
    <p>Run #{run.id} | Branch: <code>{run.branch}</code> | Commit: <code>{run.commit_hash}</code> | Date: {run.created_at}</p>
    <div>
        <p>Global Health Score:</p>
        <div class="score">{run.health_score}/100</div>
    </div>
    <h2>Defects & Security Vulnerabilities ({len(defects)})</h2>
    <table>
        <tr><th>Severity</th><th>Category</th><th>Rule</th><th>File</th><th>Line</th><th>Description</th></tr>
        {"".join(f"<tr><td><span class='badge {d.severity}'>{d.severity}</span></td><td>{d.category}</td><td>{d.rule_id}</td><td>{d.file_path}</td><td>{d.line_number}</td><td>{d.title}</td></tr>" for d in defects)}
    </table>
</body>
</html>"""
        return Response(content=html_content, media_type="text/html")

    else:
        # Markdown report
        lines = [
            f"# 🛡️ CodeGuardian Analysis Report - #{run.id}",
            f"- **Branch:** `{run.branch}`",
            f"- **Commit:** `{run.commit_hash}`",
            f"- **Date:** {run.created_at}",
            f"- **Health Score:** **{run.health_score} / 100**",
            f"- **Total Issues:** {run.total_issues} (🔴 {run.critical_count} Critical, 🟠 {run.high_count} High, 🟡 {run.medium_count} Medium, 🔵 {run.low_count} Low)",
            f"- **Duplication Rate:** {run.duplication_percentage}%",
            "",
            "## 🚨 Top Defect & Vulnerability Findings",
            "| Severity | Category | Rule | Location | Description |",
            "|---|---|---|---|---|"
        ]
        for d in defects:
            lines.append(f"| **{d.severity}** | {d.category} | `{d.rule_id}` | `{d.file_path}:{d.line_number}` | {d.title} |")

        lines.extend([
            "",
            "## 🔮 High-Risk Hotspot Predictions",
            "| File | Risk Score | Risk Level | Commit Churn | Bug Fix History |",
            "|---|---|---|---|---|"
        ])
        for h in hotspots[:10]:
            lines.append(f"| `{h.file_path}` | **{h.risk_score}** | {h.risk_level} | {h.churn_lines} lines ({h.commit_count} commits) | {h.bug_fix_count} bug fixes |")

        return Response(content="\n".join(lines), media_type="text/markdown")
