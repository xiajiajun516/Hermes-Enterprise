#!/usr/bin/env python3
"""
Self Health Check — Structural Validation Script

Performs 5 checks on the hermes-enterprise-profile-push repository:
  1. All 7 skill directories contain SKILL.md
  2. Each SKILL.md has required YAML frontmatter (name, description, category)
  3. All 7 templates exist in templates/
  4. Master Dispatch consistency: SKILL.md stage names match skills/ subdirectories
  5. Reference chain: spec.md → architecture.md → implementation-plan.md

Exit code 0 = PASS, 1 = FAIL (any check 1-4 fails, or check 5 fails critically)
"""

import os
import re
import sys
import yaml  # optional, will fall back to regex if missing

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_SKILLS = [
    "se-team-architect",
    "se-team-compliance-reviewer",
    "se-team-engineer",
    "se-team-product-research",
    "se-team-qa-release",
    "se-team-rule-manager",
    "se-team-rules",
]

REQUIRED_TEMPLATES = [
    "architecture-template.md",
    "compliance-report-template.md",
    "implementation-plan-template.md",
    "release-template.md",
    "review-template.md",
    "spec-template.md",
    "test-report-template.md",
]

REQUIRED_FRONTMATTER_KEYS = ["name", "description", "category"]


def read_yaml_frontmatter(path):
    """Extract YAML frontmatter from a markdown file."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    fm_text = match.group(1)

    # Try yaml parser first
    try:
        import yaml as _yaml

        return _yaml.safe_load(fm_text)
    except ImportError:
        pass

    # Fallback: simple key-value regex
    result = {}
    for line in fm_text.strip().split("\n"):
        kv_match = re.match(r"^(\w+)\s*:\s*(.+)$", line)
        if kv_match:
            result[kv_match.group(1)] = kv_match.group(2).strip().strip('"').strip("'")
    return result


def check_skill_mds():
    """Check 1: All 7 skill directories have SKILL.md."""
    failed = []
    for skill in REQUIRED_SKILLS:
        path = os.path.join(REPO_ROOT, "skills", skill, "SKILL.md")
        if not os.path.isfile(path):
            failed.append(f"skills/{skill}/SKILL.md")
    return failed


def check_frontmatter():
    """Check 2: YAML frontmatter in each SKILL.md has required keys."""
    failed = []
    for skill in REQUIRED_SKILLS:
        path = os.path.join(REPO_ROOT, "skills", skill, "SKILL.md")
        if not os.path.isfile(path):
            failed.append(f"skills/{skill}/SKILL.md (file missing)")
            continue
        fm = read_yaml_frontmatter(path)
        if fm is None:
            failed.append(f"skills/{skill}/SKILL.md (no YAML frontmatter)")
            continue
        missing = [k for k in REQUIRED_FRONTMATTER_KEYS if k not in fm]
        if missing:
            failed.append(
                f"skills/{skill}/SKILL.md (missing keys: {', '.join(missing)})"
            )
    return failed


def check_templates():
    """Check 3: All 7 templates exist (WARN only)."""
    missing = []
    for tmpl in REQUIRED_TEMPLATES:
        path = os.path.join(REPO_ROOT, "templates", tmpl)
        if not os.path.isfile(path):
            missing.append(f"templates/{tmpl}")
    return missing


def check_dispatch_consistency():
    """Check 4: SKILL.md stage names correspond to skills/ subdirectories.

    Parses the Master Dispatch SKILL.md for stage lines like:
      Stage 2a: Two-Phase Brainstorming (Product Subagent — skill: se-team-product-research)
    and cross-references against skills/ directory entries.
    """
    root_skill_path = os.path.join(REPO_ROOT, "SKILL.md")
    if not os.path.isfile(root_skill_path):
        return ["SKILL.md (root) not found — cannot check dispatch consistency"]

    with open(root_skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all skill references in the pipeline section
    # Pattern: skill: some-skill-name
    skill_refs = set(re.findall(r"skill:\s*([\w-]+)", content))

    # Also check the Dispatch Table
    table_skills = set(re.findall(r"`se-team-[\w-]+`", content))
    table_skills = {s.strip("`") for s in table_skills}

    all_refs = skill_refs | table_skills

    # Filter to only se-team-* skills
    se_team_refs = {s for s in all_refs if s.startswith("se-team-")}

    # Get actual skills/ directories
    skills_dir = os.path.join(REPO_ROOT, "skills")
    if not os.path.isdir(skills_dir):
        return ["skills/ directory not found"]

    actual_skills = set(os.listdir(skills_dir))
    actual_skills = {s for s in actual_skills if s.startswith("se-team-")}

    # Every referenced skill should exist
    missing_from_fs = se_team_refs - actual_skills

    # Every actual skill should be referenced (warning only)
    not_referenced = actual_skills - se_team_refs

    failed = []
    if missing_from_fs:
        failed.append(
            f"SKILL.md references skills not found in skills/ directory: {', '.join(sorted(missing_from_fs))}"
        )

    warnings = []
    if not_referenced:
        warnings.append(
            f"skills/ directory has skills not referenced in SKILL.md: {', '.join(sorted(not_referenced))}"
        )

    return failed, warnings


def check_reference_chain():
    """Check 5: Reference chain spec.md → architecture.md → implementation-plan.md."""
    artifacts_dir = os.path.join(REPO_ROOT, "artifacts")
    chain = ["spec.md", "architecture.md", "implementation-plan.md"]
    missing = [f for f in chain if not os.path.isfile(os.path.join(artifacts_dir, f))]
    return missing


def main():
    exit_code = 0
    total_checks = 5
    results = []

    # --- Check 1: Skill SKILL.md existence ---
    skill_md_failed = check_skill_mds()
    if skill_md_failed:
        results.append(f"[FAIL] Check 1: Missing SKILL.md files: {', '.join(skill_md_failed)}")
        exit_code = 1
    else:
        results.append("[PASS] Check 1: All 7 skill directories have SKILL.md")

    # --- Check 2: YAML frontmatter ---
    fm_failed = check_frontmatter()
    if fm_failed:
        results.append(f"[FAIL] Check 2: Frontmatter issues: {'; '.join(fm_failed)}")
        exit_code = 1
    else:
        results.append("[PASS] Check 2: All SKILL.md files have valid frontmatter")

    # --- Check 3: Templates ---
    tmpl_missing = check_templates()
    if tmpl_missing:
        results.append(
            f"[WARN] Check 3: Missing templates: {', '.join(tmpl_missing)}"
        )
    else:
        results.append("[PASS] Check 3: All 7 templates present")

    # --- Check 4: Dispatch consistency ---
    dispatch_failed, dispatch_warnings = check_dispatch_consistency()
    if dispatch_failed:
        for msg in dispatch_failed:
            results.append(f"[FAIL] Check 4: {msg}")
        exit_code = 1
    else:
        results.append("[PASS] Check 4: Master Dispatch references consistent with skills/ directory")
    for w in dispatch_warnings:
        results.append(f"[WARN] Check 4: {w}")

    # --- Check 5: Reference chain ---
    chain_missing = check_reference_chain()
    if chain_missing:
        results.append(
            f"[WARN] Check 5: Reference chain missing: {', '.join(chain_missing)}"
        )
    else:
        results.append("[PASS] Check 5: spec.md → architecture.md → implementation-plan.md chain intact")

    # Summary
    print(f"\n{'='*60}")
    print(f"  Self Health Check Report")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r}")
    print(f"{'='*60}")
    print(f"  Result: {'PASS' if exit_code == 0 else 'FAIL'}")
    print(f"{'='*60}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
