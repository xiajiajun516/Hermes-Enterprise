import subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "scripts")
import test_manifest_lineage as lineage

PROJECT = Path(__file__).resolve().parents[1]
HEALTH = PROJECT / "scripts/self_health_check.py"
VALIDATOR = PROJECT / "scripts/validate_artifact.py"


class GitTrackingTests(unittest.TestCase):
    def health(self, root):
        return subprocess.run([sys.executable, str(HEALTH), "--root", str(root)], text=True, capture_output=True)

    def test_health_bootstrap_tristate_uses_actual_script(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            zero = self.health(root)
            self.assertNotEqual(zero.returncode, 0)
            self.assertIn("BOOTSTRAP_PENDING", zero.stdout)
            untracked = root / f"artifacts/runs/{lineage.RUN}__manifest.json"
            untracked.parent.mkdir(parents=True); untracked.write_text("{}", encoding="utf-8")
            only_untracked = self.health(root)
            self.assertNotEqual(only_untracked.returncode, 0)
            self.assertNotIn("PASS:", only_untracked.stdout)
        case = lineage.LineageTests()
        directory, root, _, _ = case.fixture()
        with directory:
            valid = self.health(root)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertIn("PASS:", valid.stdout)

    def test_validator_requires_tracked_contract_in_isolated_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            contract = root / f"artifacts/runs/{lineage.RUN}__contract.md"
            contract.parent.mkdir(parents=True)
            contract.write_text(lineage.strict_contract(lineage.RUN, "a" * 64), encoding="utf-8")
            command = [sys.executable, str(VALIDATOR), "--root", str(root), contract.relative_to(root).as_posix()]
            untracked = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(untracked.returncode, 0)
            self.assertIn("BLOCKED", untracked.stdout)
            subprocess.run(["git", "-C", directory, "add", contract.relative_to(root).as_posix()], check=True)
            tracked = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(tracked.returncode, 0, tracked.stdout + tracked.stderr)
            self.assertIn("PASS", tracked.stdout)


if __name__ == "__main__": unittest.main()
