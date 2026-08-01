# Contributing Guidelines

Thank you for considering contributing to the **Hermes Enterprise**!

## Skill Standards

1. **Modular Agent Prompts**: Any updates to files in `skills/` must keep role boundaries and prohibitions explicit.
2. **Standard Alignment**: New rules added under `skills/` must be clear, actionable, and non-conflicting.
3. **Template Alignment**: Role skills must reference exactly the templates they produce; keep the 3-template set (`spec`, `implementation-report`, `review`) in sync with the role skills.

## Skill Sync (repo ↔ installed skills)

The repository is the source of truth. After changing `SKILL.md` or `skills/`, run:

```bash
python scripts/sync_skills.py          # mirror repo -> Hermes skills dir
python scripts/sync_skills.py --check  # detect drift (exit 1 on drift)
```

Known-divergent skills (`se-team-rules`) are on an ignore-list and are neither copied nor checked.

## Testing

Run the kept test suite before merging:

```bash
python -m pytest tests/ -q
```

## Submitting Pull Requests

1. Fork the repository and create your branch from `main`.
2. Run `python scripts/sync_skills.py --check` and the test suite locally.
3. Open a Pull Request detailing your changes and reasoning.
4. **Merge discipline**: the kept test suite must pass on the final target tree (CI on the PR/push target). A green run on an earlier tree does not authorize a merge.

## Versioning

- Breaking architecture changes: bump the minor version (e.g. `1.7.0` → `2.0.0`) in `SKILL.md`, `distribution.yaml`, and `VERSION`, and add a `CHANGELOG.md` entry.
- Small fixes/features: bump the patch version.
