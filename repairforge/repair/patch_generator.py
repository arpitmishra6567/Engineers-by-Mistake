"""
Patch generator producing minimal unified diffs for diagnosed defects.
"""

from __future__ import annotations

import difflib
import logging
from pathlib import Path
from typing import Optional

from repairforge.agent.context import BugReport, PatchRecord, RootCauseRecord
from repairforge.models.base import BaseModelAdapter, Message, MessageRole
from repairforge.repository.file_reader import SafeFileReader, PathTraversalError

logger = logging.getLogger(__name__)


class PatchGenerator:
    """Generates minimal, target-specific unified diffs."""

    def __init__(self, model_adapter: BaseModelAdapter) -> None:
        self.model_adapter = model_adapter

    def generate_patch(
        self,
        workspace_path: Path,
        bug_report: BugReport,
        root_cause: RootCauseRecord,
    ) -> PatchRecord:
        """
        Produce a unified diff for the defect.
        Verifies that the target path stays inside the designated workspace.
        """
        reader = SafeFileReader(workspace_path)
        target_rel = root_cause.file_path

        # Validate that path is within workspace (raises PathTraversalError if outside)
        safe_target = reader.resolve_safe_path(target_rel)

        original_code = ""
        if safe_target.exists():
            original_code = reader.read_text(target_rel)

        prompt = (
            f"Generate a minimal code patch in unified diff format for this defect:\n"
            f"Target File: {target_rel}\n"
            f"Bug Description: {bug_report.description}\n"
            f"Expected Behavior: {bug_report.expected_behavior}\n"
            f"Root Cause: {root_cause.explanation}\n\n"
            f"Original Code:\n{original_code}\n\n"
            f"Return ONLY the unified diff."
        )

        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="You are an automated code repair generator. Generate only minimal, targeted unified diffs.",
            ),
            Message(role=MessageRole.USER, content=prompt),
        ]

        response = self.model_adapter.generate(messages)
        diff_text = response.content.strip()

        # If model returned markdown codeblock, extract diff
        if "```diff" in diff_text:
            diff_text = diff_text.split("```diff", 1)[1].split("```", 1)[0].strip()
        elif "```" in diff_text:
            diff_text = diff_text.split("```", 1)[1].split("```", 1)[0].strip()

        return PatchRecord(
            file_path=target_rel,
            diff=diff_text,
            summary=f"Fix for {root_cause.explanation[:100]}",
            is_mock=response.is_mock,
        )

