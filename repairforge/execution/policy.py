"""
Execution safety policy defining boundaries, timeouts, and sandboxing rules.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List, Set
from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    """Supported execution environments."""
    SAFE_FIXTURE = "SAFE_FIXTURE"     # Local execution restricted to verified fixtures
    DOCKER_SANDBOX = "DOCKER_SANDBOX" # Isolated container execution
    RESTRICTED_HOST = "RESTRICTED_HOST" # Limited host execution with explicit confirmation


# Commands considered safe for local test execution
SAFE_TEST_COMMANDS: Set[str] = {
    "pytest",
    "python -m pytest",
    "python -m unittest",
    "py -m pytest",
    "py -m unittest",
}

# Commands explicitly blocked from automatic execution
BLOCKED_COMMANDS: Set[str] = {
    "rm -rf",
    "git push",
    "git commit",
    "git merge",
    "format",
    "dd",
    "mkfs",
    "shutdown",
    "reboot",
}


class ExecutionSecurityViolation(Exception):
    """Raised when an unapproved or dangerous command execution is requested."""
    pass


class ExecutionPolicy(BaseModel):
    """Defines what commands and environments are permissible."""
    mode: ExecutionMode = ExecutionMode.SAFE_FIXTURE
    command_timeout_seconds: float = 60.0
    allowed_working_dirs: List[Path] = Field(default_factory=list)
    allow_destructive_ops: bool = False
    enforce_safe_commands_only: bool = True

    def validate_command(self, command: str, working_dir: Path) -> None:
        """Inspect command string and working directory against security constraints."""
        cmd_lower = command.strip().lower()

        # Check for blocked dangerous commands
        for blocked in BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                raise ExecutionSecurityViolation(
                    f"Execution blocked: Command contains forbidden operation '{blocked}'."
                )

        # Check working directory if restricted
        if self.allowed_working_dirs:
            resolved_wd = working_dir.resolve()
            is_allowed = any(
                resolved_wd == allowed.resolve() or resolved_wd.is_relative_to(allowed.resolve())
                for allowed in self.allowed_working_dirs
            )
            if not is_allowed:
                raise ExecutionSecurityViolation(
                    f"Execution blocked: Working directory {working_dir} is outside approved directories."
                )

        # In safe fixture mode, enforce safe test commands
        if self.enforce_safe_commands_only and self.mode == ExecutionMode.SAFE_FIXTURE:
            is_safe = any(cmd_lower.startswith(safe_cmd) for safe_cmd in SAFE_TEST_COMMANDS)
            if not is_safe and not ("python" in cmd_lower and ("test" in cmd_lower or "-m unittest" in cmd_lower)):
                raise ExecutionSecurityViolation(
                    f"Execution blocked under SAFE_FIXTURE mode: Command '{command}' is not in the safe test command whitelist."
                )

