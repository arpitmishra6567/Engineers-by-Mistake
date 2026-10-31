"""
Bug reproducer executing targeted tests to demonstrate defect presence.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from repairforge.agent.context import BugReport, ReproductionResult
from repairforge.execution.policy import ExecutionSecurityViolation
from repairforge.execution.runner import CommandRunner

logger = logging.getLogger(__name__)


class BugReproducer:
    """Executes reproduction tests and records real outcomes."""

    def __init__(self, runner: Optional[CommandRunner] = None) -> None:
        self.runner = runner or CommandRunner()

    def discover_reproduction_command(self, repo_path: Path, bug_report: Optional[BugReport] = None) -> str:
        """Identify appropriate test command from bug report or existing tests."""
        if bug_report and bug_report.reproduction_command:
            return bug_report.reproduction_command

        # Check for pytest files
        test_files = list(repo_path.glob("**/test_*.py"))
        if test_files:
            rel = test_files[0].relative_to(repo_path).as_posix()
            return f"python -m pytest {rel}"

        return "python -m pytest"

    def reproduce(self, repo_path: Path, bug_report: BugReport, custom_command: Optional[str] = None) -> ReproductionResult:
        """
        Execute reproduction command in repo directory.
        Evaluates whether the failure was observed (REPRODUCED),
        tests passed unexpectedly (NOT_REPRODUCED), or execution was BLOCKED.
        """
        command = custom_command or self.discover_reproduction_command(repo_path, bug_report)
        logger.info("Attempting reproduction with command: %s", command)

        try:
            cmd_result = self.runner.run(command, working_dir=repo_path)
        except ExecutionSecurityViolation as e:
            logger.warning("Reproduction execution blocked by policy: %s", e)
            return ReproductionResult(
                status="BLOCKED",
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_seconds=0.0,
                evidence_notes="Execution blocked by security policy.",
            )

        if cmd_result.timed_out:
            return ReproductionResult(
                status="BLOCKED",
                command=command,
                exit_code=-1,
                stdout=cmd_result.stdout,
                stderr=cmd_result.stderr,
                duration_seconds=cmd_result.duration_seconds,
                evidence_notes="Reproduction command timed out.",
            )

        # In reproduction phase:
        # Non-zero exit code means test failed, which confirms defect reproduction!
        if cmd_result.exit_code != 0:
            evidence = f"Test failed with exit code {cmd_result.exit_code} as expected for bug presence."
            # Check for specific error message matching if available
            if bug_report.error_message and (
                bug_report.error_message.lower() in cmd_result.stdout.lower()
                or bug_report.error_message.lower() in cmd_result.stderr.lower()
            ):
                evidence += f" Captured matching error: {bug_report.error_message}"

            return ReproductionResult(
                status="REPRODUCED",
                command=command,
                exit_code=cmd_result.exit_code,
                stdout=cmd_result.stdout,
                stderr=cmd_result.stderr,
                duration_seconds=cmd_result.duration_seconds,
                evidence_notes=evidence,
            )
        else:
            # Tests passed cleanly! Defect did not trigger.
            return ReproductionResult(
                status="NOT_REPRODUCED",
                command=command,
                exit_code=cmd_result.exit_code,
                stdout=cmd_result.stdout,
                stderr=cmd_result.stderr,
                duration_seconds=cmd_result.duration_seconds,
                evidence_notes="Test command passed with exit code 0. Failure not observed.",
            )

