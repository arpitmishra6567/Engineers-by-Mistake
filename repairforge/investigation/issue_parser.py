"""
Parses bug reports, markdown issue descriptions, and error traces.
"""

from __future__ import annotations

import re
from typing import Optional
from repairforge.agent.context import BugReport


class IssueParser:
    """Extracts structured bug specifications from unstructured or markdown issue text."""

    @staticmethod
    def parse(raw_text: str) -> BugReport:
        """Parse raw issue text into a BugReport model."""
        lines = [line.strip() for line in raw_text.strip().splitlines()]
        title = "Reported Defect"
        description_lines = []
        expected_behavior = ""
        actual_behavior = ""
        error_message = None
        stack_trace = None
        reproduction_cmd = None

        # Try to find title from first heading or line
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if title == "Reported Defect" and lines:
            title = lines[0]

        # Extract sections if markdown headers exist
        current_section = "description"
        section_buffers: dict[str, list[str]] = {
            "description": [],
            "expected": [],
            "actual": [],
            "trace": [],
            "repro": [],
        }

        for line in lines:
            lower = line.lower()
            if "expected behavior" in lower or "expected:" in lower:
                current_section = "expected"
                continue
            elif "actual behavior" in lower or "actual:" in lower:
                current_section = "actual"
                continue
            elif "stack trace" in lower or "error message" in lower or "traceback" in lower:
                current_section = "trace"
                continue
            elif "reproduction command" in lower or "how to reproduce" in lower or "repro:" in lower:
                current_section = "repro"
                continue
            elif line.startswith("#"):
                current_section = "description"
                continue

            section_buffers[current_section].append(line)

        expected_behavior = "\n".join(section_buffers["expected"]).strip()
        actual_behavior = "\n".join(section_buffers["actual"]).strip()
        desc = "\n".join(section_buffers["description"]).strip()

        # If sections weren't explicitly separated, scan text for error indicators
        full_text = raw_text
        error_match = re.search(r"([A-Za-z]+Error:[^\n]+)", full_text)
        if error_match:
            error_message = error_match.group(1).strip()

        # Extract stack trace if traceback found
        if "Traceback (most recent call last):" in full_text:
            tb_part = full_text.split("Traceback (most recent call last):", 1)[1]
            stack_trace = ("Traceback (most recent call last):" + tb_part).strip()

        # Extract reproduction command from code block if present
        repro_text = "\n".join(section_buffers["repro"]).strip()
        if "```" in repro_text:
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", repro_text, flags=re.MULTILINE).strip()
            cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE).strip()
            reproduction_cmd = cleaned
        elif repro_text.startswith("`") and repro_text.endswith("`"):
            reproduction_cmd = repro_text.strip("`").strip()
        elif repro_text:
            reproduction_cmd = repro_text
        else:
            # Fallback scan across full text
            fence_match = re.search(r"```(?:bash|sh)?\r?\n([^\r\n]+)\r?\n```", full_text)
            if fence_match:
                reproduction_cmd = fence_match.group(1).strip()

        return BugReport(
            title=title,
            description=desc or raw_text[:200],
            expected_behavior=expected_behavior or "System functions according to specification without error.",
            actual_behavior=actual_behavior or (error_message or "Failure or unhandled exception observed."),
            error_message=error_message,
            stack_trace=stack_trace,
            reproduction_command=reproduction_cmd,
        )
