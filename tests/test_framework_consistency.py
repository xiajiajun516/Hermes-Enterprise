"""Framework-level consistency guards.

Keep the v2.0 daily-driver contract honest without running agents: the four
version locations agree, the dispatch convention stays intact, and every
template referenced by a role skill exists.
"""

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def _read(relative):
    return (PROJECT / relative).read_text(encoding="utf-8")


def test_version_consistent_across_all_four_files():
    changelog_top = re.search(r"^## (\d+\.\d+\.\d+)$", _read("CHANGELOG.md"), re.M).group(1)
    version_file = _read("VERSION").strip()
    distribution = re.search(r'version: "(\d+\.\d+\.\d+)"', _read("distribution.yaml")).group(1)
    master = re.search(r"^version: (\d+\.\d+\.\d+)$", _read("SKILL.md"), re.M).group(1)
    assert changelog_top == version_file == distribution == master, (
        changelog_top,
        version_file,
        distribution,
        master,
    )


def test_dispatch_convention_carries_all_four_fields_plus_load():
    master = _read("SKILL.md")
    for field in ("run:", "stage:", "output:", "rule:", "load:"):
        assert field in master, f"dispatch field {field!r} missing from SKILL.md"


def test_load_clause_allows_task_relevant_skills():
    """The load clause keeps its fixed prefix (role skill + se-team-rules) and
    allows an optional tail of task-relevant skills per run."""
    master = _read("SKILL.md")
    # fixed prefix semantics must be stated
    assert "fixed prefix" in master, "load clause must document its fixed prefix"
    assert "Load se-team-rules" in master
    # task-relevant skills are appended between role skill and se-team-rules
    assert "task-relevant skills" in master
    assert "Load skill: <stage-role>. [Load skill: <task-relevant skill>. ...] Load se-team-rules." in master
    # an example mapping must exist so the Master knows how to pick
    assert "angular-development" in master or "database-management" in master


def test_output_paths_are_concrete_and_tracked():
    """Deliverables must be fixed, git-tracked paths — never gitignored."""
    master = _read("SKILL.md")
    for path in (
        "artifacts/spec/<DD-MM-YYYY>-spec.md",
        "artifacts/report/<DD-MM-YYYY>-report.md",
        "artifacts/review/<DD-MM-YYYY>-review.md",
    ):
        assert path in master, f"{path} missing from SKILL.md"
    assert (PROJECT / "artifacts").is_dir(), "artifacts/ dir must exist"
    # the gitignore must not exclude stage deliverables
    gitignore = _read(".gitignore")
    assert "/artifacts/*.md" not in gitignore, "stage deliverables must be git-tracked"
    # the run-date prefix is computed by the Master at dispatch time
    assert "output:" in master and "<DD-MM-YYYY>" in master
    # every role skill names its concrete output path
    assert "artifacts/spec/<DD-MM-YYYY>-spec.md" in _read("skills/se-team-design/SKILL.md")
    assert "artifacts/report/<DD-MM-YYYY>-report.md" in _read("skills/se-team-engineer/SKILL.md")
    assert "artifacts/review/<DD-MM-YYYY>-review.md" in _read("skills/se-team-qa-release/SKILL.md")


def test_role_skill_templates_exist():
    for role in ("se-team-design", "se-team-engineer", "se-team-qa-release"):
        skill = _read(f"skills/{role}/SKILL.md")
        for template in re.findall(r"`templates/([\w.-]+)`", skill):
            assert (PROJECT / "templates" / template).is_file(), (
                f"{role} references missing template {template}"
            )
