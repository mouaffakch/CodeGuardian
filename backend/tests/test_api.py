import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_root_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["name"] == "CodeGuardian"

def test_scan_sample_project():
    import os
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_project"))
    
    response = client.post("/api/scans/run", json={
        "target_path": sample_dir,
        "project_name": "Test Sample Project",
        "include_ai_fixes": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_issues"] > 0
    assert data["critical_count"] > 0
    assert len(data["defects"]) > 0
    assert len(data["hotspots"]) > 0

    # Test detail fetch
    run_id = data["id"]
    detail_res = client.get(f"/api/scans/{run_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == run_id

def test_dashboard_stats():
    res = client.get("/api/scans/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "latest_health_score" in data
    assert "category_breakdown" in data

def test_ai_fix_endpoint():
    res = client.post("/api/ai/fix", json={
        "code_snippet": "SECRET_KEY = 'secret12345'",
        "rule_id": "SEC001",
        "description": "Hardcoded secret"
    })
    assert res.status_code == 200
    data = res.json()
    assert "explanation" in data
    assert "fixed_code" in data
    assert "diff" in data
