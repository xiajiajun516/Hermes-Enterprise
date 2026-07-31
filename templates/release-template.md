# Release — <run-id>

## Run Identity
- **run_id**: <run-id>
- **agent_slug**: qa-release
- **stage**: <2e>
- **contract**: artifacts/runs/<run-id>__contract.md
- **created_at_utc**: <ISO-8601>

## Source Artifacts
- **inputs**: <paths matching contract inputs[]>

## Version
- **Version**: <semver>
- **Release Date**: <ISO date>
- **Author**: <agent slug>

## What's New
- <feature>: <what it does and why it matters>

## Bug Fixes
- <fix>: <issue it resolves>

## Breaking Changes
- [ ] No breaking changes
- [ ] Yes (list below): <each breaking change with migration note>

## Deployment Instructions
1. <exact command>
2. <exact command>

## Rollback Plan
- **Rollback command**: <exact concrete command — not a description>
- **Rollback verification**: <how to confirm the rollback succeeded>

---
**Release Status**: `DEPLOYED` / `PENDING` / `ROLLED_BACK`
