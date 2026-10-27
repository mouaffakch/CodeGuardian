import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Known advisory offline database for fast, zero-downtime dependency vulnerability scanning
OFFLINE_ADVISORIES = [
    {
        "ecosystem": "PyPI",
        "package": "requests",
        "vulnerable_versions": ["<2.31.0"],
        "cve": "CVE-2023-32681",
        "severity": "MEDIUM",
        "title": "Requests Proxy-Authorization Header Leak",
        "fixed_version": ">=2.31.0",
        "description": "Unintended leak of Proxy-Authorization header to destination servers when following redirects."
    },
    {
        "ecosystem": "PyPI",
        "package": "urllib3",
        "vulnerable_versions": ["<2.0.7", "<1.26.18"],
        "cve": "CVE-2023-45803",
        "severity": "HIGH",
        "title": "urllib3 HTTP Request Header Injection / Cookie Leak",
        "fixed_version": ">=2.0.7",
        "description": "urllib3 does not remove the Cookie header on cross-origin redirects."
    },
    {
        "ecosystem": "PyPI",
        "package": "django",
        "vulnerable_versions": ["<4.2.8", "<5.0.1"],
        "cve": "CVE-2024-27351",
        "severity": "CRITICAL",
        "title": "Django Potential Denial of Service in regular expression validator",
        "fixed_version": ">=5.0.1",
        "description": "Potential denial-of-service vulnerability in django.utils.text.Truncator."
    },
    {
        "ecosystem": "PyPI",
        "package": "flask",
        "vulnerable_versions": ["<2.2.5"],
        "cve": "CVE-2023-30861",
        "severity": "HIGH",
        "title": "Flask Session Cookie Disclosure via Shared Caching",
        "fixed_version": ">=2.2.5",
        "description": "When all of an application's routes are behind an HTTP cache, session cookies could be cached."
    },
    {
        "ecosystem": "PyPI",
        "package": "jinja2",
        "vulnerable_versions": ["<3.1.3"],
        "cve": "CVE-2024-22195",
        "severity": "MEDIUM",
        "title": "Jinja2 Server-Side Template Injection / XSS in xmlattr filter",
        "fixed_version": ">=3.1.3",
        "description": "The xmlattr filter in Jinja2 allows attackers to inject arbitrary attributes."
    },
    {
        "ecosystem": "npm",
        "package": "lodash",
        "vulnerable_versions": ["<4.17.21"],
        "cve": "CVE-2021-23337",
        "severity": "HIGH",
        "title": "Lodash Prototype Pollution via template function",
        "fixed_version": ">=4.17.21",
        "description": "Command injection vulnerability in lodash.template."
    },
    {
        "ecosystem": "npm",
        "package": "axios",
        "vulnerable_versions": ["<1.6.0"],
        "cve": "CVE-2023-45857",
        "severity": "HIGH",
        "title": "Axios Cross-Site Request Forgery (CSRF) via Header Exposure",
        "fixed_version": ">=1.6.0",
        "description": "Axios exposes confidential headers when redirecting to another domain."
    },
    {
        "ecosystem": "npm",
        "package": "express",
        "vulnerable_versions": ["<4.19.2"],
        "cve": "CVE-2024-29041",
        "severity": "MEDIUM",
        "title": "Express Open Redirect Vulnerability in res.location()",
        "fixed_version": ">=4.19.2",
        "description": "Express fails to properly validate destination in location headers."
    }
]

class SCAScanner:
    """Software Composition Analysis (SCA) Scanner for Python requirements and npm package.json."""

    def scan_directory(self, target_dir: str) -> List[Dict[str, Any]]:
        findings = []
        path = Path(target_dir)

        # 1. Scan requirements.txt / Pipfile
        req_file = path / "requirements.txt"
        if req_file.is_file():
            findings.extend(self._scan_requirements_txt(req_file, target_dir))

        # 2. Scan package.json
        pkg_file = path / "package.json"
        if pkg_file.is_file():
            findings.extend(self._scan_package_json(pkg_file, target_dir))

        return findings

    def _scan_requirements_txt(self, file_path: Path, root_dir: str) -> List[Dict[str, Any]]:
        findings = []
        rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception:
            return findings

        for line_no, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse package and version constraint (e.g. requests==2.28.0 or flask>=2.0,<2.2.0)
            match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([=><!~]+.*)?$", line)
            if not match:
                continue

            pkg_name = match.group(1).lower()
            version_spec = (match.group(2) or "").strip()

            # Match against advisories
            for adv in OFFLINE_ADVISORIES:
                if adv["ecosystem"] == "PyPI" and adv["package"].lower() == pkg_name:
                    # Simple heuristic version match or version equality
                    if self._is_version_vulnerable(version_spec, adv["vulnerable_versions"]):
                        findings.append({
                            "file_path": rel_path,
                            "line_number": line_no,
                            "rule_id": f"SCA-{adv['cve']}",
                            "title": f"Vulnerable Dependency: {adv['package']} ({adv['cve']})",
                            "description": f"{adv['title']}. Advisory: {adv['description']} Recommandation : mettre à jour vers {adv['fixed_version']}.",
                            "category": "SECURITY",
                            "severity": adv["severity"],
                            "code_snippet": line,
                            "ai_explanation": f"Le package '{adv['package']}' spécifié à la ligne {line_no} est sujet à la faille connue {adv['cve']}. Les versions vulnérables permettent des attaques de type {adv['title'].lower()}.",
                            "ai_suggested_fix": f"{adv['package']}{adv['fixed_version']}",
                            "ai_diff": f"- {line}\n+ {adv['package']}{adv['fixed_version']}"
                        })

        return findings

    def _scan_package_json(self, file_path: Path, root_dir: str) -> List[Dict[str, Any]]:
        findings = []
        rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
        except Exception:
            return findings

        all_deps = {}
        all_deps.update(data.get("dependencies", {}))
        all_deps.update(data.get("devDependencies", {}))

        for pkg_name, version_spec in all_deps.items():
            pkg_lower = pkg_name.lower()
            for adv in OFFLINE_ADVISORIES:
                if adv["ecosystem"] == "npm" and adv["package"].lower() == pkg_lower:
                    if self._is_version_vulnerable(version_spec, adv["vulnerable_versions"]):
                        findings.append({
                            "file_path": rel_path,
                            "line_number": 1,
                            "rule_id": f"SCA-{adv['cve']}",
                            "title": f"Vulnerable npm Dependency: {adv['package']} ({adv['cve']})",
                            "description": f"{adv['title']}. Recommandation : mettre à jour vers {adv['fixed_version']}.",
                            "category": "SECURITY",
                            "severity": adv["severity"],
                            "code_snippet": f'"{pkg_name}": "{version_spec}"',
                            "ai_explanation": f"La bibliothèque npm '{adv['package']}' contient une vulnérabilité connue ({adv['cve']}).",
                            "ai_suggested_fix": f'"{pkg_name}": "{adv["fixed_version"].replace(">=", "^")}"',
                            "ai_diff": f'- "{pkg_name}": "{version_spec}"\n+ "{pkg_name}": "{adv["fixed_version"].replace(">=", "^")}"'
                        })

        return findings

    def _is_version_vulnerable(self, version_spec: str, vulnerable_ranges: List[str]) -> bool:
        if not version_spec:
            return True # Unpinned dependency is always considered risky

        # Extract numeric version
        version_num = re.findall(r"\d+\.\d+(?:\.\d+)?", version_spec)
        if not version_num:
            return True

        v_parts = [int(p) for p in version_num[0].split(".")]

        for v_range in vulnerable_ranges:
            threshold_match = re.search(r"<\s*(\d+\.\d+(?:\.\d+)?)", v_range)
            if threshold_match:
                t_parts = [int(p) for p in threshold_match.group(1).split(".")]
                # Compare version tuples
                if v_parts < t_parts:
                    return True

        return False

sca_scanner = SCAScanner()
