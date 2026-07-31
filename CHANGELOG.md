# Changelog

## 1.6.1
- Failure channel: `blocked`/`failed` runs can close with **zero outputs**
  (aborted runs no longer deadlock in in_flight); `completed` runs still require
  every declared output. Manifest validation accepts partial outputs for
  non-completed status only (undeclared outputs still rejected).
- Cleanliness gate: closing a run now blocks on any undeclared working-tree
  change (only the manifest itself may be untracked) — tampered templates,
  scripts or skills surface as `BLOCKED: undeclared working-tree changes`.
- Contract body must enumerate the same input/output paths as the frontmatter;
  placeholder bodies (`inputs: exact`) are rejected — the body is the
  subagent's behavioral contract and can no longer drift from machine truth.
- Rule Manager skill documents the rule-change path (repo `se-team-rules` +
  manual sync); retry & recovery flow (attempt N+1 with `parent_run_id`,
  Blocked column as review queue) documented in SKILL.md and CONTRIBUTING.
- `self_health_check` bootstrap state prints next-step guidance.

## 1.6.0
- Trust-chain hardening (audit round, 2026-07-31):
  - Input producer lineage: every `inputs[].producer_run_id` must exist as a tracked
    manifest whose `outputs` declare the consumed path + artifact name — fabricated
    ancestors are rejected.
  - Verification records must be self-consistent: `result: PASS` iff
    `exit_code == expected_exit_code`.
  - Time integrity: `closed_at_utc` must not precede `created_at_utc`; manifest
    `created_at_utc` must equal the contract's.
- `update_kanban.py` warns on corrupt lineage records instead of silently dropping them.
- `self_health_check.py` distinguishes FAIL (exit 2) from BOOTSTRAP_PENDING (exit 1).
- Removed `validate_kanban.py`: board drift is enforced by `update_kanban.py --check`
  (PR job); the push job regenerates the board (sync job now rebases before pushing).
- Contract frontmatter accepts YAML markers inside quoted values (e.g. `"QA & Release"`);
  ambiguity errors now carry line numbers.
- README (EN + zh-CN): install paths aligned with `sync_skills.py` defaults; layout,
  agent matrix, and dispatch example updated to v1.5+ artifact model.
- `SKILL.md`: `--authorize` step added to dispatch prerequisites.

## 1.5.0
- **CI trustworthy in every state (U-01)**: bootstrap gate now derives mode from
  `git ls-files` — asserts `BOOTSTRAP_PENDING` (exit 1) only while no tracked manifests
  exist, and requires `PASS` (exit 0) post-bootstrap; a corrupted manifest goes red.
- **Contract spec enforced (U-02)**: `tier` (P0/P1/P2), `stage` (2a–2f), `language` (en-US)
  enums and the stage↔agent_slug pairing are validated; `tier: "P9"`, `stage: "2z"`,
  `language: "zh-CN"` and mismatched slug pairs are rejected.
- **Templates complete + validated (U-03)**: added `research`, `spec-draft`,
  `implementation-report`, `governance-report` templates; every `outputs[].template` must
  name the matching `<artifact-name>-template.md` and the file must exist.
- **Run creation tooling (U-17)**: new `scripts/close_run.py` creates contracts and
  manifests with recomputed SHA-256, pre-commit validation mode (`require_tracked=False`)
  and exclusive create-new writes; tampered inputs, missing outputs and wrong statuses are
  rejected before anything is written.
- **Executable input authorization (U-22)**: `scripts/validate_artifact.py --authorize
  <contract> <input>` exits 0 only for tracked, hash-matching, contract-declared inputs.
- **Skill sync mechanism (U-23)**: new `scripts/sync_skills.py` mirrors repo skills to the
  Hermes skills directory with `--check` drift detection; `se-team-rules` on the
  ignore-list (Floratech drift accepted by user directive 2026-07-31).
- **Unified template skeleton (U-19/U-20)**: all 11 content templates share
  `Run Identity` + `Source Artifacts` lineage headers with per-section guardrails; every
  se-team agent skill now references its output templates explicitly.
- **Portable contract template (U-21)**: `<repo-root>` placeholder replaces the hardcoded
  machine path in `templates/task-contract-template.md` and `SKILL.md`.
- **Test hardening (U-04…U-16)**: CWD-independent imports, shared `tests/fixtures.py`,
  4-space style with a `ruff` gate, `coverage` gate (≥80%), sequence-retry, positive-path,
  CLI-branch, FAIL-path, kanban-error-path, temporal parent-ordering and full 3-stage
  end-to-end rehearsal tests (64 tests).
- **Derived live kanban (Phase 5)**: new `scripts/update_kanban.py` renders the board as a
  deterministic projection of the tracked lineage (bullet format, `--check` mode); CI
  auto-sync job on push (`[skip ci]`, `concurrency` group) and drift-check job on PRs.
- **Kanban warning removed (U-11)**: the perpetual "table not found" warning is gone —
  the bullet layout is the locked generator format; six-section enforcement unchanged.
- **Contributing guidelines (U-18/U-23/Phase 5)**: merge-discipline rule, skill-sync
  workflow and derived-kanban workflow documented.
- Historical kanban entries (v1.1–v1.3) replaced by the lineage-derived board on first sync.

## 1.4.0
- Added forward-only structured eight-section Task Contracts and exact SHA/Git input authorization.
- Added immutable agent-owned timestamp artifacts and Git-tracked run manifest lineage validation.
- Kept root legacy artifacts out of the runtime interface; no migration or compatibility layer.
- Defined `BOOTSTRAP_PENDING` until a valid tracked future run is present.
