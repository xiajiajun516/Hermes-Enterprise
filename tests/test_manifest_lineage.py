import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from manifest_lineage import validate_manifest, validate_manifest_data, validate_parent_graph

from fixtures import RUN, SOURCE_RUN, make_repo


class LineageTests(unittest.TestCase):
    def fixture(self):
        return make_repo()

    def test_valid_manifest_cross_validates_contract_and_actual_files(self):
        directory, root, manifest, _ = self.fixture()
        with directory:
            self.assertEqual(validate_manifest(manifest.relative_to(root).as_posix(), root)["status"], "completed")

    def test_rejects_incomplete_or_inconsistent_manifest_schema(self):
        mutations = [
            lambda m: m.update(manifest_version="2.0"),
            lambda m: m.update(run_id="20260730T155030-637"),
            lambda m: m.update(contract_sha256="A" * 64),
            lambda m: m["outputs"][0].update(artifact_name="release"),
            lambda m: m["inputs"][0].update(sha256="c" * 64),
            lambda m: m.update(status="nonsense"),
            lambda m: m.update(verification=[{
                "command": "test", "expected_exit_code": 0, "exit_code": 1,
                "result": "PASS", "evidence_paths": [],
            }]),
            lambda m: m.update(verification=[]),
        ]
        for mutate in mutations:
            directory, root, manifest, payload = self.fixture()
            with directory, self.subTest(mutate=mutate):
                mutate(payload)
                manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                with self.assertRaises(ValueError):
                    validate_manifest(manifest.relative_to(root).as_posix(), root)

    def test_blocked_manifest_needs_structural_nonpass_evidence(self):
        directory, root, manifest, payload = self.fixture()
        with directory:
            payload["status"] = "blocked"
            payload["verification"] = [{
                "command": "gate", "expected_exit_code": 0, "exit_code": 1,
                "result": "BLOCKED", "evidence_paths": [],
            }]
            manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self.assertEqual(validate_manifest(manifest.relative_to(root).as_posix(), root)["status"], "blocked")

    def test_parent_cycle_rejected(self):
        with self.assertRaises(ValueError):
            validate_parent_graph({"a": "b", "b": "a"})

    def test_parent_must_predate_child(self):
        with self.assertRaises(ValueError):
            validate_parent_graph({"20260731T120000-003": "20260731T130000-004"})

    def test_older_parent_accepted(self):
        validate_parent_graph({
            "20260731T120000-003": "20260731T110000-002",
            "20260731T110000-002": None,
        })

    def test_precommit_mode_skips_only_manifest_tracking_gate(self):
        directory, root, manifest, payload = self.fixture()
        with directory:
            rel = f"artifacts/runs/{RUN}__manifest.json"
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", rel], check=True)
            self.assertEqual(validate_manifest_data(payload, rel, root, require_tracked=False)["status"], "completed")
            with self.assertRaises(ValueError):
                validate_manifest_data(payload, rel, root)

    def test_missing_template_file_rejected(self):
        directory, root, _, payload = self.fixture()
        with directory:
            (root / "templates/implementation-report-template.md").unlink()
            rel = f"artifacts/runs/{RUN}__manifest.json"
            with self.assertRaises(ValueError):
                validate_manifest_data(payload, rel, root, require_tracked=False)

    def test_producer_lineage_required(self):
        directory, root, manifest, _ = self.fixture()
        with directory:
            producer_rel = f"artifacts/runs/{SOURCE_RUN}__manifest.json"
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", producer_rel], check=True)
            with self.assertRaisesRegex(ValueError, "producer lineage missing"):
                validate_manifest(manifest.relative_to(root).as_posix(), root)

    def test_closed_at_must_follow_created_at(self):
        directory, root, manifest, payload = self.fixture()
        with directory:
            payload["closed_at_utc"] = "2026-07-30T15:49:00.000Z"
            manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "closed_at precedes created_at"):
                validate_manifest(manifest.relative_to(root).as_posix(), root)

    def test_created_at_must_match_contract(self):
        directory, root, manifest, payload = self.fixture()
        with directory:
            payload["created_at_utc"] = "2099-01-01T00:00:00.000Z"
            payload["closed_at_utc"] = "2099-01-01T00:00:01.000Z"
            manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "contract mismatch"):
                validate_manifest(manifest.relative_to(root).as_posix(), root)

    def test_verification_result_must_match_exit_code(self):
        directory, root, manifest, payload = self.fixture()
        with directory:
            payload["status"] = "blocked"
            payload["verification"] = [{
                "command": "gate", "expected_exit_code": 0, "exit_code": 0,
                "result": "FAIL", "evidence_paths": [],
            }]
            manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "contradicts exit code"):
                validate_manifest(manifest.relative_to(root).as_posix(), root)


if __name__ == "__main__":
    unittest.main()
