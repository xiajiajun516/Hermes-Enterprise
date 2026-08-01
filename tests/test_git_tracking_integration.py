import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from fixtures import RUN, SOURCE_RUN, make_repo  # noqa: E402

HEALTH = PROJECT / "scripts/self_health_check.py"
VALIDATOR = PROJECT / "scripts/validate_artifact.py"


class GitTrackingTests(unittest.TestCase):
    def health(self, root):
        return subprocess.run([sys.executable, str(HEALTH), "--root", str(root)], text=True, capture_output=True)

    def validator(self, root, *args):
        command = [sys.executable, str(VALIDATOR)]
        if root is not None:
            command += ["--root", str(root)]
        return subprocess.run(command + list(args), text=True, capture_output=True)

    def test_health_bootstrap_tristate_uses_actual_script(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            zero = self.health(root)
            self.assertNotEqual(zero.returncode, 0)
            self.assertIn("BOOTSTRAP_PENDING", zero.stdout)
            untracked = root / f"artifacts/runs/{RUN}__manifest.json"
            untracked.parent.mkdir(parents=True)
            untracked.write_text("{}", encoding="utf-8")
            only_untracked = self.health(root)
            self.assertNotEqual(only_untracked.returncode, 0)
            self.assertNotIn("PASS:", only_untracked.stdout)
        directory, root, _, _ = make_repo()
        with directory:
            valid = self.health(root)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertIn("PASS:", valid.stdout)

    def test_health_fail_path_reports_fail_on_corrupted_tracked_manifest(self):
        directory, root, manifest, _ = make_repo()
        with directory:
            manifest.write_text("{", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", manifest.relative_to(root).as_posix()], check=True)
            failed = self.health(root)
            self.assertEqual(failed.returncode, 2)
            self.assertIn("FAIL:", failed.stdout)
            self.assertNotIn("PASS:", failed.stdout)

    def test_validator_requires_tracked_contract_in_isolated_repository(self):
        directory, root, _, _ = make_repo(with_manifest=False)
        with directory:
            contract = root / f"artifacts/runs/{RUN}__contract.md"
            rel = contract.relative_to(root).as_posix()
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", rel], check=True)
            untracked = self.validator(root, rel)
            self.assertNotEqual(untracked.returncode, 0)
            self.assertIn("BLOCKED", untracked.stdout)
            subprocess.run(["git", "-C", str(root), "add", rel], check=True)
            tracked = self.validator(root, rel)
            self.assertEqual(tracked.returncode, 0, tracked.stdout + tracked.stderr)
            self.assertIn("PASS", tracked.stdout)

    def test_validator_manifest_branch(self):
        directory, root, manifest, _ = make_repo()
        with directory:
            rel = manifest.relative_to(root).as_posix()
            valid = self.validator(root, rel)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertIn("PASS", valid.stdout)
            manifest.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", rel], check=True)
            invalid = self.validator(root, rel)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("BLOCKED", invalid.stdout)

    def test_validator_plain_artifact_branch(self):
        directory, root, _, _ = make_repo(with_manifest=False)
        with directory:
            artifact = root / f"artifacts/design/{SOURCE_RUN}__architecture.md"
            rel = artifact.relative_to(root).as_posix()
            result = self.validator(root, rel)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)
            self.assertRegex(result.stdout, r"[0-9a-f]{64}")

    def test_validator_root_flag_resolves_relative_to_root(self):
        directory, root, manifest, _ = make_repo()
        with directory:
            rel = manifest.relative_to(root).as_posix()
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "--root", str(root), rel],
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)

    def test_authorize_accepts_tracked_hash_matching_input(self):
        directory, root, _, _ = make_repo()
        with directory:
            contract = f"artifacts/runs/{RUN}__contract.md"
            source = f"artifacts/design/{SOURCE_RUN}__architecture.md"
            result = self.validator(root, "--authorize", contract, source)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("AUTHORIZED", result.stdout)

    def test_authorize_rejects_missing_untracked_and_hash_mismatched_input(self):
        directory, root, _, _ = make_repo()
        with directory:
            contract = f"artifacts/runs/{RUN}__contract.md"
            source = f"artifacts/design/{SOURCE_RUN}__architecture.md"
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", source], check=True)
            untracked = self.validator(root, "--authorize", contract, source)
            self.assertNotEqual(untracked.returncode, 0)
            self.assertIn("BLOCKED", untracked.stdout)
            subprocess.run(["git", "-C", str(root), "add", source], check=True)
            (root / source).write_text("tampered", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", source], check=True)
            mismatch = self.validator(root, "--authorize", contract, source)
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("BLOCKED", mismatch.stdout)

    def test_authorize_rejects_undeclared_input(self):
        directory, root, _, _ = make_repo()
        with directory:
            contract = f"artifacts/runs/{RUN}__contract.md"
            undeclared = f"artifacts/engineer/{RUN}__implementation-report.md"
            result = self.validator(root, "--authorize", contract, undeclared)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOCKED", result.stdout)

    def test_validate_artifact_main_in_process_all_branches(self):
        import contextlib
        import io

        from validate_artifact import authorize, main as validate_main

        directory, root, manifest, _ = make_repo()
        with directory:
            contract_rel = f"artifacts/runs/{RUN}__contract.md"
            manifest_rel = manifest.relative_to(root).as_posix()
            artifact_rel = f"artifacts/design/{SOURCE_RUN}__architecture.md"
            for rel, expected in (
                (contract_rel, 0),
                (manifest_rel, 0),
                (artifact_rel, 0),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(validate_main(rel, root), expected, rel)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validate_main("artifacts/spec.md", root), 1)
                self.assertEqual(validate_main(manifest_rel, root / "nonexistent"), 1)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(authorize(contract_rel, artifact_rel, root), 0)
                self.assertEqual(authorize(contract_rel, "artifacts/engineer/x.md", root), 1)

    def test_health_main_in_process_states(self):
        import contextlib
        import io

        from self_health_check import main as health_main

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(health_main(root), 1)
                self.assertIn("BOOTSTRAP_PENDING", out.getvalue())
        directory, root, manifest, _ = make_repo()
        with directory:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(health_main(root), 0)
                self.assertIn("PASS:", out.getvalue())
            manifest.write_text("{", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", manifest.relative_to(root).as_posix()], check=True)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(health_main(root), 2)
                self.assertIn("FAIL:", out.getvalue())


if __name__ == "__main__":
    unittest.main()
