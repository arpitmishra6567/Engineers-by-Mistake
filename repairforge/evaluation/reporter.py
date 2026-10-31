"""
Report generator producing structured JSON and Markdown repair summaries.
Adheres strictly to the RepairForge report standard.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from repairforge.agent.context import ExecutionContext
from repairforge.agent.state import AgentState


class RepairReporter:
    """Generates verifiable reports from execution contexts."""

    @staticmethod
    def determine_status(context: ExecutionContext) -> str:
        """
        Derive report status adhering strictly to allowed status values:
        - VERIFIED
        - PATCH_GENERATED_UNVERIFIED
        - VALIDATION_FAILED
        - NOT_REPRODUCED
        - BLOCKED
        """
        if context.current_state == AgentState.EXECUTION_BLOCKED:
            return "BLOCKED"
        if context.current_state == AgentState.NOT_REPRODUCED:
            return "NOT_REPRODUCED"
        if context.current_state == AgentState.VALIDATION_FAILED:
            return "VALIDATION_FAILED"

        # Check verification result
        if context.verification_result:
            if context.verification_result.verified:
                return "VERIFIED"
            else:
                return "VALIDATION_FAILED"

        if context.patch:
            return "PATCH_GENERATED_UNVERIFIED"

        return "BLOCKED"

    @classmethod
    def generate_markdown(cls, context: ExecutionContext) -> str:
        """Generate human-readable Markdown report."""
        status = cls.determine_status(context)

        # Issue Summary
        issue_title = context.bug_report.title if context.bug_report else "No issue provided"
        issue_desc = context.bug_report.description if context.bug_report else ""
        expected = context.bug_report.expected_behavior if context.bug_report else "N/A"
        actual = context.bug_report.actual_behavior if context.bug_report else "N/A"

        # Repo Analysis
        repo_files_count = context.repo_summary.total_files if context.repo_summary else 0
        repo_langs = ", ".join(context.repo_summary.languages) if context.repo_summary and context.repo_summary.languages else "N/A"
        test_framework = context.repo_summary.test_framework if context.repo_summary else "N/A"

        # Reproduction Evidence
        if context.reproduction_result:
            repro_status = context.reproduction_result.status
            repro_cmd = context.reproduction_result.command
            repro_code = context.reproduction_result.exit_code
            repro_notes = context.reproduction_result.evidence_notes
            repro_dur = f"{context.reproduction_result.duration_seconds:.2f}s"
            repro_section = (
                f"- **Outcome**: {repro_status}\n"
                f"- **Command**: `{repro_cmd}`\n"
                f"- **Exit Code**: {repro_code}\n"
                f"- **Duration**: {repro_dur}\n"
                f"- **Evidence**: {repro_notes}\n"
            )
        else:
            repro_section = "Reproduction was not executed or attempted."

        # Root Cause
        if context.root_cause_analysis:
            rc_file = context.root_cause_analysis.file_path
            rc_func = context.root_cause_analysis.function_name or "N/A"
            rc_expl = context.root_cause_analysis.explanation
            rc_unc = context.root_cause_analysis.uncertainty_level
            rc_ev = context.root_cause_analysis.evidence
            rc_section = (
                f"- **File**: `{rc_file}`\n"
                f"- **Function/Component**: `{rc_func}`\n"
                f"- **Uncertainty**: {rc_unc}\n"
                f"- **Explanation**: {rc_expl}\n"
                f"- **Evidence**: {rc_ev}\n"
            )
        else:
            rc_section = "Root cause analysis not completed."

        # Files Modified
        if context.patch:
            files_modified = f"- `{context.patch.file_path}`"
            patch_summary = (
                f"{context.patch.summary}\n\n"
                f"```diff\n{context.patch.diff}\n```"
            )
        else:
            files_modified = "None."
            patch_summary = "No patch generated."

        # Verification Results
        if context.verification_result:
            vr_verified = "PASSED" if context.verification_result.verified else "FAILED"
            vr_cmd = context.verification_result.command
            vr_code = context.verification_result.exit_code
            vr_syntax = "Valid" if context.verification_result.syntax_valid else "Invalid"
            vr_passed = ", ".join(context.verification_result.tests_passed) or "None"
            vr_failed = ", ".join(context.verification_result.tests_failed) or "None"
            verif_section = (
                f"- **Verification Outcome**: {vr_verified}\n"
                f"- **Syntax Check**: {vr_syntax}\n"
                f"- **Command Executed**: `{vr_cmd}`\n"
                f"- **Exit Code**: {vr_code}\n"
                f"- **Tests Passed**: {vr_passed}\n"
                f"- **Tests Failed**: {vr_failed}\n"
            )
        else:
            verif_section = "Verification tests were not run."

        # Remaining Risks
        risks = []
        if context.is_mock:
            risks.append("Patch was generated using deterministic MockModelAdapter fixture, not live LLM reasoning.")
        if status != "VERIFIED":
            risks.append("Patch has NOT been verified with passing tests.")
        if context.retry_count > 0:
            risks.append(f"Required {context.retry_count} retries during validation.")
        if not risks:
            risks.append("No critical regressions detected by the test suite.")

        risks_section = "\n".join(f"- {r}" for r in risks)

        return (
            f"# Repair Report\n\n"
            f"## Issue Summary\n"
            f"- **Title**: {issue_title}\n"
            f"- **Expected Behavior**: {expected}\n"
            f"- **Actual Behavior**: {actual}\n"
            f"- **Details**: {issue_desc}\n\n"
            f"## Repository Analysis\n"
            f"- **Files Tracked**: {repo_files_count}\n"
            f"- **Languages**: {repo_langs}\n"
            f"- **Test Framework**: {test_framework}\n\n"
            f"## Reproduction Evidence\n"
            f"{repro_section}\n"
            f"## Root Cause\n"
            f"{rc_section}\n"
            f"## Files Modified\n"
            f"{files_modified}\n\n"
            f"## Patch Summary\n"
            f"{patch_summary}\n\n"
            f"## Verification Results\n"
            f"{verif_section}\n"
            f"## Remaining Risks\n"
            f"{risks_section}\n\n"
            f"## Status\n"
            f"{status}\n"
        )

    @classmethod
    def save_reports(cls, context: ExecutionContext, output_dir: Path) -> tuple[Path, Path]:
        """Save JSON and Markdown reports to target directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        task_id = context.task_id

        # 1. Markdown report
        md_content = cls.generate_markdown(context)
        md_path = output_dir / f"repair_report_{task_id}.md"
        md_path.write_text(md_content, encoding="utf-8")

        # 2. JSON structured report
        json_path = output_dir / f"repair_report_{task_id}.json"
        json_data = context.model_dump(mode="json")
        json_data["report_status"] = cls.determine_status(context)
        json_path.write_text(json.dumps(json_data, indent=2, default=str), encoding="utf-8")

        return md_path, json_path

