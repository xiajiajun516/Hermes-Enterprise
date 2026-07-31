#!/usr/bin/env python3
"""Render kanban/kanban.md as a deterministic projection of the pipeline lineage.

Reads only git-tracked manifests (artifacts/runs/*__manifest.json) and their
referenced contracts, plus tracked contracts without manifests (runs in flight).
Modes:
  generate (default)  write kanban/kanban.md
  --check             render in memory, compare with disk; exit 0 if fresh,
                      1 + actionable message if drifted (never writes)

Column mapping (see docs/KANBAN_SYNC_PLAN.md):
  Implementation  contract tracked, no manifest yet (run in flight)
  In Review       manifest completed, agent_slug != qa-release
  Done            manifest completed, agent_slug == qa-release
  Blocked         manifest status in {blocked, failed}
  Backlog/Planning  empty placeholders (no source in derived mode)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from task_contract import parse_and_validate_contract  # noqa: E402

HEADER = "# Project Kanban\n\n## Status Overview\n\n"
COLUMNS = ["Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"]
TERMINAL_SLUG = "qa-release"


def _tracked_paths(root, pattern):
    result = subprocess.run(["git", "-C", str(root), "ls-files", "--", pattern], text=True, capture_output=True, check=False)
    return [path for path in result.stdout.splitlines() if path]


def collect_lineage(root):
    """Return {run_id: {"status": str, "agent_slug": str}} from tracked lineage."""
    root = Path(root).resolve()
    items = {}
    for contract_rel in _tracked_paths(root, "artifacts/runs/*__contract.md"):
        try:
            contract = parse_and_validate_contract(root / contract_rel)
        except (OSError, ValueError) as error:
            print(f"WARN: skipped corrupt contract {contract_rel}: {error}", file=sys.stderr)
            continue
        items[contract["run_id"]] = {"status": "in_flight", "agent_slug": contract["agent_slug"]}
    for manifest_rel in _tracked_paths(root, "artifacts/runs/*__manifest.json"):
        try:
            data = json.loads((root / manifest_rel).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"WARN: skipped corrupt manifest {manifest_rel}: {error}", file=sys.stderr)
            continue
        run_id = data.get("run_id")
        if run_id not in items:
            continue
        items[run_id] = {"status": data.get("status", "in_flight"), "agent_slug": items[run_id]["agent_slug"]}
    return items


def _column_for(item):
    status = item["status"]
    if status in {"blocked", "failed"}:
        return "Blocked"
    if status == "in_flight":
        return "Implementation"
    if status == "completed":
        return "Done" if item["agent_slug"] == TERMINAL_SLUG else "In Review"
    return "Implementation"


def render_board(items):
    lines = [HEADER]
    for column in COLUMNS:
        cards = sorted(
            (run_id for run_id, item in items.items() if _column_for(item) == column),
            reverse=True,
        )
        rendered = ", ".join(f"'{run_id} ({items[run_id]['agent_slug']})'" for run_id in cards)
        lines.append(f"- **{column}**: [{rendered}]")
    return "\n".join(lines) + "\n"


def generate(root):
    return render_board(collect_lineage(root))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render the derived kanban board from tracked lineage.")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--check", action="store_true", help="diff in memory; exit 1 on drift, never write")
    parser.add_argument("--output", type=Path, default=None, help="target board path (default: <root>/kanban/kanban.md)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root is not None else Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve() if args.output is not None else root / "kanban/kanban.md"
    try:
        rendered = generate(root)
    except (OSError, ValueError) as error:
        print("BLOCKED:", error)
        return 1

    if args.check:
        if output.is_file() and output.read_text(encoding="utf-8") == rendered:
            print("kanban --check OK: board is fresh")
            return 0
        print("kanban --check FAILED: board drifted from lineage")
        print("run `python scripts/update_kanban.py` and commit the result")
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print("kanban updated:", output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
