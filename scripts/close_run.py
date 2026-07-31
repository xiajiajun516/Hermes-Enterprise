#!/usr/bin/env python3
"""Create forward-only Contracts and run Manifests with validate-before-write.

Subcommands:
  contract --input <path>          validate a filled contract and write it
                                   create-new to artifacts/runs/<run-id>__contract.md
  manifest --contract <path>       recompute all real SHA-256 values from the actual
      --status <completed|blocked|failed>  files, render the manifest from the exact
      [--verification <json>]      MANIFEST_FIELDS schema, validate it in pre-commit
      [--closed-at <iso-utc>]      mode (require_tracked=False), then write it
                                   create-new to artifacts/runs/<run-id>__manifest.json

Never trusts caller-supplied hashes: every input/output hash is recomputed from the
tracked file on disk, and the contract's declared input hashes are enforced first.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from artifact_io import create_new_utf8, sha256_file
from artifact_naming import validate_relative_path
from manifest_lineage import validate_manifest_data
from task_contract import parse_and_validate_contract, validate_template_files


def _tracked(root, path):
    args = ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", path]
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    return result.returncode == 0


def _blocked(message):
    print("BLOCKED:", message)
    return 1


def create_contract(input_path, root):
    root = Path(root).resolve()
    try:
        contract = parse_and_validate_contract(Path(input_path))
        validate_template_files(contract, root)
    except (OSError, ValueError) as error:
        return _blocked(error)
    run_id = contract["run_id"]
    rel = f"artifacts/runs/{run_id}__contract.md"
    target = root / rel
    if target.exists():
        return _blocked(f"contract already exists: {rel}")
    try:
        create_new_utf8(target, Path(input_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return _blocked(error)
    print("CREATED", rel)
    return 0


def close_manifest(contract_path, status, verification, closed_at, root):
    root = Path(root).resolve()
    rel = Path(contract_path).as_posix()
    if not validate_relative_path(rel) or not rel.endswith("__contract.md"):
        return _blocked("unsupported or legacy contract path")
    if status not in {"completed", "blocked", "failed"}:
        return _blocked(f"invalid status: {status}")
    try:
        verification_records = json.loads(verification)
    except ValueError as error:
        return _blocked(f"invalid --verification JSON: {error}")
    if not isinstance(verification_records, list):
        return _blocked("invalid --verification JSON: expected a list")
    try:
        if not _tracked(root, rel):
            raise ValueError("contract untracked (commit the contract before closing the run)")
        contract = parse_and_validate_contract(root / rel)
        validate_template_files(contract, root)
        run_id = contract["run_id"]
        manifest_rel = f"artifacts/runs/{run_id}__manifest.json"
        target = root / manifest_rel
        if target.exists():
            raise ValueError(f"manifest already exists: {manifest_rel}")
        contract_file = root / rel
        # Recompute real hashes; never trust caller-supplied values.
        for item in contract["inputs"]:
            path = item["path"]
            if not _tracked(root, path):
                raise ValueError(f"BLOCKED: input untracked: {path}")
            actual = sha256_file(root / path)
            if actual != item["sha256"]:
                raise ValueError(f"BLOCKED: input hash mismatch (tampered): {path}")
        outputs = []
        for output in contract["outputs"]:
            path = output["target_path"]
            if not _tracked(root, path):
                if status in {"blocked", "failed"}:
                    continue  # aborted run: outputs may be absent
                raise ValueError(f"BLOCKED: output untracked: {path}")
            if not (root / path).is_file():
                if status in {"blocked", "failed"}:
                    continue
                raise ValueError(f"BLOCKED: output missing: {path}")
            outputs.append({"path": path, "artifact_name": output["artifact_name"], "sha256": sha256_file(root / path)})
        payload = {
            "manifest_version": "1.0",
            "run_id": run_id,
            "contract_path": rel,
            "contract_sha256": sha256_file(contract_file),
            "parent_run_id": contract["parent_run_id"],
            "status": status,
            "inputs": contract["inputs"],
            "outputs": outputs,
            "verification": verification_records,
            "created_at_utc": contract["created_at_utc"],
            "closed_at_utc": closed_at,
        }
        # Pre-commit validation: skip only the git-tracking gate on the manifest itself.
        validate_manifest_data(payload, manifest_rel, root, require_tracked=False)
        # Cleanliness gate: the working tree may differ from HEAD only by the
        # manifest being created. Any other change is an undeclared mutation
        # (e.g. tampered templates, scripts, skills) and blocks the close.
        porcelain = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"], text=True, capture_output=True, check=False
        )
        unexpected = []
        for line in porcelain.stdout.splitlines():
            rel = line[3:].strip()
            if rel.startswith('"') and rel.endswith('"'):
                rel = rel[1:-1]
            if rel != manifest_rel:
                unexpected.append(line)
        if unexpected:
            raise ValueError("BLOCKED: undeclared working-tree changes: " + "; ".join(unexpected))
        create_new_utf8(target, json.dumps(payload, indent=2) + "\n")
    except (OSError, ValueError) as error:
        return _blocked(error)
    print("CLOSED", manifest_rel)
    return 0


def _now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: repo containing this script)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    contract_parser = subparsers.add_parser("contract", help="create a Contract (validate-before-write)")
    contract_parser.add_argument("--input", required=True, help="path to the filled contract text")

    manifest_parser = subparsers.add_parser("manifest", help="close a run: create its manifest")
    manifest_parser.add_argument("--contract", required=True, help="tracked contract path, e.g. artifacts/runs/<run-id>__contract.md")
    manifest_parser.add_argument("--status", required=True, choices=["completed", "blocked", "failed"])
    manifest_parser.add_argument("--verification", required=True, help="JSON list of verification records")
    manifest_parser.add_argument("--closed-at", default=None, help="ISO-8601 UTC close timestamp (default: now)")

    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root is not None else Path(__file__).resolve().parents[1]
    if args.command == "contract":
        return create_contract(args.input, root)
    if args.command == "manifest":
        closed_at = args.closed_at or _now_utc()
        return close_manifest(args.contract, args.status, args.verification, closed_at, root)
    return 2


if __name__ == "__main__":
    sys.exit(main())
