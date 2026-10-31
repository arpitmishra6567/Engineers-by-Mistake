"""
Safe file reading utilities with path traversal defense and size limits.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


class PathTraversalError(Exception):
    """Raised when a file path escapes the permitted repository root."""
    pass


class FileSizeExceededError(Exception):
    """Raised when a file exceeds permitted size limits."""
    pass


class SafeFileReader:
    """Safely reads files within a designated workspace boundary."""

    def __init__(self, repo_root: Path, max_file_size_bytes: int = 1_048_576) -> None:
        self.repo_root = repo_root.resolve()
        self.max_file_size_bytes = max_file_size_bytes

    def resolve_safe_path(self, relative_or_absolute_path: str | Path) -> Path:
        """
        Resolve path and ensure it does not escape the repository boundary.
        Prevents path traversal attacks (e.g. ../../etc/passwd).
        """
        target = Path(relative_or_absolute_path)
        if not target.is_absolute():
            resolved = (self.repo_root / target).resolve()
        else:
            resolved = target.resolve()

        # Enforce boundary
        try:
            resolved.relative_to(self.repo_root)
        except ValueError as e:
            raise PathTraversalError(
                f"Path traversal detected: {relative_or_absolute_path} resolves outside {self.repo_root}"
            ) from e

        return resolved

    def read_text(self, path: str | Path, encoding: str = "utf-8") -> str:
        """Safely read text content of a file subject to size and boundary checks."""
        safe_path = self.resolve_safe_path(path)

        if not safe_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not safe_path.is_file():
            raise IsADirectoryError(f"Target is not a file: {path}")

        file_size = safe_path.stat().st_size
        if file_size > self.max_file_size_bytes:
            raise FileSizeExceededError(
                f"File size {file_size} bytes exceeds maximum allowed limit of {self.max_file_size_bytes} bytes"
            )

        return safe_path.read_text(encoding=encoding, errors="replace")

