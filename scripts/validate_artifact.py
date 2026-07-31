#!/usr/bin/env python3
"""Validate one exact forward artifact; never discover legacy files."""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from artifact_io import sha256_file
from artifact_naming import validate_relative_path
from manifest_lineage import validate_manifest
from task_contract import authorized_input, parse_and_validate_contract, validate_template_files


def _tracked(root, path):
    args = ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", path]
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    return result.returncode == 0


def main(path, root=None):
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[1]
    rel = Path(path).as_posix()
    if not validate_relative_path(rel):
        print("BLOCKED: unsupported or legacy path")
        return 1
    try:
        if rel.endswith("__contract.md"):
            if not _tracked(root, rel):
                raise ValueError("BLOCKED: contract untracked")
            contract = parse_and_validate_contract(root / rel)
            validate_template_files(contract, root)
        elif rel.endswith("__manifest.json"):
            validate_manifest(rel, root)
        else:
            digest = sha256_file(root / rel)
            print("SHA256", digest)
        print("PASS", rel)
        return 0
    except (OSError, ValueError) as error:
        print("BLOCKED:", error)
        return 1


def authorize(contract_path, input_path, root=None):
    """--authorize mode: exit 0 only when the input is declared in the contract,
    git-tracked, and its recomputed SHA-256 matches the contract."""
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[1]
    rel = Path(contract_path).as_posix()
    if not validate_relative_path(rel) or not rel.endswith("__contract.md"):
        print("BLOCKED: unsupported or legacy contract path")
        return 1
    try:
        if not _tracked(root, rel):
            raise ValueError("BLOCKED: contract untracked")
        contract = parse_and_validate_contract(root / rel)
        result = authorized_input(contract, root, input_path)
        if not result["authorized"]:
            print(result["reason"] or "BLOCKED: unauthorized input")
            return 1
        print("AUTHORIZED", input_path)
        return 0
    except (OSError, ValueError) as error:
        print("BLOCKED:", error)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--authorize", nargs=2, metavar=("CONTRACT", "INPUT"), help="authorize an input against a tracked contract")
    parser.add_argument("path", nargs="?")
    arguments = parser.parse_args()
    if arguments.authorize:
        contract, input_path = arguments.authorize
        sys.exit(authorize(contract, input_path, arguments.root))
    if arguments.path is None:
        parser.error("a path argument is required unless --authorize is used")
    sys.exit(main(arguments.path, arguments.root))
