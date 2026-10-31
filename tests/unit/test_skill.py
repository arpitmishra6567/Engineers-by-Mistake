"""Unit tests validating Agent Skill metadata and package compliance."""

import yaml
from pathlib import Path


def test_bugrepro_skill_compliance():
    """Verify bugrepro skill package follows the Agent Skills standard."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    skill_dir = repo_root / "skills" / "bugrepro"

    assert skill_dir.is_dir(), f"Skill directory missing at {skill_dir}"

    skill_md = skill_dir / "SKILL.md"
    assert skill_md.is_file(), "SKILL.md file missing"

    content = skill_md.read_text(encoding="utf-8")
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter '---'"

    parts = content.split("---", 2)
    assert len(parts) >= 3, "Frontmatter must be enclosed by '---'"

    meta = yaml.safe_load(parts[1])
    assert isinstance(meta, dict), "Frontmatter must parse to a dictionary"

    # Directory name and skill name must match
    assert meta.get("name") == "bugrepro"
    assert meta.get("name") == skill_dir.name
    assert "description" in meta and len(meta["description"].strip()) > 10

    # Verify supporting files exist and are not empty
    wf = skill_dir / "references" / "workflow.md"
    sec = skill_dir / "references" / "security.md"
    rep = skill_dir / "references" / "report-format.md"
    script = skill_dir / "scripts" / "validate_patch.py"
    asset = skill_dir / "assets" / "bug_report_template.md"

    for file_path in [wf, sec, rep, script, asset]:
        assert file_path.is_file(), f"Supporting resource {file_path.name} is missing"
        assert file_path.stat().st_size > 0, f"Resource {file_path.name} is empty"

