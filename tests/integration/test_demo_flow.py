"""Integration tests for the full deterministic bug-repair workflow."""

from pathlib import Path
from repairforge.agent.orchestrator import RepairOrchestrator
from repairforge.agent.state import AgentState
from repairforge.config import AppConfig
from repairforge.evaluation.reporter import RepairReporter
from repairforge.investigation.issue_parser import IssueParser


def test_end_to_end_demo_repair(tmp_path):
    """
    Execute full end-to-end workflow on the buggy average fixture.
    Verifies:
    1. Initial defect reproduced.
    2. Patch generated deterministically.
    3. Verification passes with exit code 0.
    4. Orchestrator reaches COMPLETED state.
    5. Original repository files remain untouched.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    fixture_dir = repo_root / "examples" / "buggy_average"
    bug_report_path = fixture_dir / "bug_report.md"

    original_average_code = (fixture_dir / "average.py").read_text(encoding="utf-8")

    bug_report = IssueParser.parse(bug_report_path.read_text(encoding="utf-8"))

    config = AppConfig()
    config.agent.auto_approve_human_review = True
    config.agent.output_dir = tmp_path
    config.provider.provider_type = "mock"

    orchestrator = RepairOrchestrator(config=config)

    context = orchestrator.run(
        repo_path=fixture_dir,
        bug_report=bug_report,
        test_command="python -m pytest test_average.py",
        isolate_workspace=True,
        human_approval_callback=True,
    )

    # 1. Verification status
    status = RepairReporter.determine_status(context)
    assert status == "VERIFIED"
    assert context.current_state == AgentState.COMPLETED

    # 2. Reproduction check
    assert context.reproduction_result is not None
    assert context.reproduction_result.status == "REPRODUCED"
    assert context.reproduction_result.exit_code == 1

    # 3. Patch check
    assert context.patch is not None
    assert context.patch.is_mock is True
    assert "ValueError" in context.patch.diff

    # 4. Verification test check
    assert context.verification_result is not None
    assert context.verification_result.verified is True
    assert context.verification_result.exit_code == 0

    # 5. Isolation check: original file was not modified
    current_average_code = (fixture_dir / "average.py").read_text(encoding="utf-8")
    assert current_average_code == original_average_code, "Original file was modified despite isolate_workspace=True!"

    # 6. Check report saved
    saved_reports = list(tmp_path.glob("repair_report_*.md"))
    assert len(saved_reports) == 1
    content = saved_reports[0].read_text(encoding="utf-8")
    assert "Status\nVERIFIED" in content

