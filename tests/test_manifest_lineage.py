import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, "scripts")
from manifest_lineage import validate_manifest, validate_parent_graph

RUN = "20260730T155029-637"
SOURCE_RUN = "20260730T150000-001"


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strict_contract(run, source_sha):
    return f'''---
contract_version: "1.0"
run_id: "{run}"
created_at_utc: "2026-07-30T15:50:29.637Z"
tier: "P2"
stage: "2d"
attempt: 1
agent_display_name: "Engineer"
agent_slug: "engineer"
parent_run_id: null
language: "en-US"
inputs:
  - path: "artifacts/architect/{SOURCE_RUN}__architecture.md"
    artifact_name: "architecture"
    sha256: "{source_sha}"
    producer_run_id: "{SOURCE_RUN}"
outputs:
  - agent_slug: "engineer"
    artifact_name: "implementation-report"
    target_path: "artifacts/engineer/{run}__implementation-report.md"
    template: "templates/task-contract-template.md"
    write_mode: "create-new"
---
## Run Identity
run_id: identity
created_at_utc: time
## Goal & Scope
goal: validation
scope: future
## Source of Truth
source: architecture
## Environment SOP
command: gate
## Artifact I/O Contract
inputs: exact
outputs: exact
## Checksum / Verification
sha256: actual
verification: command
## Hard Prohibitions
prohibited: legacy
## Final Report Protocol
report: results
'''


class LineageTests(unittest.TestCase):
    def fixture(self):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        source = root / f"artifacts/architect/{SOURCE_RUN}__architecture.md"
        output = root / f"artifacts/engineer/{RUN}__implementation-report.md"
        contract = root / f"artifacts/runs/{RUN}__contract.md"
        for path, content in ((source, "architecture"), (output, "report")):
            path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")
        contract.parent.mkdir(parents=True); contract.write_text(strict_contract(RUN, digest(source)), encoding="utf-8")
        manifest = root / f"artifacts/runs/{RUN}__manifest.json"
        payload = {"manifest_version": "1.0", "run_id": RUN, "contract_path": contract.relative_to(root).as_posix(), "contract_sha256": digest(contract), "parent_run_id": None, "status": "completed", "inputs": [{"path": source.relative_to(root).as_posix(), "artifact_name": "architecture", "sha256": digest(source), "producer_run_id": SOURCE_RUN}], "outputs": [{"path": output.relative_to(root).as_posix(), "artifact_name": "implementation-report", "sha256": digest(output)}], "verification": [{"command": "python -m unittest", "expected_exit_code": 0, "exit_code": 0, "result": "PASS", "evidence_paths": []}], "created_at_utc": "2026-07-30T15:50:29.637Z", "closed_at_utc": "2026-07-30T15:51:00.000Z"}
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "artifacts"], check=True)
        return directory, root, manifest, payload

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
            lambda m: m.update(verification=[{"command": "test", "expected_exit_code": 0, "exit_code": 1, "result": "PASS", "evidence_paths": []}]),
            lambda m: m.update(verification=[]),
        ]
        for mutate in mutations:
            directory, root, manifest, payload = self.fixture()
            with directory, self.subTest(mutate=mutate):
                mutate(payload); manifest.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(ValueError): validate_manifest(manifest.relative_to(root).as_posix(), root)

    def test_blocked_manifest_needs_structural_nonpass_evidence(self):
        directory, root, manifest, payload = self.fixture()
        with directory:
            payload["status"] = "blocked"
            payload["verification"] = [{"command": "gate", "expected_exit_code": 0, "exit_code": 1, "result": "BLOCKED", "evidence_paths": []}]
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(validate_manifest(manifest.relative_to(root).as_posix(), root)["status"], "blocked")

    def test_parent_cycle_rejected(self):
        with self.assertRaises(ValueError): validate_parent_graph({"a": "b", "b": "a"})


if __name__ == "__main__": unittest.main()
