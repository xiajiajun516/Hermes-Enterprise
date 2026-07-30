#!/usr/bin/env python3
"""
Kanban Validator Script for Hermes Enterprise Profile
Validates whether kanban/kanban.md conforms to allowed states and formats.
"""

import sys
import os

VALID_STATES = ["Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"]
# Kanban column names used for table-format detection.
KANBAN_COLUMNS = ["Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"]


def check_kanban_table(content):
    """Detect a standard Markdown Kanban table and emit warnings without failing validation."""
    lines = content.split("\n")
    table_found = False
    separator_found = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # Check whether the header contains Kanban column names.
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            matches = sum(1 for col in KANBAN_COLUMNS if col in cells)
            if matches >= 3:
                # A header was found; check whether the next line is a separator.
                table_found = True
                if i + 1 < len(lines):
                    sep_line = lines[i + 1].strip()
                    if "|" in sep_line and all(c in "| -:" for c in sep_line):
                        separator_found = True
                break

    if not table_found:
        print("⚠️  WARNING: Standard Kanban Markdown table not found (expected columns: Backlog, Planning, Implementation, In Review, Done, Blocked)")
        print("    Add a Markdown table to improve Kanban visualization.")
    elif not separator_found:
        print("⚠️  WARNING: Kanban header found but separator row (| --- | --- |) is missing; rendering may be incorrect.")
    else:
        print("✅  Kanban table format check passed.")

    # Always return True: this is a backward-compatible warning only.
    return True

def validate_kanban(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' does not exist.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"🔍 Validating {file_path}...")
    errors = []

    # Table-format detection is a warning only and does not affect the exit code.
    check_kanban_table(content)

    for state in VALID_STATES:
        if f"**{state}**" not in content and f"- {state}:" not in content:
            errors.append(f"Missing expected status section: '{state}'")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False

    print("✅ Kanban validation passed successfully!")
    return True

if __name__ == "__main__":
    kanban_path = sys.argv[1] if len(sys.argv) > 1 else "kanban/kanban.md"
    success = validate_kanban(kanban_path)
    sys.exit(0 if success else 1)
