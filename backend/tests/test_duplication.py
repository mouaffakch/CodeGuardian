import pytest
from app.core.duplication_detector import DuplicationDetector

def test_duplication_detection():
    block = """
def validate_user(u):
    if not u:
        raise ValueError("User cannot be empty")
    if len(u) < 3:
        raise ValueError("User too short")
    return True
"""
    files = {
        "file1.py": f"# Header 1\n{block}\nprint(1)",
        "file2.py": f"# Header 2\n{block}\nprint(2)",
    }

    detector = DuplicationDetector(min_lines=5)
    result = detector.find_duplications(files)

    assert len(result["blocks"]) >= 1
    assert result["total_duplicate_lines"] >= 5
    assert result["duplication_percentage"] > 0
