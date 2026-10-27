import pytest
from app.core.sca_scanner import sca_scanner

def test_sca_scanner_detects_vulnerable_python_deps(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests==2.28.0\nflask==2.1.0\n", encoding="utf-8")

    findings = sca_scanner.scan_directory(str(tmp_path))
    assert len(findings) >= 2
    rule_ids = [f["rule_id"] for f in findings]
    assert any("CVE" in r for r in rule_ids)
    assert any("requests" in f["title"].lower() for f in findings)

def test_sca_scanner_detects_npm_deps(tmp_path):
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text('{"dependencies": {"lodash": "4.17.15", "express": "4.18.0"}}', encoding="utf-8")

    findings = sca_scanner.scan_directory(str(tmp_path))
    assert len(findings) >= 1
    assert any("lodash" in f["title"].lower() for f in findings)
