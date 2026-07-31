import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from close_run import create_contract, main as close_main  # noqa: E402
from fixtures import RUN, SOURCE_RUN, chain_contract, digest, make_repo, strict_contract  # noqa: E402
from manifest_lineage import tracked_manifest_paths, validate_manifest  # noqa: E402
from self_health_check import main as health_main  # noqa: E402

VERIFICATION_PASS = json.dumps([{
    "command": "python -m unittest",
    "expected_exit_code": 0,
    "exit_code": 0,
    "result": "PASS",
    "evidence_paths": [],
}])
VERIFICATION_FAIL = json.dumps([{
    "command": "gate",
    "expected_exit_code": 0,
    "exit_code": 1,
    "result": "FAIL",
    "evidence_paths": [],
}])
CLOSED_AT = "2026-07-30T15:51:00.000Z"


def close(root, *args):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = close_main(["--root", str(root), "manifest", *args])
    return code, output.getvalue()


def make_repo_without_manifest():
    return make_repo(with_manifest=False)


def make_repo_without_contract():
    return make_repo(with_manifest=False, with_contract=False)


class CloseRunTests(unittest.TestCase):
    def test_manifest_happy_path_produces_valid_tracked_manifest(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            code, text = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md",
                               "--status", "completed", "--verification", VERIFICATION_PASS,
                               "--closed-at", CLOSED_AT)
            self.assertEqual(code, 0, text)
            self.assertIn("CLOSED", text)
            manifest_rel = f"artifacts/runs/{RUN}__manifest.json"
            self.assertTrue((root / manifest_rel).is_file())
            subprocess.run(["git", "-C", str(root), "add", manifest_rel], check=True)
            self.assertEqual(validate_manifest(manifest_rel, root)["status"], "completed")
            self.assertIn(manifest_rel, tracked_manifest_paths(root))

    def test_manifest_rerun_is_rejected_as_immutable(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            first = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md",
                          "--status", "completed", "--verification", VERIFICATION_PASS,
                          "--closed-at", CLOSED_AT)
            self.assertEqual(first[0], 0, first[1])
            second = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md",
                           "--status", "completed", "--verification", VERIFICATION_PASS,
                           "--closed-at", CLOSED_AT)
            self.assertEqual(second[0], 1, second[1])
            self.assertIn("BLOCKED: manifest already exists", second[1])

    def test_wrong_status_rejected_when_evidence_does_not_match(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            failing = json.dumps([{
                "command": "test", "expected_exit_code": 0, "exit_code": 1,
                "result": "FAIL", "evidence_paths": [],
            }])
            code, text = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md",
                               "--status", "completed", "--verification", failing,
                               "--closed-at", CLOSED_AT)
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED:", text)
            self.assertFalse((root / f"artifacts/runs/{RUN}__manifest.json").exists())

    def test_tampered_input_hash_rejected_and_nothing_written(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            source = root / f"artifacts/architect/{SOURCE_RUN}__architecture.md"
            source.write_text("tampered", encoding="utf-8")
            code, text = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md",
                               "--status", "completed", "--verification", VERIFICATION_PASS,
                               "--closed-at", CLOSED_AT)
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED: input hash mismatch", text)
            self.assertFalse((root / f"artifacts/runs/{RUN}__manifest.json").exists())

    def test_missing_output_rejected(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            (root / f"artifacts/engineer/{RUN}__implementation-report.md").unlink()
            code, text = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md",
                               "--status", "completed", "--verification", VERIFICATION_PASS,
                               "--closed-at", CLOSED_AT)
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED: output missing", text)
            self.assertFalse((root / f"artifacts/runs/{RUN}__manifest.json").exists())

    def test_untracked_contract_rejected(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            rel = f"artifacts/runs/{RUN}__contract.md"
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", rel], check=True)
            code, text = close(root, "--contract", rel, "--status", "completed",
                               "--verification", VERIFICATION_PASS, "--closed-at", CLOSED_AT)
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED: contract untracked", text)

    def test_blocked_run_can_close_with_zero_outputs(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            out = root / f"artifacts/engineer/{RUN}__implementation-report.md"
            subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", out.relative_to(root).as_posix()], check=True)
            out.unlink()
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "abort: drop declared output"], check=True)
            code, text = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md", "--status", "blocked",
                               "--verification", VERIFICATION_FAIL, "--closed-at", CLOSED_AT)
            self.assertEqual(code, 0, text)
            self.assertIn("CLOSED", text)
            payload = json.loads((root / f"artifacts/runs/{RUN}__manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["outputs"], [])
            self.assertEqual(payload["status"], "blocked")

    def test_close_rejects_undeclared_working_tree_changes(self):
        directory, root, _, _ = make_repo_without_manifest()
        with directory:
            template = root / "templates/implementation-report-template.md"
            template.write_text("# Tampered\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "templates"], check=True)
            code, text = close(root, "--contract", f"artifacts/runs/{RUN}__contract.md", "--status", "completed",
                               "--verification", VERIFICATION_PASS, "--closed-at", CLOSED_AT)
            self.assertEqual(code, 1)
            self.assertIn("undeclared working-tree changes", text)
            self.assertFalse((root / f"artifacts/runs/{RUN}__manifest.json").exists())

    def test_contract_creation_validates_before_write(self):
        directory, root, _, _ = make_repo_without_contract()
        with directory:
            filled = root / "filled-contract.md"
            filled.write_text(strict_contract(RUN, digest(root / f"artifacts/architect/{SOURCE_RUN}__architecture.md")), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = create_contract(filled, root)
            self.assertEqual(code, 0, output.getvalue())
            contract_rel = f"artifacts/runs/{RUN}__contract.md"
            self.assertTrue((root / contract_rel).is_file())
            duplicate = io.StringIO()
            with contextlib.redirect_stdout(duplicate):
                code = create_contract(filled, root)
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED: contract already exists", duplicate.getvalue())

    def test_contract_creation_rejects_invalid_input(self):
        directory, root, _, _ = make_repo_without_contract()
        with directory:
            bad = root / "bad-contract.md"
            bad.write_text(strict_contract(RUN, "a" * 64).replace('tier: "P2"', 'tier: "P9"'), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = create_contract(bad, root)
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED:", output.getvalue())
            self.assertFalse((root / f"artifacts/runs/{RUN}__contract.md").exists())


class EndToEndRehearsalTests(unittest.TestCase):
    def test_full_three_stage_chain_health_pass(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            template_paths = {
                "spec": "templates/spec-template.md",
                "architecture": "templates/architecture-template.md",
                "implementation-report": "templates/implementation-report-template.md",
            }
            for name in template_paths:
                template = root / template_paths[name]
                template.parent.mkdir(parents=True, exist_ok=True)
                template.write_text(f"# {name} — template\n## Run Identity\n## Source Artifacts\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "fixture"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "templates"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture: templates"], check=True)

            stages = [
                ("20260731T100000-001", "product-research", "2a", "spec", None, None),
                ("20260731T110000-002", "architect", "2b", "architecture", "20260731T100000-001", "spec"),
                ("20260731T120000-003", "engineer", "2d", "implementation-report", "20260731T110000-002", "architecture"),
            ]
            previous_output = None
            for run, slug, stage, output_name, parent, input_name in stages:
                input_item = None
                if input_name is not None:
                    input_path = f"artifacts/{previous_output['slug']}/{previous_output['run']}__{input_name}.md"
                    input_item = {
                        "path": input_path,
                        "artifact_name": input_name,
                        "sha256": digest(root / input_path),
                        "producer_run_id": previous_output["run"],
                    }
                contract_text = chain_contract(run, slug, stage, output_name, input_item, parent)
                contract = root / f"artifacts/runs/{run}__contract.md"
                contract.parent.mkdir(parents=True, exist_ok=True)
                contract.write_text(contract_text, encoding="utf-8")
                output = root / f"artifacts/{slug}/{run}__{output_name}.md"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(f"{output_name} content", encoding="utf-8")
                subprocess.run(["git", "-C", str(root), "add", "artifacts"], check=True)
                subprocess.run(["git", "-C", str(root), "commit", "-qm", f"fixture: {run} contract+output"], check=True)
                code, text = close(root, "--contract", contract.relative_to(root).as_posix(),
                                   "--status", "completed", "--verification", VERIFICATION_PASS,
                                   "--closed-at", "2026-07-31T13:00:00.000Z")
                self.assertEqual(code, 0, text)
                subprocess.run(["git", "-C", str(root), "add", f"artifacts/runs/{run}__manifest.json"], check=True)
                subprocess.run(["git", "-C", str(root), "commit", "-qm", f"fixture: {run} manifest"], check=True)
                previous_output = {"run": run, "slug": slug}

            output_stream = io.StringIO()
            with contextlib.redirect_stdout(output_stream):
                health_code = health_main(root)
            self.assertEqual(health_code, 0, output_stream.getvalue())
            self.assertIn("PASS:", output_stream.getvalue())
            self.assertEqual(len(tracked_manifest_paths(root)), 3)


if __name__ == "__main__":
    unittest.main()
