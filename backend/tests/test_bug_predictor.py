import pytest
from app.core.bug_predictor import bug_predictor

def test_hotspot_prediction_high_risk():
    metrics = {
        "complex_legacy.py": {
            "cyclomatic_complexity": 25,
            "cognitive_complexity": 30,
            "maintainability_index": 28.0,
            "loc": 450
        },
        "clean_util.py": {
            "cyclomatic_complexity": 2,
            "cognitive_complexity": 1,
            "maintainability_index": 92.0,
            "loc": 30
        }
    }

    churn = {
        "complex_legacy.py": {
            "commit_count": 14,
            "churn_lines": 520,
            "bug_fix_count": 5
        },
        "clean_util.py": {
            "commit_count": 1,
            "churn_lines": 10,
            "bug_fix_count": 0
        }
    }

    defects = {
        "complex_legacy.py": [
            {"severity": "CRITICAL", "title": "SQLi"},
            {"severity": "HIGH", "title": "High CC"}
        ],
        "clean_util.py": []
    }

    hotspots = bug_predictor.predict_hotspots(metrics, churn, defects)

    assert len(hotspots) == 2
    assert hotspots[0]["file_path"] == "complex_legacy.py"
    assert hotspots[0]["risk_score"] > 60
    assert hotspots[0]["risk_level"] in ("CRITICAL", "HIGH")
    assert hotspots[1]["file_path"] == "clean_util.py"
    assert hotspots[1]["risk_score"] < 30
