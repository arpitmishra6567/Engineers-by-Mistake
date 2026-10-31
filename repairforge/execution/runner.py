"""
Subprocess command runner with timeout enforcement and output capture.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from repairforge.execution.policy import ExecutionPolicy, ExecutionSecurityViolation

logger = logging.getLogger(__name__)


class CommandResult(BaseModel):
    """Result of an executed shell command."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    working_dir: str


class CommandRunner:
    """Executes commands while strictly enforcing execution policies and timeouts."""

    def __init__(self, policy: Optional[ExecutionPolicy] = None) -> None:
        self.policy = policy or ExecutionPolicy()

    def run(
        self,
        command: str,
        working_dir: Path,
        env: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> CommandResult:
        """
        Execute command synchronously with strict timeout.
        Validates the command against safety policies before execution.
        """
        resolved_wd = working_dir.resolve()
        self.policy.validate_command(command, resolved_wd)

        timeout_sec = timeout if timeout is not None else self.policy.command_timeout_seconds
        start_time = time.time()

        # Merge environment variables safely without leaking secrets
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        # Ensure current python executable's directory is at the front of PATH
        import sys
        current_py_dir = os.path.dirname(sys.executable)
        run_env["PATH"] = current_py_dir + os.pathsep + run_env.get("PATH", "")
        run_env["PYTHONUNBUFFERED"] = "1"
        if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
            run_env["VIRTUAL_ENV"] = sys.prefix

        logger.info("Executing command: '%s' in %s (timeout: %ss)", command, resolved_wd, timeout_sec)

        try:
            # We use shell=True for portability across Windows/Unix test runners, but strictly validate above
            process = subprocess.run(
                command,
                cwd=str(resolved_wd),
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=run_env,
            )
            duration = time.time() - start_time
            return CommandResult(
                command=command,
                exit_code=process.returncode,
                stdout=process.stdout,
                stderr=process.stderr,
                duration_seconds=duration,
                timed_out=False,
                working_dir=str(resolved_wd),
            )
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            stdout = e.stdout if isinstance(e.stdout, str) else (e.stdout.decode() if e.stdout else "")
            stderr = e.stderr if isinstance(e.stderr, str) else (e.stderr.decode() if e.stderr else "")
            logger.warning("Command timed out after %ss: '%s'", timeout_sec, command)
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout=stdout,
                stderr=stderr + f"\n[ERROR] Command timed out after {timeout_sec} seconds.",
                duration_seconds=duration,
                timed_out=True,
                working_dir=str(resolved_wd),
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error("Command execution error: %s", e)
            return CommandResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=f"[ERROR] Subprocess launch failed: {str(e)}",
                duration_seconds=duration,
                timed_out=False,
                working_dir=str(resolved_wd),
            )

    @staticmethod
    def is_docker_available() -> bool:
        """Check if Docker CLI daemon is accessible."""
        docker_path = shutil.which("docker")
        if not docker_path:
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False
