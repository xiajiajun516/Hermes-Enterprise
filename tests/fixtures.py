"""Shared temp-repository fixtures for the test suite (U-15)."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from artifact_naming import iso_utc_for_run_id

RUN = "20260730T155029-637"
SOURCE_RUN = "20260730T150000-001"
TEMPLATE = "templates/implementation-report-template.md"
TEMPLATE_TEXT = "# Implementation Report — template\n## Run Identity\n## Source Artifacts\n"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strict_contract(run, source_sha, source_run=SOURCE_RUN, template=TEMPLATE, parent=None):
    parent_line = "null" if parent is None else f'"{parent}"'
    return f"""---
contract_version: "1.0"
run_id: "{run}"
created_at_utc: "2026-07-30T15:50:29.637Z"
tier: "P2"
stage: "2d"
attempt: 1
agent_display_name: "Engineer"
agent_slug: "engineer"
parent_run_id: {parent_line}
language: "en-US"
inputs:
  - path: "artifacts/architect/{source_run}__architecture.md"
    artifact_name: "architecture"
    sha256: "{source_sha}"
    producer_run_id: "{source_run}"
outputs:
  - agent_slug: "engineer"
    artifact_name: "implementation-report"
    target_path: "artifacts/engineer/{run}__implementation-report.md"
    template: "{template}"
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
"""


def chain_contract(run, slug, stage, output_name, input_item=None, parent=None):
    """Contract for an arbitrary stage; input_item is a dict with path/artifact_name/sha256/producer_run_id."""
    created_at = iso_utc_for_run_id(run)
    parent_line = "null" if parent is None else f'"{parent}"'
    inputs = ""
    if input_item is not None:
        inputs = f"""inputs:
  - path: "{input_item['path']}"
    artifact_name: "{input_item['artifact_name']}"
    sha256: "{input_item['sha256']}"
    producer_run_id: "{input_item['producer_run_id']}"
"""
    else:
        inputs = "inputs: []\n"
    return f"""---
contract_version: "1.0"
run_id: "{run}"
created_at_utc: "{created_at}"
tier: "P1"
stage: "{stage}"
attempt: 1
agent_display_name: "{slug}"
agent_slug: "{slug}"
parent_run_id: {parent_line}
language: "en-US"
{inputs}outputs:
  - agent_slug: "{slug}"
    artifact_name: "{output_name}"
    target_path: "artifacts/{slug}/{run}__{output_name}.md"
    template: "templates/{output_name}-template.md"
    write_mode: "create-new"
---
## Run Identity
run_id: identity
created_at_utc: time
## Goal & Scope
goal: chain rehearsal
scope: future
## Source of Truth
source: upstream
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
"""


def make_repo(with_manifest=True, contract=None, template=TEMPLATE, with_contract=True):
    """Create an isolated temp git repo with the template file, source artifact,
    output artifact, contract and (optionally) manifest, all git-tracked."""
    directory = tempfile.TemporaryDirectory()
    root = Path(directory.name)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    template_path = root / template
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(TEMPLATE_TEXT, encoding="utf-8")
    source = root / f"artifacts/architect/{SOURCE_RUN}__architecture.md"
    output = root / f"artifacts/engineer/{RUN}__implementation-report.md"
    contract_path = root / f"artifacts/runs/{RUN}__contract.md"
    for path, content in ((source, "architecture"), (output, "report")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    # Producer run: a fully valid, tracked architect run whose outputs declare the
    # source artifact (required by the input-lineage check).
    template_arch = root / "templates/architecture-template.md"
    template_arch.write_text("# Architecture — template\n## Run Identity\n## Source Artifacts\n", encoding="utf-8")
    producer_contract = root / f"artifacts/runs/{SOURCE_RUN}__contract.md"
    producer_contract.parent.mkdir(parents=True, exist_ok=True)
    producer_contract.write_text(chain_contract(SOURCE_RUN, "architect", "2b", "architecture"), encoding="utf-8")
    producer_manifest = root / f"artifacts/runs/{SOURCE_RUN}__manifest.json"
    producer_payload = {
        "manifest_version": "1.0",
        "run_id": SOURCE_RUN,
        "contract_path": producer_contract.relative_to(root).as_posix(),
        "contract_sha256": digest(producer_contract),
        "parent_run_id": None,
        "status": "completed",
        "inputs": [],
        "outputs": [{"path": source.relative_to(root).as_posix(), "artifact_name": "architecture", "sha256": digest(source)}],
        "verification": [{
            "command": "python -m unittest", "expected_exit_code": 0, "exit_code": 0,
            "result": "PASS", "evidence_paths": [],
        }],
        "created_at_utc": "2026-07-30T15:00:00.001Z",
        "closed_at_utc": "2026-07-30T15:01:00.000Z",
    }
    producer_manifest.write_text(json.dumps(producer_payload, indent=2), encoding="utf-8")
    if with_contract:
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(contract or strict_contract(RUN, digest(source)), encoding="utf-8")
    manifest = root / f"artifacts/runs/{RUN}__manifest.json"
    payload = None
    if with_manifest:
        payload = {
            "manifest_version": "1.0",
            "run_id": RUN,
            "contract_path": contract_path.relative_to(root).as_posix(),
            "contract_sha256": digest(contract_path),
            "parent_run_id": None,
            "status": "completed",
            "inputs": [{
                "path": source.relative_to(root).as_posix(),
                "artifact_name": "architecture",
                "sha256": digest(source),
                "producer_run_id": SOURCE_RUN,
            }],
            "outputs": [{
                "path": output.relative_to(root).as_posix(),
                "artifact_name": "implementation-report",
                "sha256": digest(output),
            }],
            "verification": [{
                "command": "python -m unittest",
                "expected_exit_code": 0,
                "exit_code": 0,
                "result": "PASS",
                "evidence_paths": [],
            }],
            "created_at_utc": "2026-07-30T15:50:29.637Z",
            "closed_at_utc": "2026-07-30T15:51:00.000Z",
        }
        manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "artifacts", "templates"], check=True)
    return directory, root, manifest, payload
