"""
Patch applier and workspace modifier with rollback and isolation support.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Optional

from repairforge.repository.file_reader import SafeFileReader, PathTraversalError

logger = logging.getLogger(__name__)


class PatchApplicationError(Exception):
    """Raised when a patch cannot be applied cleanly."""
    pass


class PatchApplier:
    """Safely applies diff patches to target files with rollback backup."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path.resolve()
        self.reader = SafeFileReader(self.workspace_path)
        self.backups: Dict[Path, str] = {}

    def create_backup(self, relative_path: str | Path) -> None:
        """Store original file content before modification."""
        safe_path = self.reader.resolve_safe_path(relative_path)
        if safe_path.exists() and safe_path not in self.backups:
            self.backups[safe_path] = safe_path.read_text(encoding="utf-8")

    def rollback(self) -> None:
        """Restore all backed-up files to their exact original state."""
        for path, original_content in self.backups.items():
            try:
                path.write_text(original_content, encoding="utf-8")
                logger.info("Rolled back file: %s", path)
            except Exception as e:
                logger.error("Failed to rollback %s: %s", path, e)
        self.backups.clear()

    def apply_unified_diff(self, diff_text: str, target_file_override: Optional[str] = None) -> Path:
        """
        Apply a unified diff string to the repository.
        Parses diff headers to identify target file, applies hunks, and writes back.
        """
        lines = diff_text.strip().splitlines()
        target_rel = target_file_override

        # Extract target file from diff headers if not overridden
        # e.g., +++ b/average.py or +++ average.py
        if not target_rel:
            for line in lines:
                if line.startswith("+++ "):
                    raw_target = line[4:].strip()
                    if raw_target.startswith("b/"):
                        raw_target = raw_target[2:]
                    target_rel = raw_target
                    break

        if not target_rel:
            raise PatchApplicationError("Could not extract target file from unified diff header.")

        safe_path = self.reader.resolve_safe_path(target_rel)
        if not safe_path.exists():
            raise PatchApplicationError(f"Target file for patch does not exist: {target_rel}")

        # Create backup before applying
        self.create_backup(target_rel)

        original_content = safe_path.read_text(encoding="utf-8")
        original_lines = original_content.splitlines(keepends=True)

        # Parse hunks and apply
        try:
            patched_lines = self._apply_hunks(original_lines, lines)
            safe_path.write_text("".join(patched_lines), encoding="utf-8")
            logger.info("Successfully applied patch to %s", safe_path)
            return safe_path
        except Exception as e:
            logger.error("Error applying patch hunks to %s: %s", safe_path, e)
            self.rollback()
            raise PatchApplicationError(f"Failed to apply patch hunks to {target_rel}: {str(e)}") from e

    def _apply_hunks(self, original_lines: list[str], diff_lines: list[str]) -> list[str]:
        """Robust unified diff hunk applier with context-based locating."""
        hunk_indices = [i for i, line in enumerate(diff_lines) if line.startswith("@@")]
        if not hunk_indices:
            raise PatchApplicationError("Unified diff has no valid '@@' hunk headers.")

        out_lines = list(original_lines)

        # Process each hunk in reverse order so line offsets don't invalidate subsequent hunks
        for h_start_idx in reversed(hunk_indices):
            header = diff_lines[h_start_idx]
            match = re.search(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", header)
            if not match:
                continue

            old_start = int(match.group(1))
            old_len = int(match.group(2)) if match.group(2) else 1

            # Collect hunk lines until next hunk or end
            next_hunks = [i for i in hunk_indices if i > h_start_idx]
            h_end_idx = min(next_hunks) if next_hunks else len(diff_lines)
            hunk_content = diff_lines[h_start_idx + 1:h_end_idx]

            expected_old: list[str] = []
            new_sub_lines: list[str] = []

            for hline in hunk_content:
                if hline.startswith("+"):
                    line_to_add = hline[1:]
                    if not line_to_add.endswith("\n"):
                        line_to_add += "\n"
                    new_sub_lines.append(line_to_add)
                elif hline.startswith(" "):
                    line_to_keep = hline[1:]
                    if not line_to_keep.endswith("\n"):
                        line_to_keep += "\n"
                    new_sub_lines.append(line_to_keep)
                    expected_old.append(line_to_keep)
                elif hline.startswith("-"):
                    line_to_del = hline[1:]
                    if not line_to_del.endswith("\n"):
                        line_to_del += "\n"
                    expected_old.append(line_to_del)

            # Locate where in out_lines the expected_old hunk lines match
            found_idx = None
            if expected_old:
                first_target = expected_old[0].strip()
                for idx, o_line in enumerate(out_lines):
                    if o_line.strip() == first_target:
                        match_all = True
                        for offset, exp_line in enumerate(expected_old):
                            if (
                                idx + offset >= len(out_lines)
                                or out_lines[idx + offset].strip() != exp_line.strip()
                            ):
                                match_all = False
                                break
                        if match_all:
                            found_idx = idx
                            break

            if found_idx is not None:
                replace_start = found_idx
                replace_end = replace_start + len(expected_old)
            else:
                replace_start = max(0, old_start - 1)
                replace_end = replace_start + old_len

            out_lines[replace_start:replace_end] = new_sub_lines

        return out_lines
