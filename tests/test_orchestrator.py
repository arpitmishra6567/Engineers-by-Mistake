"""Unit and orchestration tests for RepairOrchestrator."""

import pytest
from pathlib import Path
from repairforge.agent.orchestrator import RepairOrchestrator
from repairforge.agent.state import AgentState
from repairforge.config import AppConfig
from repairforge.agent.context import BugReport


def test_orchestrator_initialization():
    """Verify orchestrator initializes with default mock adapter and configs."""
    orchestrator = RepairOrchestrator()
    assert orchestrator.config is not None
    assert orchestrator.model_adapter is not None
    assert orchestrator.model_adapter.is_deterministic is True


def test_orchestrator_not_reproduced_halts_gracefully(tmp_path):
    """Verify workflow halts when tests pass and bug cannot be reproduced."""
    # Create clean repo with passing test
    test_file = tmp_path / "test_ok.py"
    test_file.write_text("def test_always_passes(): assert True\n", encoding="utf-8")

    bug_report = BugReport(
        title="Phantom Bug",
        expected_behavior="Something",
        actual_behavior="Nothing",
        reproduction_command="python -m pytest test_ok.py",
    )

    config = AppConfig()
    config.agent.output_dir = tmp_path / "results"
    orchestrator = RepairOrchestrator(config=config)

    context = orchestrator.run(
        repo_path=tmp_path,
        bug_report=bug_report,
        test_command="python -m pytest test_ok.py",
        isolate_workspace=True,
    )

    assert context.current_state == AgentState.NOT_REPRODUCED
    assert context.reproduction_result.status == "NOT_REPRODUCED"
    assert context.patch is None  # Never generates patch if not reproduced

