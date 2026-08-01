import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from sync_skills import check, copy_all, main as sync_main  # noqa: E402


def make_repo():
    directory = tempfile.TemporaryDirectory()
    root = Path(directory.name)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "SKILL.md").write_text("# Master\n", encoding="utf-8")
    (root / "scripts").mkdir(exist_ok=True)
    (root / "scripts/validate_artifact.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    (root / "skills").mkdir(exist_ok=True)
    for name in ("se-team-engineer", "se-team-design", "se-team-rules"):
        skill_dir = root / "skills" / name
        skill_dir.mkdir(exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return directory, root


class SyncSkillsTests(unittest.TestCase):
    def test_copy_all_mirrors_master_and_agent_skills_skipping_ignored(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                copy_all(repo, target)
                self.assertTrue((target / "software-engineering-team/SKILL.md").is_file())
                self.assertTrue((target / "software-engineering-team/scripts/validate_artifact.py").is_file())
                self.assertTrue((target / "se-team-engineer/SKILL.md").is_file())
                self.assertTrue((target / "se-team-design/SKILL.md").is_file())
                self.assertFalse((target / "se-team-rules/SKILL.md").exists())
                missing, drifted = check(repo, target)
                self.assertEqual((missing, drifted), ([], []))

    def test_check_detects_drift_on_non_ignored_skill(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                copy_all(repo, target)
                (target / "se-team-engineer/SKILL.md").write_text("# tampered\n", encoding="utf-8")
                missing, drifted = check(repo, target)
                self.assertEqual(drifted, ["se-team-engineer/SKILL.md"])
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = sync_main(["--repo", str(repo), "--target", str(target), "--check"])
                self.assertEqual(code, 1)
                self.assertIn("DRIFTED", output.getvalue())

    def test_check_ignores_se_team_rules_drift(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                copy_all(repo, target)
                # Simulate the known-divergent installed copy (Floratech rules).
                rules_dir = target / "se-team-rules"
                rules_dir.mkdir(exist_ok=True)
                (rules_dir / "SKILL.md").write_text("# se-team-rules\n# Floratech extras\n", encoding="utf-8")
                missing, drifted = check(repo, target)
                self.assertEqual((missing, drifted), ([], []))
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = sync_main(["--repo", str(repo), "--target", str(target), "--check"])
                self.assertEqual(code, 0)
                self.assertIn("OK", output.getvalue())

    def test_check_reports_missing_target_files(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                missing, drifted = check(repo, target)
                self.assertIn("software-engineering-team/SKILL.md", missing)


if __name__ == "__main__":
    unittest.main()
