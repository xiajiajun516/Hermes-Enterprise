# Changelog

## 1.7.0
- **Merge Product & Research (2a) + Architect (2b) into a single Design Agent**
  (`se-team-design`, stage `2a`, slug `design`): one role now produces
  `research`, `spec-draft`, `spec`, `architecture`, and `implementation-plan`
  under `artifacts/design/`. Rationale: spec→architecture is a strongly
  sequential design phase sharing one compliance audit point; merging removes
  one dispatch round-trip and artifact-handoff loss. The Workflow Manager
  stays a pure controller — no execution is folded into it.
- Scripts: `ALLOWED_SLUGS` drops `product-research`/`architect`, adds `design`
  with the full artifact set; `STAGE_SLUGS["2a"] = "design"`. Stage `2b` is
  deprecated and kept in the map only so any new 2b contract is rejected at
  the ALLOWED_SLUGS gate; historical manifests are forward-only and untouched.
- Skills: `skills/se-team-design/SKILL.md` replaces the two former skills;
  all 5 output templates now declare `agent_slug: design`.
- Docs: README/README.zh-CN role table (02 Design Agent, renumbered 03–06),
  dispatch example, and directory tree updated.
- Tests: fixtures and 7 test modules migrated to the merged slug/stage;
  full suite green (72 tests, 60 subtests).

## 1.6.3
- QA & Release skill gains an **optional** OCR mechanical-review step: if the
  `ocr` CLI (alibaba/open-code-review) is installed, run `ocr review --audience
  agent` (OCR-managed LLM) or `ocr delegate preview` + `ocr delegate rule`
  (delegation mode, no OCR LLM needed) as a first-pass advisory signal before
  the manual review. High/Medium findings are input signals only — Contract
  verification and SHA checks always take precedence; raw JSON may be archived
  under `artifacts/qa-release/` as an immutable artifact. Protocol, scripts,
  and templates unchanged.

## 1.6.2
- Subagent handoff protocol: every Contract now instructs the agent to maintain
  `artifacts/handoffs/<run-id>__handoff.md` (gitignored scratch, fields:
  run_id, stage, done, remaining, next_steps with exact commands) from the
  start and refresh it before every deliverable write and verification run.
  When the agent estimates ~10 tool calls remain it must stop and write the
  handoff immediately — a run whose budget expires mid-task leaves a resume
  point for the retry subagent instead of dying silently.
- Retry & Recovery: a retry subagent first reads the failed run's handoff.
- `close_run` cleanliness gate tolerates `artifacts/handoffs/` scratch files.

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
