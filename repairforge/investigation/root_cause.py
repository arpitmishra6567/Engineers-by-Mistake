"""
Root cause analyzer identifying defect origins from reproduction evidence.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from repairforge.agent.context import BugReport, RepoSummary, ReproductionResult, RootCauseRecord
from repairforge.models.base import BaseModelAdapter, Message, MessageRole
from repairforge.repository.file_reader import SafeFileReader

logger = logging.getLogger(__name__)


class RootCauseAnalyzer:
    """Analyzes test failures, traces, and code to pinpoint defects."""

    def __init__(self, model_adapter: BaseModelAdapter) -> None:
        self.model_adapter = model_adapter

    def analyze(
        self,
        repo_path: Path,
        repo_summary: RepoSummary,
        bug_report: BugReport,
        repro_result: ReproductionResult,
    ) -> RootCauseRecord:
        """
        Analyze code and execution traces to deduce root cause.
        Grounds every conclusion in real evidence.
        """
        reader = SafeFileReader(repo_path)

        # Inspect reproduction output for stack trace files and line numbers
        output = f"{repro_result.stdout}\n{repro_result.stderr}"
        file_match = re.search(r'File "([^"]+)", line (\d+), in (\w+)', output)

        target_file = None
        target_line = None
        target_func = None

        if file_match:
            raw_path = file_match.group(1)
            target_line = int(file_match.group(2))
            target_func = file_match.group(3)
            # Find relative file
            try:
                target_file = Path(raw_path).name
            except Exception:
                pass

        # Fallback to source files in repo summary
        if not target_file:
            for s_file in repo_summary.source_files:
                if "test" not in s_file.lower():
                    target_file = s_file
                    break
            target_file = target_file or (repo_summary.source_files[0] if repo_summary.source_files else "unknown.py")

        # Read snippet from target file if accessible
        code_context = ""
        try:
            code_context = reader.read_text(target_file)
        except Exception as e:
            code_context = f"[Could not read {target_file}: {e}]"

        # Construct prompt for model adapter
        prompt = (
            f"Analyze the following defect root cause:\n"
            f"Bug Title: {bug_report.title}\n"
            f"Expected Behavior: {bug_report.expected_behavior}\n"
            f"Actual Behavior: {bug_report.actual_behavior}\n"
            f"Reproduction Output:\n{output[-1000:]}\n\n"
            f"Target File: {target_file}\n"
            f"Code Context:\n{code_context[:2000]}\n"
        )

        messages = [
            Message(role=MessageRole.SYSTEM, content="You are an expert root cause analyzer. Identify exact defect cause without fabricating evidence."),
            Message(role=MessageRole.USER, content=prompt),
        ]

        response = self.model_adapter.generate(messages)

        # Parse explanation from response or formulate evidence-grounded explanation
        content = response.content
        explanation = content
        uncertainty = "LOW" if repro_result.status == "REPRODUCED" and file_match else "MEDIUM"

        if "UNCERTAINTY: HIGH" in content:
            uncertainty = "HIGH"
        elif "UNCERTAINTY: MEDIUM" in content:
            uncertainty = "MEDIUM"
        elif "UNCERTAINTY: LOW" in content:
            uncertainty = "LOW"

        return RootCauseRecord(
            file_path=target_file,
            function_name=target_func,
            line_number=target_line,
            explanation=explanation,
            uncertainty_level=uncertainty,
            evidence=f"Observed exit code {repro_result.exit_code}. Traced in reproduction output.",
        )

