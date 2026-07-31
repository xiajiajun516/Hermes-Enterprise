# Hermes Enterprise Profile Push

Forward-only, contract-driven orchestration profile for an AI software engineering team
(the `software-engineering-team` skill, v1.4). Every pipeline run is recorded as immutable,
Git-tracked artifacts — never guessed, never overwritten.

## How a run works

1. **Contract** — before dispatching, the Master creates an immutable Task Contract at
   `artifacts/runs/<run-id>__contract.md` (exclusive write). It pins exact input paths and
   SHA-256 values and declares create-new outputs. Inputs are never selected by `latest`,
   glob, mtime, directory traversal, or filename guessing.
2. **Dispatch** — the contract (exact path + SHA-256) is passed to the subagent; inputs are
   authorized by path, Git tracking, and recomputed hash.
3. **Outputs** — role artifacts are written under their fixed agent slug
   (`artifacts/<slug>/<run-id>__<artifact-name>.md`) with create-new semantics.
4. **Manifest** — the run closes with a Git-tracked manifest
   (`artifacts/runs/<run-id>__manifest.json`) recording status, verification evidence, and
   hashes.
5. **Health gate** — `scripts/self_health_check.py` validates the whole tracked lineage.
   Until the first valid tracked run exists it deliberately returns `BOOTSTRAP_PENDING`
   (non-zero).

Root-level `artifacts/*.md` files are legacy design handoff material — they are not moved,
not migrated, and are not a v1.4 runtime interface.

## Repository layout

| Path | Purpose |
|---|---|
| `SKILL.md` | Master orchestration skill (stages 2a–2f) |
| `skills/` | Subagent skills: product-research, architect, compliance-reviewer, engineer, qa-release, rule-manager, rules |
| `scripts/` | Validation tooling: `validate_artifact.py`, `self_health_check.py`, `validate_kanban.py`, plus naming / lineage / contract modules |
| `templates/` | Artifact templates for each role output |
| `tests/` | unittest suite (fixtures run in isolated temp git repos) |
| `kanban/` | Project kanban |
| `.github/workflows/` | CI: unit tests, health bootstrap gate, kanban validation |

## Validation & tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
python scripts/self_health_check.py            # BOOTSTRAP_PENDING until first tracked run
python scripts/validate_artifact.py <path>     # validate a contract / manifest / artifact
python scripts/validate_kanban.py kanban/kanban.md
```

## CI

`.github/workflows/validate-artifacts.yml` runs on every push and pull request:
unit tests → health bootstrap gate → kanban validation.

## Version

v1.4.0 — see `CHANGELOG.md`.
