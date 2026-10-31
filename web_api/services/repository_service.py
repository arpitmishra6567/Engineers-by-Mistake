"""
Repository service providing safe inspection and metadata retrieval.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from repairforge.repository.analyzer import RepositoryAnalyzer
from web_api.schemas import RepositoryInspectResponse


class RepositoryService:
    """Safely inspects authorized repository paths."""

    def __init__(self, allowed_roots: Optional[List[Path]] = None) -> None:
        # Default allowed roots: workspace root and its subdirectories
        base_dir = Path.cwd().resolve()
        self.allowed_roots = allowed_roots or [base_dir]

    def _resolve_and_validate(self, path_str: str) -> Path:
        """Resolve path and ensure it falls within an authorized workspace root."""
        target = Path(path_str)
        if not target.is_absolute():
            resolved = (Path.cwd() / target).resolve()
        else:
            resolved = target.resolve()

        if not resolved.exists():
            raise FileNotFoundError(f"Path does not exist: {path_str}")

        if not resolved.is_dir():
            raise NotADirectoryError(f"Target path is not a directory: {path_str}")

        # Check containment
        is_allowed = any(
            resolved == root.resolve() or resolved.is_relative_to(root.resolve())
            for root in self.allowed_roots
        )
        if not is_allowed:
            raise PermissionError(
                f"Access denied: {path_str} is outside permitted server workspace boundaries."
            )

        return resolved

    def inspect(self, path_str: str) -> RepositoryInspectResponse:
        """Inspect repository and return structured summary."""
        safe_path = self._resolve_and_validate(path_str)
        analyzer = RepositoryAnalyzer(safe_path)
        summary = analyzer.analyze()

        return RepositoryInspectResponse(
            root_path=str(summary.root_path),
            total_files=summary.total_files,
            languages=summary.languages,
            has_git=summary.has_git,
            has_tests=summary.has_tests,
            test_framework=summary.test_framework,
            dependency_files=summary.dependency_files,
            source_files=summary.source_files,
        )

    def list_known_repositories(self) -> List[dict]:
        """Return configured and available local repository fixtures."""
        results = []
        # Current project
        results.append({
            "name": "Engineers-by-Mistake (Current Root)",
            "path": ".",
            "type": "project",
        })
        # Known example fixture
        example_dir = Path("examples/buggy_average")
        if example_dir.exists():
            results.append({
                "name": "Buggy Average Fixture",
                "path": "examples/buggy_average",
                "type": "fixture",
            })
        return results

