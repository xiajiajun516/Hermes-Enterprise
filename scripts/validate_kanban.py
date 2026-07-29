#!/usr/bin/env python3
"""
Kanban Validator Script for Hermes Enterprise Profile
Validates whether kanban/kanban.md conforms to allowed states and formats.
"""

import sys
import os

VALID_STATES = ["Backlog", "Planning", "Implementation", "In Review", "Done", "Blocked"]

def validate_kanban(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' does not exist.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"🔍 Validating {file_path}...")
    errors = []

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
