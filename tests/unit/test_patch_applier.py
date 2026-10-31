"""Unit tests for patch application and verifier."""

import pytest
from pathlib import Path
from repairforge.repair.patch_applier import PatchApplier, PatchApplicationError
from repairforge.repair.verifier import PatchVerifier
from repairforge.agent.context import PatchRecord
from repairforge.repository.file_reader import PathTraversalError


def test_patch_applier_and_rollback(tmp_path):
    """Verify applying unified diff modifies file, and rollback restores original."""
    applier = PatchApplier(tmp_path)
    target = tmp_path / "foo.py"
    original_code = "def foo():\n    return 1\n"
    target.write_text(original_code, encoding="utf-8")

    diff = (
        "--- a/foo.py\n"
        "+++ b/foo.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def foo():\n"
        "-    return 1\n"
        "+    return 2\n"
    )

    applier.apply_unified_diff(diff)
    patched_code = target.read_text(encoding="utf-8")
    assert "return 2" in patched_code

    # Rollback
    applier.rollback()
    restored_code = target.read_text(encoding="utf-8")
    assert restored_code == original_code


def test_patch_applier_path_traversal_rejection(tmp_path):
    """Verify diff targeting files outside workspace is blocked."""
    applier = PatchApplier(tmp_path)
    diff = (
        "--- a/../../secret.py\n"
        "+++ b/../../secret.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-bad\n"
        "+good\n"
    )
    with pytest.raises(PathTraversalError):
        applier.apply_unified_diff(diff)


def test_patch_verifier_syntax_validation(tmp_path):
    """Verify verifier flags SyntaxErrors in patched python files."""
    verifier = PatchVerifier()
    bad_py = tmp_path / "syntax_err.py"
    bad_py.write_text("def broken_syntax(:\n    pass\n", encoding="utf-8")

    is_valid = verifier.validate_syntax(tmp_path, "syntax_err.py")
    assert is_valid is False

    good_py = tmp_path / "valid.py"
    good_py.write_text("def valid():\n    return 42\n", encoding="utf-8")
    assert verifier.validate_syntax(tmp_path, "valid.py") is True

