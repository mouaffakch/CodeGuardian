import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models import Project, AnalysisRun, Defect

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_apply_fix_endpoint(tmp_path):
    # Create sample file with defect
    code_file = tmp_path / "target_code.py"
    code_file.write_text("def authenticate(user, roles=[]):\n    pass\n", encoding="utf-8")

    db = SessionLocal()
    project = Project(name="Test Project", root_path=str(tmp_path))
    db.add(project)
    db.commit()

    run = AnalysisRun(project_id=project.id, branch="main", commit_hash="HEAD")
    db.add(run)
    db.commit()

    defect = Defect(
        run_id=run.id,
        file_path="target_code.py",
        line_number=1,
        rule_id="BUG002",
        title="Mutable Default Argument",
        description="roles=[] is mutable",
        code_snippet="def authenticate(user, roles=[]):",
        ai_suggested_fix="def authenticate(user, roles=None):\n    if roles is None: roles = []"
    )
    db.add(defect)
    db.commit()
    db.refresh(defect)

    defect_id = defect.id
    db.close()

    # Call /api/ai/apply-fix
    response = client.post("/api/ai/apply-fix", json={
        "defect_id": defect_id
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "target_code.py" in data["file_path"]

    # Check backup file exists
    backup_file = tmp_path / "target_code.py.bak"
    assert backup_file.exists()

    # Check file was modified
    new_content = code_file.read_text(encoding="utf-8")
    assert "roles=None" in new_content

def test_badge_svg_endpoint():
    res = client.get("/api/reports/badge.svg")
    assert res.status_code == 200
    assert "image/svg+xml" in res.headers["content-type"]
    assert "CodeGuardian" in res.text
