import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
from validate_kanban import validate_kanban


def valid_content():
    return "\n".join(f"- **{state}**: []" for state in (
        "Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked",
    ))


class ValidateKanbanTests(unittest.TestCase):
    def run_validator(self, path):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = validate_kanban(path)
        return result, output.getvalue()

    def test_missing_file_returns_false(self):
        with tempfile.TemporaryDirectory() as directory:
            result, text = self.run_validator(Path(directory) / "nope.md")
        self.assertFalse(result)
        self.assertIn("does not exist", text)
        self.assertNotRegex(text, r"[\u4e00-\u9fff]")

    def test_valid_bullet_board_passes_without_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kanban.md"
            path.write_text(valid_content(), encoding="utf-8")
            result, text = self.run_validator(path)
        self.assertTrue(result)
        self.assertNotIn("WARNING", text)
        self.assertNotRegex(text, r"[\u4e00-\u9fff]")

    def test_missing_status_section_returns_false_with_english_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kanban.md"
            path.write_text(valid_content().replace("- **Blocked**: []", ""), encoding="utf-8")
            result, text = self.run_validator(path)
        self.assertFalse(result)
        self.assertIn("Blocked", text)
        self.assertNotRegex(text, r"[\u4e00-\u9fff]")

    def test_table_layout_also_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kanban.md"
            content = valid_content() + "\n| Backlog | Planning | Implementation | In Review | Done | Blocked |\n"
            path.write_text(content, encoding="utf-8")
            result, text = self.run_validator(path)
        self.assertTrue(result)
        self.assertNotIn("WARNING", text)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            good = Path(directory) / "good.md"
            good.write_text(valid_content(), encoding="utf-8")
            missing = Path(directory) / "missing.md"
            command = [sys.executable, str(PROJECT / "scripts/validate_kanban.py")]
            self.assertEqual(subprocess.run(command + [str(good)], text=True, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command + [str(missing)], text=True, capture_output=True).returncode, 1)


if __name__ == "__main__":
    unittest.main()
