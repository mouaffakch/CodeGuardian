import pytest
from app.core.static_analyzer import static_analyzer
from app.core.complexity_metrics import ComplexityCalculator

def test_python_ast_defects():
    sample_code = """
def bad_func(val=[]):
    if val == None:
        pass
    try:
        x = 1
    except:
        pass
"""
    # Write to a temp string analysis
    res = static_analyzer._analyze_python(sample_code, "test.py", {"functions": []})
    rule_ids = [d["rule_id"] for d in res]
    
    assert "BUG002" in rule_ids # mutable default arg
    assert "BUG004" in rule_ids # == None
    assert "BUG001" in rule_ids # bare except

def test_sql_injection_detection():
    sample_code = """
query = f"SELECT * FROM accounts WHERE id = {user_id}"
db.execute(query)
"""
    res = static_analyzer._analyze_python(sample_code, "db.py", {"functions": []})
    rule_ids = [d["rule_id"] for d in res]
    assert "SEC002" in rule_ids

def test_secret_detection():
    sample_code = """
api_key = "ghp_1234567890abcdefghijklmnopqrstuv"
"""
    res = static_analyzer._analyze_python(sample_code, "config.py", {"functions": []})
    rule_ids = [d["rule_id"] for d in res]
    assert any("SEC001" in r for r in rule_ids)

def test_cyclomatic_complexity():
    code = """
def complex_logic(x):
    if x > 10:
        if x > 20:
            for i in range(5):
                if i == 2:
                    return True
    return False
"""
    metrics = ComplexityCalculator.calculate_metrics(code, "logic.py")
    assert metrics["cyclomatic_complexity"] >= 4
    assert metrics["max_nesting_depth"] >= 3
