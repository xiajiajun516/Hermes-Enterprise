# Changelog

## 2.0.9
- **Dated, type-organized deliverables**: stage outputs moved from fixed
  `artifacts/spec.md` / `report.md` / `review.md` to type folders under
  `artifacts/` — `artifacts/spec/<DD-MM-YYYY>-spec.md`,
  `artifacts/report/<DD-MM-YYYY>-report.md`,
  `artifacts/review/<DD-MM-YYYY>-review.md`. The Master computes the run-date
  prefix and hands the exact `output:` path to the subagent; subagents never
  derive their own date or filename. Every run now leaves a dated, non-
  overwriting record per stage.

## 2.0.8
- **One commit per stage (fix)**: the engineer now commits exactly once at
  the end of its run instead of once per coherent unit. QA's diff-scope
  (`git diff --name-only HEAD~1..HEAD`) therefore always covers precisely the
  work under review — previously a multi-commit engineer run silently left
  earlier commits outside the Semgrep/manual review scope.
- **Semgrep wording honest (fix)**: `--config auto` pulls its rule set from
  the Semgrep registry, which drifts over time — findings are no longer
  described as "deterministic / ground truth". QA skill, review template, and
  install-deps.sh now call them pattern-based signals (advisory); a finding
  that would affect a verdict must be confirmed by manual review first, same
  rule as OCR findings.
- **Anti-machinery guardrail**: Hard Prohibitions gains a "prefer convention
  fixes over new machinery" rule — process defects are fixed by changing
  prompts/commit conventions first (git + prompts cover ~95%); new scripts or
  tools only when a convention fix demonstrably cannot work. This release
  itself is a text-only fix: no new scripts, no new files.

## 2.0.7
- **Concrete deliverable paths**: stage outputs are now fixed, git-tracked
  paths — `artifacts/spec.md`, `artifacts/report.md`, `artifacts/review.md` —
  replacing the undefined "output per role table". The `.gitignore`
  `/artifacts/*.md` rule that silently dropped them from git was removed.
  New consistency test `test_output_paths_are_concrete_and_tracked` guards
  the paths and the gitignore.
- **Spec gate**: after design commits `artifacts/spec.md`, the Master reviews
  it before dispatching the engineer; ambiguous/high-risk specs go to the
  user first — never engineer on an unseen spec.
- **Post-stage verification**: Master runs `git log -1 --oneline` after each
  stage to confirm the stage commit landed (a stage that produced no commit
  silently produced nothing) before dispatching the next.
- **Semgrep gate is diff-scoped**: QA now scans only the commit under review
  (`git diff --name-only HEAD~1..HEAD`) instead of the whole repo, so
  pre-existing findings never pollute the verdict; findings are described as
  deterministic signals, not unverified "ground truth".
- **Prohibition clarified**: the Master's no-file-writing rule now explicitly
  carves out the one governance file it may patch
  (`skills/se-team-rules/SKILL.md`), resolving the contradiction with Rule
  Evolution.
- **Ops skill hygiene**: `hermes-enterprise-ops` pitfalls updated (dead
  `agent_slug`/README.zh-CN pitfalls removed, deliverable-path and
  diff-scoped-Semgrep pitfalls added), version synced to 2.0.7.

## 2.0.6
- **Sync root-cause fix**: `scripts/sync_skills.py` no longer ignore-lists
  `se-team-rules` — rule updates now mirror to the installed copy like every
  other skill, and `--check` detects rule drift. Previously the Rule Evolution
  loop told the Master to re-run sync after patching rules, but the sync
  silently skipped that skill, so the installed copy kept diverging.
- **Mirror hygiene**: only runtime files are mirrored (Master SKILL.md,
  `scripts/`/`templates/`/`references/`, and full `skills/` trees — role-skill
  references files are no longer dropped). Docs, tests, CI, and distribution
  metadata stay repo-only, so editing them no longer causes `--check` drift in
  the installed copy.
- **Framework consistency tests**: new `tests/test_framework_consistency.py`
  asserts the four version locations agree, the dispatch convention (4 fields +
  `load` clause) stays present, and every template referenced by a role skill
  exists.
- **distribution.yaml**: description updated to match the v2.0 positioning
  (was v1-era "Enterprise-grade, artifact-driven").
- **CI**: workflow now runs the Semgrep gate (`semgrep scan --config auto
  --error` on scripts/tests). The coverage gate (fail_under=80 via pyproject)
  already existed but the suite scored 78% — tests extended to cover the sync
  CLI error paths.

## 2.0.5
- **Semgrep in the QA pipeline (layered review)**: QA now runs Semgrep first
  (zero-token deterministic scan — pattern bugs / security rules are ground
  truth, no LLM confirmation needed), then OCR/LLM reviews only the remaining
  semantic questions, then the manual review issues the verdict.
  - `se-team-qa-release`: new Step 1 (Semgrep) with `semgrep scan --config
    auto --json`; steps renumbered; review-template gains a Semgrep findings
    section.
  - `scripts/install-deps.sh`: detects/installs Semgrep via pip (idempotent).
  - README: prerequisites table + layered-pipeline note.

## 2.0.4
- **Prerequisites & one-shot installer**: README gains a `Prerequisites &
  Dependencies` section (Git >= 2.41, Node >= 18, `ocr` CLI, Python >= 3.11)
  with an OCR-delegation-mode note (no LLM key needed). New
  `scripts/install-deps.sh` — idempotent check-and-install (installs only
  `ocr` via npm, reports hints for system-level deps); handles the Windows
  `python3` Microsoft-Store-alias stub by falling back to `python`.

## 2.0.3
- **Dispatch `load` clause**: the Master's dispatch convention now mandates a
  `load:` field in every `delegate_task` context (`Load skill: <stage-role>.
  Load se-team-rules.`). Verified against Hermes source: subagent system
  prompts contain no skill index — they never auto-load skills; the `load`
  clause is the only entry point. This closes the sole failure mode of
  skill-less subagent runs. Pipeline sections now carry the exact load clause
  per stage; README dispatch example updated.

## 2.0.2
- **Role skill enrichment** (kept lightweight, no new scripts/files):
  - `se-team-design`: 5-step workflow (clarify → requirements → trade-offs →
    architecture → plan) with stop-and-report guardrails.
  - `se-team-engineer`: explicit RED→GREEN→REFACTOR evidence discipline,
    scope discipline (implement ACs only), and verification requirements.
  - `se-team-qa-release`: severity table (critical/high/medium/low) and
    verdict rules (`REJECTED`/`CHANGES_REQUESTED`/`APPROVED`) so review
    judgments no longer depend on general LLM common sense alone; OCR
    findings must be confirmed by manual review before affecting a verdict.

## 2.0.1
- **i18n cleanup**: repository is now English-only. Removed `README.zh-CN.md`
  and its link in `README.md`; rewrote `templates/spec-template.md` placeholders
  in English (the last Chinese content in the repo).

## 2.0.0
- **Daily-driver rewrite**: the framework is now a lightweight, git-native,
  3-stage pipeline (`design → engineer → QA`). Breaking change — v1.x
  Contract/manifest architecture is removed entirely.
- **Deleted**: all manifest/SHA machinery (`artifact_io`, `artifact_naming`,
  `close_run`, `manifest_lineage`, `task_contract`, `validate_artifact`,
  `update_kanban`, `self_health_check`), `kanban/`, the
  `se-team-compliance-reviewer` and `se-team-rule-manager` roles, 8 of 11
  templates, and 7 of 8 test modules (only `test_sync_skills.py` remains).
- **Trust = git**: subagents self-commit with stage-tagged messages; `git log`
  is the lineage; a git ref is the input validation. No contract files.
- **Dispatch convention**: 4 fields (`run`, `stage`, `output`, `rule`) in the
  delegate context instead of an 8-section contract.
- **Soft QA gate**: OCR mechanical review (advisory) + manual review with
  `APPROVED / CHANGES_REQUESTED / REJECTED`; the Master decides rework vs.
  pass; user final acceptance is the backstop.
- **Rework loop**: QA findings return to the responsible stage (engineer for
  implementation, design for requirements) with the QA report as input;
  escalation to the user after repeated failures (default 2).
- **Rule evolution**: QA reports may suggest rule updates; the Master patches
  `se-team-rules` directly (governance is strategy duty, not business code).
- **Design output**: single `spec.md` (requirements + architecture +
  implementation plan) replaces the 5-artifact design set.
- **Kept**: `sync_skills.py`, `se-team-rules`, role skills (rewritten),
  3 templates (rewritten), `test_sync_skills.py`.

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
