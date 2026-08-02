---
name: software-engineering-team
version: 2.0.7
description: "Lightweight 3-stage engineering team orchestration (design→engineer→QA)."
category: software-development
---
# Software Engineering AI Team — Master (v2.0)

Daily-driver edition: a three-stage pipeline (design → engineer → QA). Immutability, lineage, and state tracking are handled entirely by git — no hand-written manifest/SHA machinery. The Master (this agent) only does strategy and dispatch; it never writes business code, SQL, or files itself — all execution is done by Subagents.

## Roles

| Stage | Skill | Deliverable |
|---|---|---|
| design | `se-team-design` | `artifacts/spec.md` (requirements + architecture + implementation plan) |
| engineer | `se-team-engineer` | implementation code + `artifacts/report.md` |
| qa | `se-team-qa-release` | `artifacts/review.md` (Semgrep + OCR gate + verdict) |

Deliverable paths are fixed — subagents write to the exact paths above, and these files are git-tracked (never ignore them). Every agent also loads `se-team-rules` for project standards.

## Dispatch Convention (4 fields + load clause)

Every `delegate_task` context carries these fields — no contract file, no script validation; **a git ref is the validation**:

```text
run:    <stage>-<short-slug>          # e.g. design-auth-flow
stage:  design | engineer | qa
output: artifacts/spec.md | artifacts/report.md | artifacts/review.md   # fixed per stage — see Roles table
rule:   Never overwrite another stage's output; never rewrite git history; obey se-team-rules
load:   Load skill: <stage-role>. Load se-team-rules.
```

- **`load` is mandatory**: subagents do NOT auto-load skills — their system prompt has no skill index. The `load` clause is the only entry point; a missing `load` means the subagent runs skill-less. Always write both the stage role skill and `se-team-rules` (stage → skill mapping is fixed by the Roles table above).
- **Input = git ref**: the subtask works from the current branch HEAD (or an explicitly named commit).
- **Commit = the subagent commits itself**: `git add` + `git commit -m "<type>(<stage>): <desc>"` — the stage tag in the message makes `git log` the lineage.
- **Verify after each stage**: before dispatching the next stage, the Master runs `git log -1 --oneline` and confirms the stage-tagged commit landed (and `git status` is clean). A stage that produced no commit silently produced nothing — re-dispatch it.
- Upstream output is the next stage's input: QA consumes the engineer's commit.

## Pipeline

### 1. design
Dispatch `se-team-design` (`load: Load skill: se-team-design. Load se-team-rules.`): analyze the goal, produce `artifacts/spec.md` (requirements + architecture + implementation plan), commit it.

### Spec gate (before engineer)
The Master reads `artifacts/spec.md` and decides:
- **Clear and scoped** → dispatch engineer.
- **Ambiguous, self-contradictory, or high-risk** → confirm with the user first (the user is the spec authority); never let the engineer build on a spec the user hasn't seen. Re-dispatch design if requirements need another pass.

### 2. engineer
Dispatch `se-team-engineer` (`load: Load skill: se-team-engineer. Load se-team-rules.`): TDD implementation (RED→GREEN→REFACTOR), produce code + `artifacts/report.md`, commit it.

### 3. QA (soft gate)
Dispatch `se-team-qa-release` (`load: Load skill: se-team-qa-release. Load se-team-rules.`):
1. Run Semgrep scan scoped to the reviewed commit (deterministic, zero-token) — see the role skill for the exact command.
2. OCR review (`ocr review --audience agent`, or delegate mode) — advisory signal.
3. Manual agent review → `artifacts/review.md` with verdict: `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.

## Rework Loop

QA findings → Master decides:
- **Implementation error** → back to engineer: new run, input = current HEAD (QA report included), fix and self-commit.
- **Requirement/design error** → back to design, same pattern.
- After N failed reworks (default 2), escalate to the user for clarification — never loop indefinitely.

Soft gate: the Master may let a marginal review pass (the user's final acceptance is the backstop).

## Rule Evolution (self-update)

QA reports may append a one-line rule suggestion (e.g. "third NPE of the same kind — suggest adding a rule to se-team-rules"). The Master decides and directly patches `skills/se-team-rules/SKILL.md` + commits it (governance is the Master's strategy duty, not business code). Afterwards re-run `python scripts/sync_skills.py` to refresh the installed Hermes copy.

## Hard Prohibitions

- The Master never writes business code / SQL / project files — dispatch, decide, and patch the rules skill only (see Rule Evolution; governance is strategy, and `skills/se-team-rules/SKILL.md` is the one file the Master may edit).
- Never rewrite git history (forward-only: a wrong record is corrected by a new commit).
- Never overwrite another stage's output file.

## Tooling

- `scripts/sync_skills.py` — mirror repo skills into the Hermes skills dir (`--check` detects drift).
