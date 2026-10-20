import ast
import math
from typing import Dict, Any, List

class ComplexityCalculator:
    """Calculates Cyclomatic, Cognitive, Halstead and Maintainability Index metrics."""

    @staticmethod
    def calculate_metrics(code: str, file_path: str = "") -> Dict[str, Any]:
        lines = code.splitlines()
        loc = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith(("#", "//", "/*", "*")))
        code_lines = max(1, loc - blank_lines - comment_lines)

        # Default fallback metrics
        cyclomatic = 1
        cognitive = 0
        max_nesting = 0
        functions_complexity = []

        is_python = file_path.endswith(".py")
        if is_python:
            try:
                tree = ast.parse(code)
                cyclomatic, cognitive, max_nesting, functions_complexity = ComplexityCalculator._analyze_python_ast(tree)
            except SyntaxError:
                cyclomatic = ComplexityCalculator._estimate_complexity_heuristics(code)
        else:
            cyclomatic = ComplexityCalculator._estimate_complexity_heuristics(code)

        # Halstead Estimation
        tokens = [t for t in code.replace("\n", " ").split(" ") if t.strip()]
        total_tokens = len(tokens)
        unique_tokens = len(set(tokens))
        
        # Avoid math domain error with log
        vocabulary = max(2, unique_tokens)
        length = max(2, total_tokens)
        volume = length * math.log2(vocabulary)
        
        # Maintainability Index (MI) normalized to 0-100
        # Standard SEI formula: 171 - 5.2 * ln(V) - 0.23 * (CC) - 16.2 * ln(LOC)
        try:
            raw_mi = 171.0 - 5.2 * math.log(max(1.0, volume)) - 0.23 * cyclomatic - 16.2 * math.log(max(1.0, float(code_lines)))
            normalized_mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
        except Exception:
            normalized_mi = 75.0

        return {
            "loc": loc,
            "code_lines": code_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "cyclomatic_complexity": cyclomatic,
            "cognitive_complexity": cognitive,
            "max_nesting_depth": max_nesting,
            "maintainability_index": round(normalized_mi, 2),
            "halstead_volume": round(volume, 2),
            "functions": functions_complexity
        }

    @staticmethod
    def _analyze_python_ast(tree: ast.AST):
        total_cyclomatic = 1
        cognitive = 0
        max_nesting = 0
        functions = []

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.cc = 1
                self.cog = 0
                self.current_nesting = 0
                self.max_nesting = 0

            def visit_FunctionDef(self, node):
                func_visitor = ComplexityVisitor()
                for child in node.body:
                    func_visitor.visit(child)
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "cyclomatic": func_visitor.cc,
                    "cognitive": func_visitor.cog,
                    "lines": (getattr(node, "end_lineno", node.lineno) - node.lineno + 1)
                })
                self.cc += func_visitor.cc - 1
                self.cog += func_visitor.cog
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self.visit_FunctionDef(node)

            def visit_If(self, node):
                self.cc += 1
                self.cog += (1 + self.current_nesting)
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1

            def visit_For(self, node):
                self.cc += 1
                self.cog += (1 + self.current_nesting)
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1

            def visit_AsyncFor(self, node):
                self.visit_For(node)

            def visit_While(self, node):
                self.cc += 1
                self.cog += (1 + self.current_nesting)
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1

            def visit_ExceptHandler(self, node):
                self.cc += 1
                self.cog += (1 + self.current_nesting)
                self.generic_visit(node)

            def visit_BoolOp(self, node):
                # node.values has elements, each additional element adds 1 to CC
                self.cc += max(0, len(node.values) - 1)
                self.cog += max(0, len(node.values) - 1)
                self.generic_visit(node)

        root_visitor = ComplexityVisitor()
        for stmt in tree.body:
            root_visitor.visit(stmt)

        return (
            root_visitor.cc,
            root_visitor.cog,
            root_visitor.max_nesting,
            functions
        )

    @staticmethod
    def _estimate_complexity_heuristics(code: str) -> int:
        import re
        keywords = ["if ", "else if", "elif ", "for ", "while ", "case ", "catch ", "&&", "||", " and ", " or "]
        count = 1
        for kw in keywords:
            count += len(re.findall(re.escape(kw), code))
        return count
