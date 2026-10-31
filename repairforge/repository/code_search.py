"""
Code search utilities for locating relevant files, symbols, and patterns.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

from repairforge.repository.analyzer import RepositoryAnalyzer
from repairforge.repository.file_reader import SafeFileReader


class SearchMatch(BaseModel):
    """A single match location in the repository."""
    file_path: str
    line_number: int
    line_content: str


class CodeSearch:
    """Performs read-only search across repository source files."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.reader = SafeFileReader(self.repo_root)
        self.analyzer = RepositoryAnalyzer(self.repo_root)

    def search_text(self, query: str, case_sensitive: bool = False) -> List[SearchMatch]:
        """Search for plain text query across allowed source files."""
        matches: List[SearchMatch] = []
        summary = self.analyzer.analyze()

        target = query if case_sensitive else query.lower()

        for rel_file in summary.source_files:
            try:
                content = self.reader.read_text(rel_file)
            except Exception:
                continue

            for idx, line in enumerate(content.splitlines(), start=1):
                haystack = line if case_sensitive else line.lower()
                if target in haystack:
                    matches.append(
                        SearchMatch(
                            file_path=rel_file,
                            line_number=idx,
                            line_content=line.strip(),
                        )
                    )

        return matches

    def find_definitions(self, symbol_name: str) -> List[SearchMatch]:
        """Find function or class definitions for a symbol."""
        # Common definition patterns in Python / JS
        pattern = re.compile(rf"^\s*(def|class|function|const|let)\s+{re.escape(symbol_name)}\b")
        matches: List[SearchMatch] = []
        summary = self.analyzer.analyze()

        for rel_file in summary.source_files:
            try:
                content = self.reader.read_text(rel_file)
            except Exception:
                continue

            for idx, line in enumerate(content.splitlines(), start=1):
                if pattern.search(line):
                    matches.append(
                        SearchMatch(
                            file_path=rel_file,
                            line_number=idx,
                            line_content=line.strip(),
                        )
                    )

        return matches

