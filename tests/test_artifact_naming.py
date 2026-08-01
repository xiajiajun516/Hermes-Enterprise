import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
from artifact_naming import ALLOWED_SLUGS, artifact_path, run_id_from_datetime, validate_output, validate_relative_path


class NamingTests(unittest.TestCase):
    def test_fixed_slug_and_utc_path(self):
        instant = datetime(2026, 7, 30, 15, 50, 29, 637000, tzinfo=timezone.utc)
        self.assertEqual(run_id_from_datetime(instant), "20260730T155029-637")
        expected = "artifacts/engineer/20260730T155029-637__implementation-report.md"
        self.assertEqual(artifact_path("engineer", "implementation-report", instant), expected)

    def test_rejects_legacy_and_escape(self):
        for path in (
            "artifacts/spec.md",
            "../x",
            "artifacts/engineer/latest.md",
            "artifacts" + chr(92) + "engineer" + chr(92) + "x.md",
        ):
            self.assertFalse(validate_relative_path(path))

    def test_accepts_valid_artifact_contract_and_manifest_paths(self):
        positive = (
            "artifacts/engineer/20260730T155029-637__implementation-report.md",
            "artifacts/engineer/20260730T155029-637-001__implementation-report.md",
            "artifacts/design/20260730T155029-637__spec.md",
            "artifacts/runs/20260730T155029-637__contract.md",
            "artifacts/runs/20260730T155029-637__manifest.json",
        )
        for path in positive:
            with self.subTest(path=path):
                self.assertTrue(validate_relative_path(path))

    def test_validate_output_direct_matches_and_mismatches(self):
        instant = datetime(2026, 7, 30, 15, 50, 29, 637000, tzinfo=timezone.utc)
        good = artifact_path("engineer", "implementation-report", instant)
        self.assertTrue(validate_output("engineer", "implementation-report", good))
        mismatches = (
            ("engineer", "release", good),
            ("qa-release", "implementation-report", good),
            ("engineer", "implementation-report", good.replace("engineer/", "design/")),
            ("engineer", "implementation-report", good.replace("__implementation-report.md", "__spec.md")),
            ("engineer", "implementation-report", "artifacts/engineer/legacy.md"),
        )
        for slug, name, path in mismatches:
            with self.subTest(slug=slug, name=name, path=path):
                self.assertFalse(validate_output(slug, name, path))

    def test_every_allowed_slug_artifact_has_template(self):
        project = Path(__file__).resolve().parents[1]
        for slug, names in ALLOWED_SLUGS.items():
            for name in names:
                template = project / "templates" / f"{name}-template.md"
                self.assertTrue(template.is_file(), f"missing template for {slug}/{name}")


if __name__ == "__main__":
    unittest.main()
