---
name: se-team-rule-manager
description: "Governance role for Contract-only forward artifacts."
category: software-development
---
# Rule Manager
Consume only authorized exact inputs with SHA and Git tracking. Close a create-new immutable `artifacts/rule-manager/...__governance-report.md` recording input SHA, governance actions, unchanged items, verification and risks. No legacy, latest, glob, mtime, overwrite or migration.
Output template: `templates/governance-report-template.md`.

Rule changes: write them back to the repo at `skills/se-team-rules/SKILL.md` as a `rules:` commit. The installed copy of se-team-rules intentionally diverges (out-of-scope Floratech rules, see U-23): after a rule change re-run `python scripts/sync_skills.py` and manually reconcile the installed copy.
