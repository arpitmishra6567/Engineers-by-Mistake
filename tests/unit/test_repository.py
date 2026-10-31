"""Unit tests for repository inspection, safe file reader, and code search."""

import pytest
from pathlib import Path
from repairforge.repository.analyzer import RepositoryAnalyzer, IGNORED_DIRECTORIES
from repairforge.repository.file_reader import (
    SafeFileReader,
    PathTraversalError,
    FileSizeExceededError,
)
from repairforge.repository.code_search import CodeSearch


def test_safe_file_reader_path_traversal(tmp_path):
    """Verify PathTraversalError is raised when trying to escape repo root."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("classified", encoding="utf-8")

    reader = SafeFileReader(repo_dir)

    with pytest.raises(PathTraversalError, match="Path traversal detected"):
        reader.read_text("../secret.txt")

    with pytest.raises(PathTraversalError):
        reader.resolve_safe_path(secret_file)


def test_safe_file_reader_size_limit(tmp_path):
    """Verify FileSizeExceededError is raised when file exceeds limit."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    big_file = repo_dir / "big.txt"
    big_file.write_text("A" * 200, encoding="utf-8")

    reader = SafeFileReader(repo_dir, max_file_size_bytes=100)
    with pytest.raises(FileSizeExceededError, match="exceeds maximum allowed limit"):
        reader.read_text("big.txt")


def test_repository_analyzer_ignores_directories(tmp_path):
    """Verify analyzer skips .git, .venv, node_modules, and cache directories."""
    repo_dir = tmp_path / "my_project"
    repo_dir.mkdir()

    # Valid files
    (repo_dir / "main.py").write_text("print('hello')", encoding="utf-8")
    (repo_dir / "pyproject.toml").write_text("[project]\nname='test'", encoding="utf-8")

    # Ignored directories
    venv_dir = repo_dir / ".venv" / "lib"
    venv_dir.mkdir(parents=True)
    (venv_dir / "site_pkg.py").write_text("# ignored", encoding="utf-8")

    git_dir = repo_dir / ".git" / "objects"
    git_dir.mkdir(parents=True)
    (git_dir / "commit_blob").write_text("blob", encoding="utf-8")

    analyzer = RepositoryAnalyzer(repo_dir)
    summary = analyzer.analyze()

    assert summary.total_files == 2
    assert "main.py" in summary.source_files
    assert not any(".venv" in f for f in summary.source_files)
    assert not any(".git" in f for f in summary.source_files)
    assert "Python" in summary.languages
    assert "pyproject.toml" in summary.dependency_files


def test_code_search(tmp_path):
    """Verify CodeSearch finds matching lines and function definitions."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "math_utils.py").write_text(
        "def calculate_total(items):\n    return sum(items)\n",
        encoding="utf-8",
    )

    searcher = CodeSearch(repo_dir)
    matches = searcher.search_text("calculate_total")
    assert len(matches) == 1
    assert matches[0].file_path == "math_utils.py"
    assert matches[0].line_number == 1

    defs = searcher.find_definitions("calculate_total")
    assert len(defs) == 1
    assert defs[0].file_path == "math_utils.py"

