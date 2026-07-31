import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
from artifact_io import create_new_utf8, create_timestamped_artifact, sha256_file
from artifact_naming import artifact_path


class IoTests(unittest.TestCase):
    def test_exclusive_write_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            create_new_utf8(p, "one")
            before = sha256_file(p)
            with self.assertRaises(FileExistsError):
                create_new_utf8(p, "two")
            self.assertEqual(before, sha256_file(p))

    def test_timestamped_artifact_retries_with_sequence_suffix(self):
        instant = datetime(2026, 7, 30, 15, 50, 29, 637000, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = artifact_path("engineer", "implementation-report", instant)
            create_new_utf8(root / base, "first")
            rel, digest = create_timestamped_artifact(root, "engineer", "implementation-report", instant, "second")
            self.assertEqual(rel, "artifacts/engineer/20260730T155029-637-001__implementation-report.md")
            self.assertEqual(digest, sha256_file(root / rel))
            self.assertEqual((root / rel).read_text(encoding="utf-8"), "second")

    def test_timestamped_artifact_sequence_exhaustion_raises(self):
        instant = datetime(2026, 7, 30, 15, 50, 29, 637000, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for sequence in [None, *range(1, 1000)]:
                rel = artifact_path("engineer", "implementation-report", instant, sequence)
                create_new_utf8(root / rel, "x")
            with self.assertRaises(FileExistsError) as context:
                create_timestamped_artifact(root, "engineer", "implementation-report", instant, "x")
            self.assertIn("timestamp sequence exhausted", str(context.exception))


if __name__ == "__main__":
    unittest.main()
