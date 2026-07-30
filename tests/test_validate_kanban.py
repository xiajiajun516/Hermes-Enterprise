import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "scripts")
from validate_kanban import validate_kanban


class ValidateKanbanTests(unittest.TestCase):
    def test_missing_table_warning_is_english(self):
        content = "\n".join(f"- {state}:" for state in (
            "Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked",
        ))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kanban.md"
            path.write_text(content, encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertTrue(validate_kanban(path))
        text = output.getvalue()
        self.assertIn("WARNING: Standard Kanban Markdown table not found", text)
        self.assertNotRegex(text, r"[\u4e00-\u9fff]")


if __name__ == "__main__":
    unittest.main()
