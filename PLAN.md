# Plan — v1.5.0

The v1.5 release makes the pipeline actually runnable end to end. CI is trustworthy in
bootstrap and post-bootstrap states; the contract spec is enum-enforced; templates are
complete, unified on one lineage-bearing skeleton and wired into the agent skills.
`scripts/close_run.py` ends hand-written manifest JSON (recomputed hashes, pre-commit
validation, exclusive writes); `scripts/validate_artifact.py --authorize` makes input
authorization executable; `scripts/sync_skills.py` keeps repo and installed skills in sync.
The kanban board is a deterministic projection of the tracked lineage, auto-synced by CI.
A real post-bootstrap run must still create and track its own Contract, outputs, and
manifest before health can pass. No legacy artifact handling, compatibility layer,
migration, or Git move is planned.
