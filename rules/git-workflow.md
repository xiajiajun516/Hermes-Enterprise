# Git Workflow & Commit Guidelines

## Branching Model
- `main`: Production-ready stability branch. All PRs target `main`.
- `feat/*`: Feature development branches.
- `fix/*`: Bug fix branches.

## Commit Message Format
Follow Conventional Commits: `<type>(<scope>): <short description>`

### Allowed Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `rules`: Updates to core enterprise rules
- `agent`: Updates to subagent prompt configurations
- `chore`: Maintenance tasks
