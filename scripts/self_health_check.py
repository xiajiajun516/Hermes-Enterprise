#!/usr/bin/env python3
"""Health checks only Git-tracked future manifests."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from manifest_lineage import tracked_manifest_paths, validate_manifest, validate_parent_graph


def main(root=None):
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[1]
    manifests = tracked_manifest_paths(root)
    if not manifests:
        print("BOOTSTRAP_PENDING: no Git-tracked future manifests")
        return 1
    try:
        items = [validate_manifest(path, root, manifests) for path in manifests]
        validate_parent_graph({item["run_id"]: item["parent_run_id"] for item in items})
    except (OSError, ValueError) as error:
        print("FAIL:", error)
        return 1
    print("PASS: Git-tracked future manifest lineage valid")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    sys.exit(main(parser.parse_args().root))
