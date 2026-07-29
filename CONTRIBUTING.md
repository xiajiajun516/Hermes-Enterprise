# Contributing Guidelines

Thank you for considering contributing to the **Hermes Enterprise Profile**!

## Code & Artifact Standards
1. **Modular Agent Prompts**: Any updates to files in `agents/` must strictly define boundaries and prohiibitions.
2. **Standard Alignment**: Ensure all new rules added under `rules/` are clear, actionable, and non-conflicting.
3. **Artifact Compliance**: Verify artifacts format against `scripts/validate_artifact.py`.

## Submitting Pull Requests
1. Fork the repository and create your branch from `main`.
2. Ensure `python scripts/validate_kanban.py` passes without errors.
3. Open a Pull Request detailing your changes and reasoning.
