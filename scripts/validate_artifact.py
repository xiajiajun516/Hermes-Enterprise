#!/usr/bin/env python3
"""
Artifact Validator Script for Hermes Enterprise Profile
Checks if generated artifact markdown files contain mandatory section headers.
"""

import sys
import os

MANDATORY_HEADERS = {
    "spec.md": ["Scope", "User Stories", "Acceptance Criteria"],
    "architecture.md": ["Directory Tree", "Module", "API"],
    "compliance-report.md": ["Violations", "STATUS:"]
}

def validate_artifact(file_path):
    file_name = os.path.basename(file_path)
    if file_name not in MANDATORY_HEADERS:
        print(f"ℹ️ Skipping validation for unknown artifact shape: {file_name}")
        return True

    if not os.path.exists(file_path):
        print(f"❌ Error: Artifact file '{file_path}' not found.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    missing = [header for header in MANDATORY_HEADERS[file_name] if header not in content]

    if missing:
        print(f"❌ Validation failed for {file_name}. Missing required headers: {missing}")
        return False

    print(f"✅ Artifact validation passed for {file_name}!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_artifact.py <path_to_artifact>")
        sys.exit(1)
    
    success = validate_artifact(sys.argv[1])
    sys.exit(0 if success else 1)
