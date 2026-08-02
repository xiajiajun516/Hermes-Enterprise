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


def test_role_skill_templates_exist():
    for role in ("se-team-design", "se-team-engineer", "se-team-qa-release"):
        skill = _read(f"skills/{role}/SKILL.md")
        for template in re.findall(r"`templates/([\w.-]+)`", skill):
            assert (PROJECT / "templates" / template).is_file(), (
                f"{role} references missing template {template}"
            )
