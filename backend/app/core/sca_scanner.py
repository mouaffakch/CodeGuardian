import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional

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
        "ecosystem": "PyPI",
        "package": "torch",
        "vulnerable_versions": ["<2.2.0"],
        "cve": "CVE-2024-27318",
        "severity": "HIGH",
        "title": "PyTorch Heap Buffer Overflow in model loading",
        "fixed_version": ">=2.2.0",
        "description": "Heap buffer overflow via malformed checkpoint loading."
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
    },
    {
        "ecosystem": "Maven",
        "package": "log4j-core",
        "vulnerable_versions": ["<2.17.1"],
        "cve": "CVE-2021-44228",
        "severity": "CRITICAL",
        "title": "Log4Shell Remote Code Execution in Log4j",
        "fixed_version": ">=2.17.1",
        "description": "JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP."
    },
    {
        "ecosystem": "Maven",
        "package": "spring-boot-starter-web",
        "vulnerable_versions": ["<2.7.18", "<3.1.6"],
        "cve": "CVE-2023-34055",
        "severity": "HIGH",
        "title": "Spring Boot Denial of Service via HTTP Request Parsing",
        "fixed_version": ">=3.2.0",
        "description": "Applications may be vulnerable to denial of service when processing specific request formats."
    },
    {
        "ecosystem": "NuGet",
        "package": "Newtonsoft.Json",
        "vulnerable_versions": ["<13.0.1"],
        "cve": "CVE-2024-21907",
        "severity": "HIGH",
        "title": "Newtonsoft.Json Stack Overflow Denial of Service",
        "fixed_version": ">=13.0.1",
        "description": "Improper handling of heavily nested JSON structures causes StackOverflowException."
    },
    {
        "ecosystem": "Composer",
        "package": "symfony/http-foundation",
        "vulnerable_versions": ["<5.4.35", "<6.3.12"],
        "cve": "CVE-2024-22363",
        "severity": "HIGH",
        "title": "Symfony Header Injection / Session Fixation",
        "fixed_version": ">=6.4.3",
        "description": "Potential session fixation vulnerability in HTTP header parsing."
    }
]

class SCAScanner:
    def scan_directory(self, target_dir: str) -> List[Dict[str, Any]]:
        findings = []
        path = Path(target_dir)

        req_files = list(path.glob("**/requirements*.txt"))
        for req in req_files[:5]:
            findings.extend(self._scan_requirements_txt(req, target_dir))

        pkg_files = list(path.glob("**/package.json"))
        for pkg in pkg_files[:5]:
            if "node_modules" not in str(pkg):
                findings.extend(self._scan_package_json(pkg, target_dir))

        pom_files = list(path.glob("**/pom.xml"))
        for pom in pom_files[:5]:
            findings.extend(self._scan_pom_xml(pom, target_dir))

        composer_files = list(path.glob("**/composer.json"))
        for comp in composer_files[:5]:
            if "vendor" not in str(comp):
                findings.extend(self._scan_composer_json(comp, target_dir))

        csproj_files = list(path.glob("**/*.csproj"))
        for csproj in csproj_files[:5]:
            findings.extend(self._scan_csproj(csproj, target_dir))

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

            match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([=><!~]+.*)?$", line)
            if not match:
                continue

            pkg_name = match.group(1).lower()
            version_spec = (match.group(2) or "").strip()

            for adv in OFFLINE_ADVISORIES:
                if adv["ecosystem"] == "PyPI" and adv["package"].lower() == pkg_name:
                    if self._is_version_vulnerable(version_spec, adv["vulnerable_versions"]):
                        findings.append({
                            "file_path": rel_path,
                            "line_number": line_no,
                            "rule_id": f"SCA-{adv['cve']}",
                            "title": f"Vulnerable Python Dependency: {adv['package']} ({adv['cve']})",
                            "description": f"{adv['title']}. Recommandation : mettre à jour vers {adv['fixed_version']}.",
                            "category": "SECURITY",
                            "severity": adv["severity"],
                            "code_snippet": line,
                            "ai_explanation": f"Le package '{adv['package']}' est sujet à la faille {adv['cve']}.",
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

    def _scan_pom_xml(self, file_path: Path, root_dir: str) -> List[Dict[str, Any]]:
        findings = []
        rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            ns = {"m": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
            prefix = "m:" if ns else ""

            for dep in root.findall(f".//{prefix}dependency", ns):
                art_elem = dep.find(f"{prefix}artifactId", ns)
                ver_elem = dep.find(f"{prefix}version", ns)
                if art_elem is not None and ver_elem is not None:
                    art_id = art_elem.text.strip() if art_elem.text else ""
                    ver = ver_elem.text.strip() if ver_elem.text else ""

                    for adv in OFFLINE_ADVISORIES:
                        if adv["ecosystem"] == "Maven" and adv["package"].lower() == art_id.lower():
                            if self._is_version_vulnerable(ver, adv["vulnerable_versions"]):
                                findings.append({
                                    "file_path": rel_path,
                                    "line_number": 1,
                                    "rule_id": f"SCA-{adv['cve']}",
                                    "title": f"Vulnerable Maven Dependency: {art_id} ({adv['cve']})",
                                    "description": f"{adv['title']}. Recommandation : mettre à jour vers {adv['fixed_version']}.",
                                    "category": "SECURITY",
                                    "severity": adv["severity"],
                                    "code_snippet": f"<artifactId>{art_id}</artifactId>\n<version>{ver}</version>",
                                    "ai_explanation": f"L'artefact Maven '{art_id}' est exposé à la vulnérabilité {adv['cve']}.",
                                    "ai_suggested_fix": f"<artifactId>{art_id}</artifactId>\n<version>{adv['fixed_version'].replace('>=', '')}</version>",
                                    "ai_diff": f"- <version>{ver}</version>\n+ <version>{adv['fixed_version'].replace('>=', '')}</version>"
                                })
        except Exception:
            pass

        return findings

    def _scan_composer_json(self, file_path: Path, root_dir: str) -> List[Dict[str, Any]]:
        findings = []
        rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
        except Exception:
            return findings

        all_deps = {}
        all_deps.update(data.get("require", {}))
        all_deps.update(data.get("require-dev", {}))

        for pkg_name, version_spec in all_deps.items():
            for adv in OFFLINE_ADVISORIES:
                if adv["ecosystem"] == "Composer" and adv["package"].lower() == pkg_name.lower():
                    if self._is_version_vulnerable(version_spec, adv["vulnerable_versions"]):
                        findings.append({
                            "file_path": rel_path,
                            "line_number": 1,
                            "rule_id": f"SCA-{adv['cve']}",
                            "title": f"Vulnerable PHP Composer Dependency: {pkg_name} ({adv['cve']})",
                            "description": f"{adv['title']}. Recommandation : mettre à jour vers {adv['fixed_version']}.",
                            "category": "SECURITY",
                            "severity": adv["severity"],
                            "code_snippet": f'"{pkg_name}": "{version_spec}"',
                            "ai_explanation": f"Le composant Composer '{pkg_name}' contient la vulnérabilité {adv['cve']}.",
                            "ai_suggested_fix": f'"{pkg_name}": "{adv["fixed_version"].replace(">=", "^")}"',
                            "ai_diff": f'- "{pkg_name}": "{version_spec}"\n+ "{pkg_name}": "{adv["fixed_version"].replace(">=", "^")}"'
                        })

        return findings

    def _scan_csproj(self, file_path: Path, root_dir: str) -> List[Dict[str, Any]]:
        findings = []
        rel_path = os.path.relpath(file_path, root_dir).replace("\\", "/")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            for pkg_ref in root.findall(".//PackageReference"):
                pkg_include = pkg_ref.get("Include") or ""
                pkg_version = pkg_ref.get("Version") or ""

                for adv in OFFLINE_ADVISORIES:
                    if adv["ecosystem"] == "NuGet" and adv["package"].lower() == pkg_include.lower():
                        if self._is_version_vulnerable(pkg_version, adv["vulnerable_versions"]):
                            findings.append({
                                "file_path": rel_path,
                                "line_number": 1,
                                "rule_id": f"SCA-{adv['cve']}",
                                "title": f"Vulnerable .NET NuGet Package: {pkg_include} ({adv['cve']})",
                                "description": f"{adv['title']}. Recommandation : mettre à jour vers {adv['fixed_version']}.",
                                "category": "SECURITY",
                                "severity": adv["severity"],
                                "code_snippet": f'<PackageReference Include="{pkg_include}" Version="{pkg_version}" />',
                                "ai_explanation": f"Le package NuGet '{pkg_include}' est sujet à la faille {adv['cve']}.",
                                "ai_suggested_fix": f'<PackageReference Include="{pkg_include}" Version="{adv["fixed_version"].replace(">=", "")}" />',
                                "ai_diff": f'- Version="{pkg_version}"\n+ Version="{adv["fixed_version"].replace(">=", "")}"'
                            })
        except Exception:
            pass

        return findings

    def _is_version_vulnerable(self, version_spec: str, vulnerable_ranges: List[str]) -> bool:
        if not version_spec:
            return True

        version_num = re.findall(r"\d+\.\d+(?:\.\d+)?", version_spec)
        if not version_num:
            return True

        v_parts = [int(p) for p in version_num[0].split(".")]

        for v_range in vulnerable_ranges:
            threshold_match = re.search(r"<\s*(\d+\.\d+(?:\.\d+)?)", v_range)
            if threshold_match:
                t_parts = [int(p) for p in threshold_match.group(1).split(".")]
                if v_parts < t_parts:
                    return True

        return False

sca_scanner = SCAScanner()
