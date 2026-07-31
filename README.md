# Hermes Enterprise

## v1.4.0 forward-only artifacts
Future pipeline runs first create an immutable, Git-tracked Task Contract in `artifacts/runs/`. It contains exact path/SHA inputs and create-new outputs. Role artifacts live under their fixed agent slug and close with a Git-tracked manifest. Inputs are never selected by `latest`, glob, mtime, traversal, or filename guessing.

Root `artifacts/*.md` files remain local legacy design handoff material. They are not moved, migrated, or a v1.4 runtime interface. Until the first valid tracked future run exists, health deliberately returns nonzero `BOOTSTRAP_PENDING`.
