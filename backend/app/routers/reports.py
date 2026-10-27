import json
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisRun, Defect, HotspotRisk, DuplicationBlock, Project

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/badge.svg")
def get_status_badge(project_id: int = Query(default=None), db: Session = Depends(get_db)):
    """Generates a dynamic Shields.io-style SVG badge with the latest health score."""
    query = db.query(AnalysisRun)
    if project_id:
        query = query.filter(AnalysisRun.project_id == project_id)
    latest_run = query.order_by(AnalysisRun.created_at.desc()).first()

    score = latest_run.health_score if latest_run else 100.0
    status_text = f"{int(score)}/100"
    
    if score >= 80:
        badge_color = "#10b981"
    elif score >= 60:
        badge_color = "#f59e0b"
    else:
        badge_color = "#ef4444"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="168" height="20" role="img" aria-label="CodeGuardian: {status_text}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="168" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="98" height="20" fill="#1e293b"/>
    <rect x="98" width="70" height="20" fill="{badge_color}"/>
    <rect width="168" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="495" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">CodeGuardian</text>
    <text x="495" y="140" transform="scale(.1)" fill="#fff">CodeGuardian</text>
    <text aria-hidden="true" x="1320" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{status_text}</text>
    <text x="1320" y="140" transform="scale(.1)" fill="#fff">{status_text}</text>
  </g>
</svg>"""
    return Response(content=svg_content, media_type="image/svg+xml")

@router.get("/{run_id}/export")
def export_report(run_id: int, format: str = "markdown", db: Session = Depends(get_db)):
    """Exports the analysis run in markdown, html (printable PDF ready), or json format."""
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
                "title": d.title, "severity": d.severity, "category": d.category,
                "status": d.status
            } for d in defects],
            "hotspots": [{
                "file": h.file_path, "score": h.risk_score, "level": h.risk_level,
                "commits": h.commit_count, "bug_fixes": h.bug_fix_count
            } for h in hotspots]
        }
        return Response(content=json.dumps(data, indent=2), media_type="application/json")

    elif format.lower() in ("html", "pdf"):
        score_color = "#10b981" if run.health_score >= 80 else "#f59e0b" if run.health_score >= 60 else "#ef4444"
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>CodeGuardian - Rapport d'Audit & Qualité Logicielle - #{run.id}</title>
    <style>
        @media print {{
            body {{ background: white !important; color: #1e293b !important; padding: 0 !important; }}
            .no-print {{ display: none !important; }}
            .card {{ border: 1px solid #cbd5e1 !important; box-shadow: none !important; }}
        }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 2.5rem; max-width: 1200px; margin: auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 1.5rem; margin-bottom: 2rem; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; text-transform: uppercase; }}
        .CRITICAL {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
        .HIGH {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }}
        .MEDIUM {{ background: rgba(234, 179, 8, 0.2); color: #fde047; border: 1px solid #eab308; }}
        .LOW {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }}
        .metric-box {{ background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 1.25rem; }}
        .metric-val {{ font-size: 2rem; font-weight: 800; margin-top: 0.5rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; margin-bottom: 2rem; font-size: 13px; }}
        th, td {{ padding: 10px 14px; border-bottom: 1px solid #1e293b; text-align: left; }}
        th {{ background: #111827; color: #94a3b8; font-size: 11px; text-transform: uppercase; }}
        .print-btn {{ background: #06b6d4; color: black; font-weight: bold; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0; font-size: 1.75rem;">CodeGuardian — Rapport d'Audit & Sécurité Logicielle</h1>
            <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 13px;">Audit Run #{run.id} • Branche: <code>{run.branch}</code> • Commit: <code>{run.commit_hash}</code> • Date: {run.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="no-print">
            <button class="print-btn" onclick="window.print()">Imprimer / Sauvegarder en PDF</button>
        </div>
    </div>

    <div class="metrics-grid">
        <div class="metric-box">
            <span style="font-size:12px; color:#94a3b8; font-weight:600;">SCORE DE SANTÉ</span>
            <div class="metric-val" style="color: {score_color};">{run.health_score}/100</div>
        </div>
        <div class="metric-box">
            <span style="font-size:12px; color:#94a3b8; font-weight:600;">DÉFAUTS CRITIQUES</span>
            <div class="metric-val" style="color: #f87171;">{run.critical_count}</div>
        </div>
        <div class="metric-box">
            <span style="font-size:12px; color:#94a3b8; font-weight:600;">CLONES DE CODE</span>
            <div class="metric-val" style="color: #06b6d4;">{run.duplication_percentage}%</div>
        </div>
        <div class="metric-box">
            <span style="font-size:12px; color:#94a3b8; font-weight:600;">TOTAL ANOMALIES</span>
            <div class="metric-val" style="color: #e2e8f0;">{run.total_issues}</div>
        </div>
    </div>

    <h2 style="font-size: 1.25rem;">Anomalies Détectées & Vulnérabilités ({len(defects)})</h2>
    <table>
        <tr><th>Sévérité</th><th>Catégorie</th><th>Règle</th><th>Fichier & Ligne</th><th>Description</th></tr>
        {"".join(f"<tr><td><span class='badge {d.severity}'>{d.severity}</span></td><td>{d.category}</td><td><code>{d.rule_id}</code></td><td>{d.file_path}:{d.line_number}</td><td>{d.title}</td></tr>" for d in defects)}
    </table>

    <h2 style="font-size: 1.25rem;">Composants à Risque Élevé (Hotspots Prédictifs)</h2>
    <table>
        <tr><th>Fichier</th><th>Indice de Risque</th><th>Niveau</th><th>Activité Git (Lignes)</th><th>Historique Correctifs</th></tr>
        {"".join(f"<tr><td><code>{h.file_path}</code></td><td><strong>{h.risk_score}%</strong></td><td><span class='badge {h.risk_level}'>{h.risk_level}</span></td><td>{h.churn_lines} lignes ({h.commit_count} commits)</td><td>{h.bug_fix_count} correctifs</td></tr>" for h in hotspots[:10])}
    </table>
</body>
</html>"""
        return Response(content=html_content, media_type="text/html")

    else:
        lines = [
            f"# CodeGuardian - Rapport d'Audit & Qualité Logicielle - #{run.id}",
            f"- **Branche :** `{run.branch}`",
            f"- **Commit :** `{run.commit_hash}`",
            f"- **Date :** {run.created_at}",
            f"- **Score de Santé :** **{run.health_score} / 100**",
            f"- **Défauts :** {run.critical_count} Critiques, {run.high_count} Hauts, {run.medium_count} Moyens, {run.low_count} Bas ({run.total_issues} total)",
            f"- **Taux de Duplication :** {run.duplication_percentage}%",
            "",
            "## Défauts & Vulnérabilités Détectées",
            "| Sévérité | Catégorie | Règle | Localisation | Description |",
            "|---|---|---|---|---|"
        ]
        for d in defects:
            lines.append(f"| **{d.severity}** | {d.category} | `{d.rule_id}` | `{d.file_path}:{d.line_number}` | {d.title} |")

        lines.extend([
            "",
            "## Points Chauds Prédictifs (Hotspots)",
            "| Fichier | Risque | Niveau | Churn Git | Correctifs Passés |",
            "|---|---|---|---|---|"
        ])
        for h in hotspots[:10]:
            lines.append(f"| `{h.file_path}` | **{h.risk_score}%** | {h.risk_level} | {h.churn_lines} lignes ({h.commit_count} commits) | {h.bug_fix_count} correctifs |")

        return Response(content="\n".join(lines), media_type="text/markdown")
