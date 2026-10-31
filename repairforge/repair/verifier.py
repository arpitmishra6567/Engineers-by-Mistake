"""
Patch verification module executing static checks and test suites.
Distinguishes unverified proposals from verified repairs.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import List, Optional

from repairforge.agent.context import PatchRecord, VerificationResult
from repairforge.execution.policy import ExecutionSecurityViolation
from repairforge.execution.runner import CommandRunner
from repairforge.repository.file_reader import SafeFileReader

logger = logging.getLogger(__name__)


class PatchVerifier:
    """Validates syntax and executes regression test suites on patched code."""

    def __init__(self, runner: Optional[CommandRunner] = None) -> None:
        self.runner = runner or CommandRunner()

    def validate_syntax(self, workspace_path: Path, file_path: str) -> bool:
        """Perform AST syntax validation on Python files."""
        reader = SafeFileReader(workspace_path)
        safe_path = reader.resolve_safe_path(file_path)

        if not safe_path.suffix.lower() == ".py":
            # Non-python syntax checking could be delegated to linters if available
            return True

        content = reader.read_text(file_path)
        try:
            ast.parse(content, filename=str(safe_path))
            return True
        except SyntaxError as e:
            logger.error("Syntax error detected in %s: %s", file_path, e)
            return False

    def verify(
        self,
        workspace_path: Path,
        patch: PatchRecord,
        test_command: str = "python -m pytest",
    ) -> VerificationResult:
        """
        Verify that the patch fixed the defect and caused no regressions.
        A repair is only marked VERIFIED if syntax is valid and test execution succeeds (exit code 0).
        """
        # Step 1: Syntax check
        syntax_ok = self.validate_syntax(workspace_path, patch.file_path)
        if not syntax_ok:
            return VerificationResult(
                verified=False,
                syntax_valid=False,
                tests_passed=[],
                tests_failed=["Syntax validation failed"],
                command=test_command,
                exit_code=1,
                stdout="",
                stderr="SyntaxError detected in patched file.",
                duration_seconds=0.0,
                status_label="VALIDATION_FAILED",
            )

        # Step 2: Execute regression test suite
        try:
            cmd_result = self.runner.run(test_command, working_dir=workspace_path)
        except ExecutionSecurityViolation as e:
            return VerificationResult(
                verified=False,
                syntax_valid=True,
                tests_passed=[],
                tests_failed=["Security violation: Test command blocked"],
                command=test_command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_seconds=0.0,
                status_label="VALIDATION_FAILED",
            )

        # In verification phase:
        # Exit code 0 means tests PASSED -> defect resolved and no regressions!
        verified = (cmd_result.exit_code == 0) and not cmd_result.timed_out

        passed_tests: List[str] = []
        failed_tests: List[str] = []

        if verified:
            passed_tests.append(f"{test_command} (All tests passed)")
            status_label = "VERIFIED"
        else:
            failed_tests.append(f"{test_command} (Failed with exit code {cmd_result.exit_code})")
            status_label = "VALIDATION_FAILED"

        return VerificationResult(
            verified=verified,
            syntax_valid=syntax_ok,
            tests_passed=passed_tests,
            tests_failed=failed_tests,
            command=test_command,
            exit_code=cmd_result.exit_code,
            stdout=cmd_result.stdout,
            stderr=cmd_result.stderr,
            duration_seconds=cmd_result.duration_seconds,
            status_label=status_label,
        )

