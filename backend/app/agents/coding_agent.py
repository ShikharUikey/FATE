import os
import ast
import asyncio
from typing import List, Dict, Any, Optional

class CodingAgent:
    """Specialized agent performing local software analysis, syntax checks, and file patch refactoring."""

    async def execute(self, command: str, parameters: Dict[str, Any]) -> bool:
        """Entrypoint called by the Orchestrator scheduler."""
        cmd_lower = command.lower()
        if cmd_lower == "analyze_code":
            parameters["result"] = await self.analyze_code(parameters.get("file_path", ""))
            return True
        elif cmd_lower == "lint_file":
            parameters["result"] = await self.lint_file(parameters.get("file_path", ""))
            return True
        elif cmd_lower == "apply_patch":
            return await self.apply_patch(
                parameters.get("file_path", ""),
                parameters.get("new_content", "")
            )
        return False

    async def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Parses python syntax trees and returns AST metrics (functions, classes, lines)."""
        if not file_path or not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            return {
                "status": "success",
                "file_path": file_path,
                "lines_of_code": len(content.splitlines()),
                "functions": functions,
                "classes": classes
            }
        except SyntaxError as e:
            return {"status": "syntax_error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def lint_file(self, file_path: str) -> List[str]:
        """Runs syntax lint checks against target source file."""
        if not file_path or not os.path.exists(file_path):
            return ["Error: Target file does not exist."]

        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(f"Line {i}: Line exceeds 120 characters.")
                if line.rstrip().endswith(";"):
                    issues.append(f"Line {i}: Unnecessary trailing semicolon.")
        except Exception as e:
            issues.append(f"Lint exception: {str(e)}")

        return issues

    async def apply_patch(self, file_path: str, new_content: str) -> bool:
        """Safely overwrites target file with refactored code content."""
        if not file_path:
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except Exception:
            return False
