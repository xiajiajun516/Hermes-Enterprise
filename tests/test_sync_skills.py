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
    (root / "scripts/sync_skills.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    (root / "skills").mkdir(exist_ok=True)
    for name in ("se-team-engineer", "se-team-design", "se-team-rules"):
        skill_dir = root / "skills" / name
        skill_dir.mkdir(exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    # repo-only files that must NOT be mirrored
    (root / "README.md").write_text("# readme\n", encoding="utf-8")
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests/test_x.py").write_text("", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return directory, root


class SyncSkillsTests(unittest.TestCase):
    def test_copy_all_mirrors_master_scripts_and_all_role_skills(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                copy_all(repo, target)
                self.assertTrue((target / "software-engineering-team/SKILL.md").is_file())
                self.assertTrue((target / "software-engineering-team/scripts/sync_skills.py").is_file())
                for name in ("se-team-engineer", "se-team-design", "se-team-rules"):
                    self.assertTrue((target / name / "SKILL.md").is_file(), name)
                # repo-only files are not mirrored
                self.assertFalse((target / "software-engineering-team/README.md").exists())
                self.assertFalse((target / "software-engineering-team/tests").exists())
                missing, drifted = check(repo, target)
                self.assertEqual((missing, drifted), ([], []))

    def test_check_detects_drift_on_role_skill(self):
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

    def test_check_detects_drift_on_se_team_rules(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                copy_all(repo, target)
                (target / "se-team-rules/SKILL.md").write_text("# tampered\n", encoding="utf-8")
                missing, drifted = check(repo, target)
                self.assertEqual(drifted, ["se-team-rules/SKILL.md"])
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = sync_main(["--repo", str(repo), "--target", str(target), "--check"])
                self.assertEqual(code, 1)
                self.assertIn("DRIFTED", output.getvalue())

    def test_role_skill_references_files_are_mirrored(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                reference = repo / "skills/se-team-engineer/references" / "api.md"
                reference.parent.mkdir(parents=True)
                reference.write_text("# api\n", encoding="utf-8")
                subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
                copy_all(repo, target)
                self.assertTrue((target / "se-team-engineer/references/api.md").is_file())

    def test_check_reports_missing_target_files(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                target = Path(target_dir)
                missing, drifted = check(repo, target)
                self.assertIn("software-engineering-team/SKILL.md", missing)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = sync_main(["--repo", str(repo), "--target", str(target), "--check"])
                self.assertEqual(code, 1)
                self.assertIn("MISSING", output.getvalue())

    def test_main_blocks_on_non_git_repo(self):
        with tempfile.TemporaryDirectory() as target_dir, tempfile.TemporaryDirectory() as not_a_repo:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = sync_main(["--repo", not_a_repo, "--target", target_dir, "--check"])
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED", output.getvalue())

    def test_main_copy_path_syncs(self):
        directory, repo = make_repo()
        with directory:
            with tempfile.TemporaryDirectory() as target_dir:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = sync_main(["--repo", str(repo), "--target", str(target_dir)])
                self.assertEqual(code, 0)
                self.assertIn("synced", output.getvalue())
                self.assertTrue((Path(target_dir) / "software-engineering-team/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
