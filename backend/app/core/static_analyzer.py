import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings
from app.core.complexity_metrics import ComplexityCalculator

class StaticAnalyzer:
    """Multi-language static analysis engine with AST inspection and security pattern detection."""

    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|password|passwd|jwt[_-]?token|private[_-]?key)\s*=\s*[\'"][a-zA-Z0-9_\-\.\$\/]{8,}[\'"]', "SEC001", "Hardcoded credential or secret key detected", "CRITICAL", "SECURITY"),
        (r'(?i)ghp_[a-zA-Z0-9]{36}', "SEC001-GH", "Hardcoded GitHub Personal Access Token", "CRITICAL", "SECURITY"),
        (r'(?i)AKIA[0-9A-Z]{16}', "SEC001-AWS", "Hardcoded AWS Access Key ID", "CRITICAL", "SECURITY"),
    ]

    SQL_PATTERNS = [
        (r'(?i)(select|insert|update|delete)\s+.*(%s|\{\}|\.format\()', "SEC002", "Potential SQL Injection via dynamic string formatting", "CRITICAL", "SECURITY"),
        (r'(?i)f[\'"][^\'"]*\b(select|insert|update|delete)\b[^\'"]*\{[^\}]+\}', "SEC002", "SQL query built with f-string interpolation", "CRITICAL", "SECURITY"),
        (r'(?i)\.execute\s*\(\s*f[\'"].*\{', "SEC002", "SQL query built with f-string interpolation in execute()", "CRITICAL", "SECURITY"),
    ]

    UNSAFE_CALLS = [
        (r'\beval\s*\(', "SEC003", "Use of unsafe eval() allows remote code execution", "CRITICAL", "SECURITY"),
        (r'\bexec\s*\(', "SEC003", "Use of unsafe exec() allows arbitrary code execution", "CRITICAL", "SECURITY"),
        (r'\bos\.system\s*\(', "SEC004", "os.system() call may be vulnerable to shell injection; prefer subprocess.run with shell=False", "HIGH", "SECURITY"),
        (r'\bpickle\.loads?\s*\(', "SEC005", "Unpickling untrusted data is vulnerable to arbitrary code execution", "HIGH", "SECURITY"),
        (r'\byaml\.load\s*\([^,)]+\)', "SEC006", "yaml.load() without SafeLoader is unsafe; use yaml.safe_load()", "HIGH", "SECURITY")
    ]

    JS_PATTERNS = [
        (r'(?i)(api[_-]?key|secret|password|bearer|token)\s*[:=]\s*[\'"][a-zA-Z0-9_\-\.]{8,}[\'"]', "JS-SEC001", "Hardcoded secret or credential token", "CRITICAL", "SECURITY"),
        (r'\beval\s*\(', "JS-SEC002", "Dangerous eval() usage enables XSS/arbitrary JS execution", "CRITICAL", "SECURITY"),
        (r'__proto__\s*=', "JS-SEC003", "Potential Prototype Pollution vulnerability", "HIGH", "SECURITY"),
        (r'[^=!]==[^=]', "JS-BUG001", "Loose equality check (==) can lead to unexpected type coercion bugs; use ===", "MEDIUM", "BUG"),
        (r'console\.(log|debug|warn)\s*\(', "JS-SMELL001", "Console logging statements left in production code", "LOW", "BAD_PRACTICE"),
    ]

    def analyze_file(self, file_path: str, root_dir: str = "") -> Dict[str, Any]:
        """Analyzes a single source file and returns defects and complexity metrics."""
        path = Path(file_path)
        if not path.is_file():
            return {"file_path": file_path, "defects": [], "metrics": {}}

        rel_path = os.path.relpath(file_path, root_dir) if root_dir else str(path)
        rel_path = rel_path.replace("\\", "/")

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            return {
                "file_path": rel_path,
                "defects": [{
                    "file_path": rel_path,
                    "line_number": 1,
                    "rule_id": "ERR001",
                    "title": "File Read Error",
                    "description": f"Could not read file: {str(e)}",
                    "category": "BUG",
                    "severity": "LOW",
                    "code_snippet": None
                }],
                "metrics": {}
            }

        defects = []
        ext = path.suffix.lower()

        metrics = ComplexityCalculator.calculate_metrics(content, file_path)

        if ext == ".py":
            defects.extend(self._analyze_python(content, rel_path, metrics))
        elif ext in (".js", ".jsx", ".ts", ".tsx"):
            defects.extend(self._analyze_javascript(content, rel_path, metrics))
        else:
            defects.extend(self._analyze_generic(content, rel_path))

        if metrics.get("loc", 0) > settings.max_file_lines:
            defects.append({
                "file_path": rel_path,
                "line_number": 1,
                "rule_id": "SMELL-LOC",
                "title": f"File is too large ({metrics['loc']} lines)",
                "description": f"File exceeds the recommended maximum of {settings.max_file_lines} lines. Consider breaking it down into smaller, cohesive modules.",
                "category": "BAD_PRACTICE",
                "severity": "LOW",
                "code_snippet": f"# Total lines: {metrics['loc']}"
            })

        if metrics.get("maintainability_index", 100) < 40:
            defects.append({
                "file_path": rel_path,
                "line_number": 1,
                "rule_id": "SMELL-MI",
                "title": f"Low Maintainability Index ({metrics['maintainability_index']}/100)",
                "description": "Code has low maintainability according to Halstead and cyclomatic metrics. High refactoring priority.",
                "category": "COMPLEXITY",
                "severity": "MEDIUM",
                "code_snippet": f"# Maintainability Index: {metrics['maintainability_index']}"
            })

        return {
            "file_path": rel_path,
            "defects": defects,
            "metrics": metrics
        }

    def _analyze_python(self, code: str, rel_path: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        defects = []
        lines = code.splitlines()

        try:
            tree = ast.parse(code)
            ast_defects = self._run_python_ast_checks(tree, lines, rel_path)
            defects.extend(ast_defects)
        except SyntaxError as e:
            defects.append({
                "file_path": rel_path,
                "line_number": e.lineno or 1,
                "end_line": e.lineno,
                "rule_id": "SYNTAX001",
                "title": "Python Syntax Error",
                "description": f"Code contains invalid Python syntax: {e.msg}",
                "category": "BUG",
                "severity": "CRITICAL",
                "code_snippet": lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else ""
            })

        defects.extend(self._scan_regex_patterns(code, lines, rel_path, self.SECRET_PATTERNS))
        defects.extend(self._scan_regex_patterns(code, lines, rel_path, self.SQL_PATTERNS))
        defects.extend(self._scan_regex_patterns(code, lines, rel_path, self.UNSAFE_CALLS))

        for func in metrics.get("functions", []):
            if func["cyclomatic"] > settings.max_cyclomatic_complexity:
                snippet = "\n".join(lines[func["line"] - 1 : min(func["line"] + 5, len(lines))])
                defects.append({
                    "file_path": rel_path,
                    "line_number": func["line"],
                    "end_line": func["end_line"],
                    "rule_id": "COMPLEXITY001",
                    "title": f"High Cyclomatic Complexity in '{func['name']}' (CC: {func['cyclomatic']})",
                    "description": f"Function '{func['name']}' has a cyclomatic complexity of {func['cyclomatic']} (threshold is {settings.max_cyclomatic_complexity}). It contains too many branching paths and is prone to hidden bugs.",
                    "category": "COMPLEXITY",
                    "severity": "HIGH",
                    "code_snippet": snippet
                })
            if func["lines"] > settings.max_function_lines:
                snippet = "\n".join(lines[func["line"] - 1 : min(func["line"] + 4, len(lines))])
                defects.append({
                    "file_path": rel_path,
                    "line_number": func["line"],
                    "end_line": func["end_line"],
                    "rule_id": "SMELL-GOD-FUNC",
                    "title": f"Long Function Smell in '{func['name']}' ({func['lines']} lines)",
                    "description": f"Function '{func['name']}' is {func['lines']} lines long (max recommended: {settings.max_function_lines}). Break it into smaller single-responsibility methods.",
                    "category": "BAD_PRACTICE",
                    "severity": "MEDIUM",
                    "code_snippet": snippet
                })

        return defects

    def _run_python_ast_checks(self, tree: ast.AST, lines: List[str], rel_path: str) -> List[Dict[str, Any]]:
        defects = []

        class ASTChecker(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                for arg in node.args.defaults:
                    if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                        line = arg.lineno
                        snippet = lines[line - 1] if line <= len(lines) else ""
                        defects.append({
                            "file_path": rel_path,
                            "line_number": line,
                            "end_line": line,
                            "rule_id": "BUG002",
                            "title": "Mutable Default Argument",
                            "description": f"Function '{node.name}' uses a mutable default argument ({type(arg).__name__}). In Python, default arguments are evaluated once at definition time and shared across calls, leading to state leakage bugs.",
                            "category": "BUG",
                            "severity": "HIGH",
                            "code_snippet": snippet
                        })

                total_args = len(node.args.args)
                if total_args > 5:
                    line = node.lineno
                    snippet = lines[line - 1] if line <= len(lines) else ""
                    defects.append({
                        "file_path": rel_path,
                        "line_number": line,
                        "end_line": line,
                        "rule_id": "SMELL005",
                        "title": f"Too Many Parameters in '{node.name}' ({total_args} params)",
                        "description": f"Function '{node.name}' takes {total_args} parameters. Consider grouping parameters into a dataclass, Pydantic model, or configuration dictionary.",
                        "category": "BAD_PRACTICE",
                        "severity": "LOW",
                        "code_snippet": snippet
                    })

                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)

            def visit_ExceptHandler(self, node):
                if node.type is None:
                    line = node.lineno
                    snippet = lines[line - 1] if line <= len(lines) else ""
                    defects.append({
                        "file_path": rel_path,
                        "line_number": line,
                        "end_line": line,
                        "rule_id": "BUG001",
                        "title": "Bare Except Clause Detected",
                        "description": "Using a bare 'except:' catches all exceptions, including KeyboardInterrupt, SystemExit, and syntax/name errors, disguising fatal defects.",
                        "category": "BUG",
                        "severity": "HIGH",
                        "code_snippet": snippet
                    })
                elif isinstance(node.type, ast.Name) and node.type.id == "BaseException":
                    line = node.lineno
                    snippet = lines[line - 1] if line <= len(lines) else ""
                    defects.append({
                        "file_path": rel_path,
                        "line_number": line,
                        "end_line": line,
                        "rule_id": "BUG001-BASE",
                        "title": "Catching BaseException",
                        "description": "Catching BaseException catches system-exiting exceptions. Catch specific exceptions or 'Exception' instead.",
                        "category": "BAD_PRACTICE",
                        "severity": "MEDIUM",
                        "code_snippet": snippet
                    })
                self.generic_visit(node)

            def visit_Compare(self, node):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value is None:
                        line = node.lineno
                        snippet = lines[line - 1] if line <= len(lines) else ""
                        defects.append({
                            "file_path": rel_path,
                            "line_number": line,
                            "end_line": line,
                            "rule_id": "BUG004",
                            "title": "Comparison with None using '==' instead of 'is'",
                            "description": "Comparisons with None should always use 'is' or 'is not' instead of equality operators ('==', '!='), as '==' can be overridden by class __eq__ methods.",
                            "category": "BUG",
                            "severity": "LOW",
                            "code_snippet": snippet
                        })
                self.generic_visit(node)

        visitor = ASTChecker()
        visitor.visit(tree)
        return defects

    def _analyze_javascript(self, code: str, rel_path: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        defects = []
        lines = code.splitlines()
        defects.extend(self._scan_regex_patterns(code, lines, rel_path, self.JS_PATTERNS))

        for i, line in enumerate(lines, 1):
            indent_spaces = len(line) - len(line.lstrip(" "))
            indent_tabs = len(line) - len(line.lstrip("\t"))
            if indent_spaces >= 20 or indent_tabs >= 5:
                defects.append({
                    "file_path": rel_path,
                    "line_number": i,
                    "end_line": i,
                    "rule_id": "JS-SMELL-NEST",
                    "title": "Excessive Callback/Nesting Depth",
                    "description": "Deeply nested code detected (callback hell / nested blocks). Consider using async/await or extracting helper functions.",
                    "category": "COMPLEXITY",
                    "severity": "MEDIUM",
                    "code_snippet": line.strip()
                })
                break
        return defects

    def _analyze_generic(self, code: str, rel_path: str) -> List[Dict[str, Any]]:
        lines = code.splitlines()
        return self._scan_regex_patterns(code, lines, rel_path, self.SECRET_PATTERNS)

    def _scan_regex_patterns(self, code: str, lines: List[str], rel_path: str, patterns) -> List[Dict[str, Any]]:
        defects = []
        for pattern_str, rule_id, title, severity, category in patterns:
            try:
                for match in re.finditer(pattern_str, code):
                    line_no = code[:match.start()].count("\n") + 1
                    snippet = lines[line_no - 1] if line_no <= len(lines) else match.group(0)
                    
                    display_snippet = snippet
                    if "SEC001" in rule_id or "secret" in title.lower():
                        display_snippet = re.sub(r'(=|:)\s*[\'"][^\'"]+[\'"]', r'\1 "********"', snippet)

                    defects.append({
                        "file_path": rel_path,
                        "line_number": line_no,
                        "end_line": line_no,
                        "rule_id": rule_id,
                        "title": title,
                        "description": f"Pattern matched: {title}",
                        "category": category,
                        "severity": severity,
                        "code_snippet": display_snippet.strip()
                    })
            except Exception:
                continue
        return defects

static_analyzer = StaticAnalyzer()
