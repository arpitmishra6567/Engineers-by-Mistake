#!/usr/bin/env python3
"""
Patch syntax and safety validator script for BugRepro skill.
Ensures patches do not escape workspace boundaries and retain valid Python AST syntax.
"""

import ast
import re
import sys
from pathlib import Path


def validate_diff_path(diff_text: str, workspace_root: Path) -> bool:
    """Check that any target file mentioned in diff headers remains inside workspace."""
    resolved_root = workspace_root.resolve()
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            target = line[4:].strip()
            if target.startswith("b/"):
                target = target[2:]
            target_path = (resolved_root / target).resolve()
            try:
                target_path.relative_to(resolved_root)
            except ValueError:
                print(f"[ERROR] Path traversal attempt detected: {target}", file=sys.stderr)
                return False
    return True


def validate_python_syntax(file_path: Path) -> bool:
    """Parse python file to verify valid AST syntax."""
    if file_path.suffix.lower() != ".py":
        return True
    try:
        content = file_path.read_text(encoding="utf-8")
        ast.parse(content, filename=str(file_path))
        return True
    except SyntaxError as e:
        print(f"[ERROR] SyntaxError in {file_path}: {e}", file=sys.stderr)
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validate_patch.py <diff_or_file_path> [workspace_root]")
        return 1

    input_path = Path(sys.argv[1])
    workspace = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        return 1

    content = input_path.read_text(encoding="utf-8")

    # If it's a diff file
    if "@@" in content or "--- " in content:
        if not validate_diff_path(content, workspace):
            return 2
        print("[OK] Diff path safety validation passed.")
        return 0

    # If it's a direct python file
    if not validate_python_syntax(input_path):
        return 3

    print(f"[OK] Python syntax validation passed for {input_path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

