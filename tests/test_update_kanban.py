import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from fixtures import chain_contract, digest  # noqa: E402
from update_kanban import collect_lineage, main as kanban_main, render_board  # noqa: E402

VERIFICATION = [{"command": "test", "expected_exit_code": 0, "exit_code": 0, "result": "PASS", "evidence_paths": []}]


def add_run(root, run, slug, stage, output_name, parent=None, status="completed"):
    """Write contract + output + manifest for one run, all git-tracked."""
    contract_text = chain_contract(run, slug, stage, output_name, parent=parent)
    contract = root / f"artifacts/runs/{run}__contract.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(contract_text, encoding="utf-8")
    output = root / f"artifacts/{slug}/{run}__{output_name}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("content", encoding="utf-8")
    manifest = root / f"artifacts/runs/{run}__manifest.json"
    payload = {
        "manifest_version": "1.0", "run_id": run,
        "contract_path": f"artifacts/runs/{run}__contract.md",
        "contract_sha256": digest(contract), "parent_run_id": parent, "status": status,
        "inputs": [], "outputs": [
            {"path": f"artifacts/{slug}/{run}__{output_name}.md", "artifact_name": output_name, "sha256": digest(output)}
        ],
        "verification": VERIFICATION, "created_at_utc": "2026-07-31T10:00:00.000Z",
        "closed_at_utc": "2026-07-31T10:05:00.000Z",
    }
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "artifacts"], check=True)
    return contract, manifest


def fresh_repo():
    directory = tempfile.TemporaryDirectory()
    root = Path(directory.name)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return directory, root


class UpdateKanbanTests(unittest.TestCase):
    def test_empty_lineage_renders_six_empty_sections(self):
        directory, root = fresh_repo()
        with directory:
            board = render_board(collect_lineage(root))
            for state in ("Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"):
                self.assertIn(f"- **{state}**: []", board)

    def test_contract_without_manifest_lands_in_implementation(self):
        directory, root = fresh_repo()
        with directory:
            run = "20260731T100000-001"
            contract_text = chain_contract(run, "engineer", "2d", "implementation-report")
            contract = root / f"artifacts/runs/{run}__contract.md"
            contract.parent.mkdir(parents=True, exist_ok=True)
            contract.write_text(contract_text, encoding="utf-8")
            output = root / f"artifacts/engineer/{run}__implementation-report.md"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("content", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "artifacts"], check=True)
            board = render_board(collect_lineage(root))
            self.assertIn("- **Implementation**: ['20260731T100000-001 (engineer)']", board)

    def test_completed_non_terminal_run_lands_in_review(self):
        directory, root = fresh_repo()
        with directory:
            add_run(root, "20260731T100000-001", "design", "2a", "architecture")
            board = render_board(collect_lineage(root))
            self.assertIn("- **In Review**: ['20260731T100000-001 (design)']", board)

    def test_completed_terminal_run_lands_in_done(self):
        directory, root = fresh_repo()
        with directory:
            add_run(root, "20260731T100000-001", "qa-release", "2e", "release")
            board = render_board(collect_lineage(root))
            self.assertIn("- **Done**: ['20260731T100000-001 (qa-release)']", board)

    def test_blocked_run_lands_in_blocked(self):
        directory, root = fresh_repo()
        with directory:
            add_run(root, "20260731T100000-001", "engineer", "2d", "implementation-report", status="blocked")
            board = render_board(collect_lineage(root))
            self.assertIn("- **Blocked**: ['20260731T100000-001 (engineer)']", board)

    def test_check_detects_drift_and_generate_restores(self):
        directory, root = fresh_repo()
        with directory:
            add_run(root, "20260731T100000-001", "qa-release", "2e", "release")
            kanban = root / "kanban/kanban.md"
            kanban.parent.mkdir(parents=True, exist_ok=True)
            kanban.write_text(render_board(collect_lineage(root)), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(kanban_main(["--root", str(root), "--check"]), 0)
            kanban.write_text("- **Done**: []", encoding="utf-8")
            drifted = io.StringIO()
            with contextlib.redirect_stdout(drifted):
                self.assertEqual(kanban_main(["--root", str(root), "--check"]), 1)
            self.assertIn("drifted", drifted.getvalue())
            generated = io.StringIO()
            with contextlib.redirect_stdout(generated):
                self.assertEqual(kanban_main(["--root", str(root)]), 0)
            self.assertIn("20260731T100000-001 (qa-release)", kanban.read_text(encoding="utf-8"))

    def test_corrupt_manifest_warns_and_is_skipped(self):
        directory, root = fresh_repo()
        with directory:
            add_run(root, "20260731T100000-001", "design", "2a", "architecture")
            bad = root / "artifacts/runs/20260731T100000-001__manifest.json"
            bad.write_text("{ broken", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "artifacts"], check=True)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                board = render_board(collect_lineage(root))
            self.assertIn("WARN: skipped corrupt manifest", stderr.getvalue())
            self.assertIn("- **Implementation**", board)

    def test_cards_sorted_descending_by_run_id(self):
        directory, root = fresh_repo()
        with directory:
            add_run(root, "20260731T100000-001", "qa-release", "2e", "release")
            add_run(root, "20260731T120000-003", "qa-release", "2e", "release")
            board = render_board(collect_lineage(root))
            self.assertIn("- **Done**: ['20260731T120000-003 (qa-release)', '20260731T100000-001 (qa-release)']", board)


if __name__ == "__main__":
    unittest.main()
