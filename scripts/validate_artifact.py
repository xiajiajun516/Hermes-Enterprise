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
from task_contract import parse_and_validate_contract


def _tracked(root, path):
    return subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", path], text=True, capture_output=True, check=False).returncode == 0


def main(path, root=None):
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[1]
    rel = Path(path).as_posix()
    if not validate_relative_path(rel):
        print("BLOCKED: unsupported or legacy path")
        return 1
    try:
        if rel.endswith("__contract.md"):
            if not _tracked(root, rel): raise ValueError("BLOCKED: contract untracked")
            parse_and_validate_contract(root / rel)
        elif rel.endswith("__manifest.json"):
            validate_manifest(rel, root)
        else:
            sha256_file(root / rel)
        print("PASS", rel)
        return 0
    except (OSError, ValueError) as error:
        print("BLOCKED:", error)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("path")
    arguments = parser.parse_args()
    sys.exit(main(arguments.path, arguments.root))
