"""Unit tests for report generation and metrics evaluation."""

from pathlib import Path
from repairforge.agent.context import (
    BugReport,
    ExecutionContext,
    RepoSummary,
    ReproductionResult,
    RootCauseRecord,
    PatchRecord,
    VerificationResult,
)
from repairforge.agent.state import AgentState
from repairforge.evaluation.metrics import MetricsCalculator
from repairforge.evaluation.reporter import RepairReporter


def test_repair_reporter_markdown_format(tmp_path):
    """Verify generated report matches the exact Section 6 required structure."""
    context = ExecutionContext(
        repo_path=tmp_path,
        bug_report=BugReport(
            title="IndexError on array",
            expected_behavior="Returns None on empty",
            actual_behavior="Raises IndexError",
        ),
        repo_summary=RepoSummary(
            root_path=tmp_path,
            total_files=2,
            languages=["Python"],
            test_framework="pytest",
        ),
        reproduction_result=ReproductionResult(
            status="REPRODUCED",
            command="python -m pytest",
            exit_code=1,
            evidence_notes="IndexError observed",
        ),
        root_cause_analysis=RootCauseRecord(
            file_path="mod.py",
            function_name="get_item",
            explanation="Missing bounds check",
            uncertainty_level="LOW",
            evidence="Traceback line 4",
        ),
        patch=PatchRecord(
            file_path="mod.py",
            diff="--- a/mod.py\n+++ b/mod.py\n@@ ... @@",
            summary="Bounds check added",
        ),
        verification_result=VerificationResult(
            verified=True,
            syntax_valid=True,
            command="python -m pytest",
            exit_code=0,
            tests_passed=["python -m pytest"],
        ),
        current_state=AgentState.COMPLETED,
    )

    report_md = RepairReporter.generate_markdown(context)

    # Check required headings
    assert "# Repair Report" in report_md
    assert "## Issue Summary" in report_md
    assert "## Repository Analysis" in report_md
    assert "## Reproduction Evidence" in report_md
    assert "## Root Cause" in report_md
    assert "## Files Modified" in report_md
    assert "## Patch Summary" in report_md
    assert "## Verification Results" in report_md
    assert "## Remaining Risks" in report_md
    assert "## Status" in report_md
    assert report_md.strip().endswith("VERIFIED")

    # Test file saving
    md_p, json_p = RepairReporter.save_reports(context, tmp_path)
    assert md_p.is_file()
    assert json_p.is_file()


def test_metrics_calculator():
    """Verify factual metrics calculation from execution contexts."""
    c1 = ExecutionContext(
        repo_path=Path("."),
        model_name="mock",
        reproduction_result=ReproductionResult(status="REPRODUCED", command="t", exit_code=1),
        verification_result=VerificationResult(verified=True, exit_code=0),
        start_time=100.0,
        end_time=110.0,
    )
    c2 = ExecutionContext(
        repo_path=Path("."),
        model_name="mock",
        reproduction_result=ReproductionResult(status="NOT_REPRODUCED", command="t", exit_code=0),
        verification_result=None,
        start_time=100.0,
        end_time=105.0,
    )

    metrics = MetricsCalculator.calculate([c1, c2])
    assert metrics.total_tasks == 2
    assert metrics.reproduced_count == 1
    assert metrics.verified_count == 1
    assert metrics.reproduction_rate == 0.5
    assert metrics.repair_success_rate == 0.5
    assert metrics.average_duration_seconds == 7.5

