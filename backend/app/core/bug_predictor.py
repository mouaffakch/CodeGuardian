from typing import List, Dict, Any

class BugPredictor:
    """Predicts file-level defect susceptibility and hotspot rankings based on code complexity and Git churn."""

    def predict_hotspots(
        self,
        files_metrics: Dict[str, Dict[str, Any]],
        churn_data: Dict[str, Dict[str, Any]],
        files_defects: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        hotspots = []

        for rel_path, metrics in files_metrics.items():
            churn = churn_data.get(rel_path, {})
            defects = files_defects.get(rel_path, [])

            cc = metrics.get("cyclomatic_complexity", 1)
            cog = metrics.get("cognitive_complexity", 0)
            mi = metrics.get("maintainability_index", 100.0)
            loc = metrics.get("loc", 10)

            commit_count = churn.get("commit_count", 0)
            churn_lines = churn.get("churn_lines", 0)
            bug_fix_count = churn.get("bug_fix_count", 0)
            defect_count = len(defects)

            critical_defect_count = sum(1 for d in defects if d.get("severity") in ("CRITICAL", "HIGH"))

            cc_factor = min(100.0, (cc / 20.0) * 100.0)
            cog_factor = min(100.0, (cog / 25.0) * 100.0)
            complexity_score = (cc_factor * 0.6) + (cog_factor * 0.4)

            churn_score = 0.0
            if commit_count > 0:
                commit_score = min(100.0, (commit_count / 15.0) * 100.0)
                lines_score = min(100.0, (churn_lines / 400.0) * 100.0)
                churn_score = (commit_score * 0.5) + (lines_score * 0.5)

            bug_recurrence_score = min(100.0, (bug_fix_count / 4.0) * 100.0)

            mi_deficit = max(0.0, 100.0 - mi)

            defect_density_score = min(100.0, (critical_defect_count * 25.0) + (defect_count * 10.0))

            if commit_count > 0:
                raw_score = (
                    complexity_score * 0.25 +
                    churn_score * 0.25 +
                    bug_recurrence_score * 0.20 +
                    mi_deficit * 0.15 +
                    defect_density_score * 0.15
                )
            else:
                raw_score = (
                    complexity_score * 0.45 +
                    mi_deficit * 0.25 +
                    defect_density_score * 0.30
                )

            final_risk_score = round(max(0.0, min(100.0, raw_score)), 1)

            if final_risk_score >= 70:
                risk_level = "CRITICAL"
            elif final_risk_score >= 45:
                risk_level = "HIGH"
            elif final_risk_score >= 20:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            reasons = []
            if cc > 10:
                reasons.append(f"High cyclomatic complexity (CC: {cc})")
            if cog > 15:
                reasons.append(f"High cognitive complexity (Cognitive: {cog})")
            if bug_fix_count > 0:
                reasons.append(f"Frequent bug-fix history ({bug_fix_count} bug fix commits)")
            if commit_count >= 8:
                reasons.append(f"High change frequency ({commit_count} commits, churn: {churn_lines} lines)")
            if mi < 45:
                reasons.append(f"Low maintainability index ({mi}/100)")
            if critical_defect_count > 0:
                reasons.append(f"{critical_defect_count} high/critical static defects detected")
            if not reasons:
                reasons.append("Code structure is clean and stable with low change frequency")

            hotspots.append({
                "file_path": rel_path,
                "risk_score": final_risk_score,
                "risk_level": risk_level,
                "churn_lines": churn_lines,
                "commit_count": commit_count,
                "bug_fix_count": bug_fix_count,
                "cyclomatic_complexity": cc,
                "maintainability_index": mi,
                "reasons": reasons
            })

        hotspots.sort(key=lambda x: x["risk_score"], reverse=True)
        return hotspots

bug_predictor = BugPredictor()
