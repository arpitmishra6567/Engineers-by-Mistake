"""
Repository analyzer for inspecting project structure, languages, and dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Set

from repairforge.agent.context import RepoSummary
from repairforge.repository.file_reader import SafeFileReader

# Standard directories to exclude from indexing and search
IGNORED_DIRECTORIES: Set[str] = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "dist",
    "build",
    "eggs",
    ".eggs",
    "results",
}

# Binary and non-source extensions to skip
IGNORED_EXTENSIONS: Set[str] = {
    ".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".pdf", ".woff", ".woff2", ".ttf", ".eot",
}

LANGUAGE_EXTENSIONS: Dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript (React)",
    ".tsx": "TypeScript (React)",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".sh": "Shell",
    ".rb": "Ruby",
    ".php": "PHP",
}

DEPENDENCY_CONFIGS = [
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "Pipfile",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
]


class RepositoryAnalyzer:
    """Analyzes a codebase without executing any untrusted files."""

    def __init__(self, repo_root: Path, max_file_size_bytes: int = 1_048_576) -> None:
        self.repo_root = repo_root.resolve()
        self.reader = SafeFileReader(self.repo_root, max_file_size_bytes=max_file_size_bytes)

    def analyze(self) -> RepoSummary:
        """Scan repository and return a structured RepoSummary."""
        if not self.repo_root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_root}")

        total_files = 0
        source_files: List[str] = []
        detected_languages: Set[str] = set()
        detected_deps: List[str] = []
        has_tests = False
        test_framework = None

        has_git = (self.repo_root / ".git").is_dir()

        for root, dirs, files in os.walk(self.repo_root):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

            for file_name in files:
                file_path = Path(root) / file_name
                rel_path = file_path.relative_to(self.repo_root).as_posix()
                ext = file_path.suffix.lower()

                if ext in IGNORED_EXTENSIONS:
                    continue

                total_files += 1

                if file_name in DEPENDENCY_CONFIGS:
                    detected_deps.append(rel_path)

                if ext in LANGUAGE_EXTENSIONS:
                    detected_languages.add(LANGUAGE_EXTENSIONS[ext])
                    source_files.append(rel_path)

                # Check if it looks like a test
                if (
                    "test" in file_name.lower()
                    or "tests" in rel_path.split("/")
                ):
                    has_tests = True
                    if ext == ".py":
                        test_framework = test_framework or "pytest"
                    elif ext in (".js", ".ts"):
                        test_framework = test_framework or "jest"

        # Check for pytest or unittest configurations
        if (self.repo_root / "pytest.ini").exists() or (self.repo_root / "pyproject.toml").exists():
            if not test_framework and "Python" in detected_languages:
                test_framework = "pytest"

        return RepoSummary(
            root_path=self.repo_root,
            total_files=total_files,
            source_files=sorted(source_files),
            languages=sorted(list(detected_languages)),
            has_git=has_git,
            has_tests=has_tests,
            test_framework=test_framework,
            dependency_files=sorted(detected_deps),
        )

