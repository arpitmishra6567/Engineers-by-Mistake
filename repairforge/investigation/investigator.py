"""
Bug investigation coordinator linking parsed issues with repository structure.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from repairforge.agent.context import BugReport, RepoSummary
from repairforge.repository.code_search import CodeSearch, SearchMatch

logger = logging.getLogger(__name__)


class BugInvestigator:
    """Investigates parsed issues and pinpoints candidate files."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.searcher = CodeSearch(self.repo_root)

    def locate_candidate_files(self, bug_report: BugReport, repo_summary: RepoSummary) -> List[str]:
        """Identify which files in the repository are most likely involved in the defect."""
        candidates = set()

        # Check terms from title and error message
        query_terms = []
        if bug_report.error_message:
            query_terms.extend(bug_report.error_message.split()[:3])
        if bug_report.title:
            query_terms.extend([w for w in bug_report.title.split() if len(w) > 3])

        for term in query_terms:
            matches = self.searcher.search_text(term)
            for m in matches:
                # Prioritize non-test source files
                if "test" not in m.file_path.lower():
                    candidates.add(m.file_path)

        # Fallback to source files in summary if no direct matches
        if not candidates:
            for s in repo_summary.source_files:
                if "test" not in s.lower():
                    candidates.add(s)

        return sorted(list(candidates))

