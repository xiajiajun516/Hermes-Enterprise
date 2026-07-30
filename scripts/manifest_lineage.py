"""Manifest and lineage validation for tracked future runs."""
import json
import re
import subprocess
from pathlib import Path

from artifact_io import sha256_file
from artifact_naming import RUN_RE, iso_utc_for_run_id, validate_relative_path
from task_contract import SHA_RE, parse_and_validate_contract


MANIFEST_FIELDS = {"manifest_version", "run_id", "contract_path", "contract_sha256", "parent_run_id", "status", "inputs", "outputs", "verification", "created_at_utc", "closed_at_utc"}


def _tracked_all(root):
    return set(subprocess.run(["git", "-C", str(root), "ls-files"], text=True, capture_output=True, check=False).stdout.splitlines())


def tracked_manifest_paths(root):
    result = subprocess.run(["git", "-C", str(root), "ls-files", "--", "artifacts/runs/*__manifest.json"], text=True, capture_output=True, check=False)
    return [path for path in result.stdout.splitlines() if path]


def validate_parent_graph(parents):
    for node in parents:
        seen, current = set(), node
        while current is not None:
            if current in seen: raise ValueError("parent cycle")
            seen.add(current); current = parents.get(current)
            if current is not None and current not in parents: raise ValueError("missing parent")


def _require_time(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", value):
        raise ValueError("invalid timestamp")


def _require_file(root, tracked, path, expected_sha, kind):
    if not isinstance(path, str) or not validate_relative_path(path) or path not in tracked:
        raise ValueError(f"BLOCKED: {kind} untracked or invalid")
    target = (root / path).resolve()
    if root not in target.parents or not target.is_file() or not isinstance(expected_sha, str) or not SHA_RE.fullmatch(expected_sha) or sha256_file(target) != expected_sha:
        raise ValueError(f"BLOCKED: {kind} hash or existence")


def _validate_verification(records, status):
    if not isinstance(records, list) or not records: raise ValueError("missing verification evidence")
    for record in records:
        if not isinstance(record, dict) or set(record) != {"command", "expected_exit_code", "exit_code", "result", "evidence_paths"}:
            raise ValueError("invalid verification schema")
        if not isinstance(record["command"], str) or not record["command"] or type(record["expected_exit_code"]) is not int or type(record["exit_code"]) is not int:
            raise ValueError("invalid verification fields")
        if record["result"] not in {"PASS", "FAIL", "BLOCKED"} or not isinstance(record["evidence_paths"], list) or not all(isinstance(path, str) and validate_relative_path(path) for path in record["evidence_paths"]):
            raise ValueError("invalid verification fields")
    all_pass = all(record["result"] == "PASS" and record["exit_code"] == record["expected_exit_code"] for record in records)
    if status == "completed" and not all_pass: raise ValueError("failed verification")
    if status != "completed" and all_pass: raise ValueError("non-completed manifest lacks failure evidence")


def validate_manifest(path, root, tracked_paths=None):
    root = Path(root).resolve()
    rel = Path(path).as_posix()
    tracked_manifests = set(tracked_paths if tracked_paths is not None else tracked_manifest_paths(root))
    if rel not in tracked_manifests: raise ValueError("BLOCKED: manifest untracked")
    manifest_path = root / rel
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != MANIFEST_FIELDS or data["manifest_version"] != "1.0" or data["status"] not in {"completed", "blocked", "failed"}:
        raise ValueError("invalid manifest")
    if not isinstance(data["run_id"], str) or not RUN_RE.fullmatch(data["run_id"]) or rel != f"artifacts/runs/{data['run_id']}__manifest.json":
        raise ValueError("manifest run id mismatch")
    _require_time(data["created_at_utc"]); _require_time(data["closed_at_utc"])
    if data["parent_run_id"] is not None and (not isinstance(data["parent_run_id"], str) or not RUN_RE.fullmatch(data["parent_run_id"])):
        raise ValueError("invalid parent run id")
    tracked = _tracked_all(root)
    contract_path = data["contract_path"]
    if contract_path != f"artifacts/runs/{data['run_id']}__contract.md": raise ValueError("contract run id mismatch")
    _require_file(root, tracked, contract_path, data["contract_sha256"], "contract")
    contract = parse_and_validate_contract(root / contract_path)
    if contract["run_id"] != data["run_id"] or contract["parent_run_id"] != data["parent_run_id"] or contract["inputs"] != data["inputs"]:
        raise ValueError("contract mismatch")
    if not isinstance(data["outputs"], list) or len(data["outputs"]) != len(contract["outputs"]): raise ValueError("output mismatch")
    expected_outputs = [{"path": output["target_path"], "artifact_name": output["artifact_name"]} for output in contract["outputs"]]
    for output, expected in zip(data["outputs"], expected_outputs):
        if not isinstance(output, dict) or set(output) != {"path", "artifact_name", "sha256"} or {"path": output["path"], "artifact_name": output["artifact_name"]} != expected:
            raise ValueError("output mismatch")
        _require_file(root, tracked, output["path"], output["sha256"], "output")
    for input_item in data["inputs"]:
        if not isinstance(input_item, dict) or set(input_item) != {"path", "artifact_name", "sha256", "producer_run_id"}:
            raise ValueError("invalid manifest input")
        _require_file(root, tracked, input_item["path"], input_item["sha256"], "input")
    _validate_verification(data["verification"], data["status"])
    return data
