# Contributing Guidelines

Thank you for considering contributing to the **Hermes Enterprise**!

## Code & Artifact Standards
1. **Modular Agent Prompts**: Any updates to files in `skills/` must strictly define boundaries and prohibitions.
2. **Standard Alignment**: Ensure all new rules added under `skills/` are clear, actionable, and non-conflicting.
3. **Artifact Compliance**: Verify artifacts format against `scripts/validate_artifact.py`.

## Skill Sync (repo ↔ installed skills)
The repository is the source of truth for the pipeline skills. After changing `SKILL.md` or
`skills/`, run `python scripts/sync_skills.py` to mirror the repo into the local Hermes skills
directory. Use `python scripts/sync_skills.py --check` to detect drift. Known-divergent skills
(`se-team-rules`) are on an ignore-list and are neither copied nor checked.

## Derived Kanban
`kanban/kanban.md` is a deterministic projection of the pipeline lineage and is never hand-edited.
After committing runs, run `python scripts/update_kanban.py` and commit the result (fork
contributors must do this locally; CI also enforces it via the PR drift check).

## Submitting Pull Requests
1. Fork the repository and create your branch from `main`.
2. Ensure `python scripts/update_kanban.py --check` passes (regenerate the board with `python scripts/update_kanban.py` if it drifts).
3. Open a Pull Request detailing your changes and reasoning.
4. **Merge discipline**: the full test suite must pass on the final target tree (CI on the PR/push target). A green run on an earlier tree does not authorize a merge.
5. **Blocked runs**: a run that fails (status `blocked`/`failed`, possibly with zero outputs) is closed as-is and appears in the kanban Blocked column — a review queue. Fix, then retry with `attempt` N+1 and `parent_run_id` linking the failed run. Never rewrite a closed manifest.
