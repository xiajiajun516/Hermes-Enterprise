"""Manifest and lineage validation for tracked future runs."""
import json
import re
import subprocess
from pathlib import Path

from artifact_io import sha256_file
from artifact_naming import RUN_RE, validate_relative_path
from task_contract import SHA_RE, parse_and_validate_contract, validate_template_files

MANIFEST_FIELDS = {
    "manifest_version", "run_id", "contract_path", "contract_sha256", "parent_run_id",
    "status", "inputs", "outputs", "verification", "created_at_utc", "closed_at_utc",
}


def _tracked_all(root):
    result = subprocess.run(["git", "-C", str(root), "ls-files"], text=True, capture_output=True, check=False)
    return set(result.stdout.splitlines())


def tracked_manifest_paths(root):
    args = ["git", "-C", str(root), "ls-files", "--", "artifacts/runs/*__manifest.json"]
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    return [path for path in result.stdout.splitlines() if path]


def validate_parent_graph(parents):
    for node in parents:
        seen, current = set(), node
        while current is not None:
            if current in seen:
                raise ValueError("parent cycle")
            seen.add(current)
            parent = parents.get(current)
            if parent is not None and parent not in parents:
                raise ValueError("missing parent")
            if parent is not None and parent >= current:
                raise ValueError("parent must predate child")
            current = parent


def _require_time(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", value):
        raise ValueError("invalid timestamp")


def _require_file(root, tracked, path, expected_sha, kind):
    if not isinstance(path, str) or not validate_relative_path(path) or path not in tracked:
        raise ValueError(f"BLOCKED: {kind} untracked or invalid")
    target = (root / path).resolve()
    valid_sha = isinstance(expected_sha, str) and SHA_RE.fullmatch(expected_sha)
    if root not in target.parents or not target.is_file() or not valid_sha or sha256_file(target) != expected_sha:
        raise ValueError(f"BLOCKED: {kind} hash or existence")


def _validate_verification(records, status):
    if not isinstance(records, list) or not records:
        raise ValueError("missing verification evidence")
    for record in records:
        if not isinstance(record, dict) or set(record) != {"command", "expected_exit_code", "exit_code", "result", "evidence_paths"}:
            raise ValueError("invalid verification schema")
        int_fields = type(record["expected_exit_code"]) is int and type(record["exit_code"]) is int
        if not isinstance(record["command"], str) or not record["command"] or not int_fields:
            raise ValueError("invalid verification fields")
        evidence_ok = isinstance(record["evidence_paths"], list) and all(
            isinstance(path, str) and validate_relative_path(path) for path in record["evidence_paths"]
        )
        if record["result"] not in {"PASS", "FAIL", "BLOCKED"} or not evidence_ok:
            raise ValueError("invalid verification fields")
        consistent = (record["result"] == "PASS") == (record["exit_code"] == record["expected_exit_code"])
        if not consistent:
            raise ValueError("verification result contradicts exit code")
    all_pass = all(record["result"] == "PASS" and record["exit_code"] == record["expected_exit_code"] for record in records)
    if status == "completed" and not all_pass:
        raise ValueError("failed verification")
    if status != "completed" and all_pass:
        raise ValueError("non-completed manifest lacks failure evidence")


def validate_manifest(path, root, tracked_paths=None, require_tracked=True):
    root = Path(root).resolve()
    rel = Path(path).as_posix()
    manifest_path = root / rel
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return validate_manifest_data(data, rel, root, require_tracked=require_tracked)


def validate_manifest_data(data, rel, root, require_tracked=True):
    """Validate rendered manifest data. With require_tracked=False the git-tracking
    gate on the manifest itself is skipped (pre-commit mode for close_run.py);
    contract, inputs and outputs must still be tracked."""
    root = Path(root).resolve()
    if require_tracked:
        tracked_manifests = set(tracked_manifest_paths(root))
        if rel not in tracked_manifests:
            raise ValueError("BLOCKED: manifest untracked")
    if not isinstance(data, dict) or set(data) != MANIFEST_FIELDS or data["manifest_version"] != "1.0":
        raise ValueError("invalid manifest")
    if data["status"] not in {"completed", "blocked", "failed"}:
        raise ValueError("invalid manifest")
    valid_run = isinstance(data["run_id"], str) and RUN_RE.fullmatch(data["run_id"])
    if not valid_run or rel != f"artifacts/runs/{data['run_id']}__manifest.json":
        raise ValueError("manifest run id mismatch")
    _require_time(data["created_at_utc"])
    _require_time(data["closed_at_utc"])
    if data["closed_at_utc"] < data["created_at_utc"]:
        raise ValueError("closed_at precedes created_at")
    if data["parent_run_id"] is not None and (not isinstance(data["parent_run_id"], str) or not RUN_RE.fullmatch(data["parent_run_id"])):
        raise ValueError("invalid parent run id")
    tracked = _tracked_all(root)
    contract_path = data["contract_path"]
    if contract_path != f"artifacts/runs/{data['run_id']}__contract.md":
        raise ValueError("contract run id mismatch")
    _require_file(root, tracked, contract_path, data["contract_sha256"], "contract")
    contract = parse_and_validate_contract(root / contract_path)
    validate_template_files(contract, root)
    mismatch = (
        contract["run_id"] != data["run_id"]
        or contract["parent_run_id"] != data["parent_run_id"]
        or contract["inputs"] != data["inputs"]
        or contract["created_at_utc"] != data["created_at_utc"]
    )
    if mismatch:
        raise ValueError("contract mismatch")
    expected_outputs = [{"path": output["target_path"], "artifact_name": output["artifact_name"]} for output in contract["outputs"]]
    if not isinstance(data["outputs"], list):
        raise ValueError("output mismatch")
    for output in data["outputs"]:
        if not isinstance(output, dict) or set(output) != {"path", "artifact_name", "sha256"}:
            raise ValueError("output mismatch")
        if {"path": output["path"], "artifact_name": output["artifact_name"]} not in expected_outputs:
            raise ValueError("output mismatch")
        _require_file(root, tracked, output["path"], output["sha256"], "output")
    if data["status"] == "completed" and len(data["outputs"]) != len(expected_outputs):
        raise ValueError("output mismatch")
    producer_outputs = {}
    for manifest_rel in tracked_manifest_paths(root):
        try:
            mdata = json.loads((root / manifest_rel).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(mdata, dict) or not isinstance(mdata.get("run_id"), str) or not isinstance(mdata.get("outputs"), list):
            continue
        producer_outputs[mdata["run_id"]] = {
            (output.get("path"), output.get("artifact_name"))
            for output in mdata["outputs"]
            if isinstance(output, dict)
        }
    for input_item in data["inputs"]:
        if not isinstance(input_item, dict) or set(input_item) != {"path", "artifact_name", "sha256", "producer_run_id"}:
            raise ValueError("invalid manifest input")
        _require_file(root, tracked, input_item["path"], input_item["sha256"], "input")
        producer = input_item["producer_run_id"]
        if producer not in producer_outputs or (input_item["path"], input_item["artifact_name"]) not in producer_outputs[producer]:
            raise ValueError(f"BLOCKED: input producer lineage missing: run {producer} does not declare {input_item['path']}")
    _validate_verification(data["verification"], data["status"])
    return data
