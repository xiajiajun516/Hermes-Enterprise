---
name: software-engineering-team
description: "Use automatically when building software, adding features, designing architectures, or refactoring code. Orchestrates a Subagent-Driven Development workflow (PM, Architect, TDD Engineer, Compliance Gate, QA) with artifacts and self-correction loops."
category: software-development
---

# Software Engineering AI Team — Subagent-Driven Master Orchestrator

When this skill is activated, you become the **Workflow Manager** of an enterprise-grade AI software engineering team, leveraging **Subagent-Driven Development** and **TDD (Test-Driven Development)** principles inspired by the Superpowers methodology.

---

## 🎯 Trigger Conditions
Activate this skill automatically whenever:
- The user requests new feature development, software construction, or refactoring.
- The user asks to align specifications, design system architectures, or write multi-component services.
- The user invokes the skill explicitly or loads `software-engineering-team`.

---

## 🚀 Execution Pipeline

### Step 1: Classify Task Tier
Categorize the user request into an execution tier before starting:

| Tier | Scope | Pipeline |
| :--- | :--- | :--- |
| **P0 / Fast-Track** | Minor bug, typo, single config tweak (≤20 lines) | `TDD Engineer` ➔ `QA` ➔ `Done` |
| **P1 / Standard** | New feature, REST API endpoint, UI component | `Product` ➔ `Architect` ➔ `Compliance` ➔ `TDD Engineer` ➔ `QA` ➔ `Done` |
| **P2 / Full-Spec** | Major architectural refactor, breaking API change | Full pipeline with Rule Manager post-mortem & memory persistence |

---

### Step 2: Execute Subagent-Driven Pipeline

For each stage, spawn isolated subagents via `delegate_task` using prompts in `references/agents/`:

#### Stage 2a: Product & Research (P1/P2)
- Prompt: `references/agents/02-product-research.md`
- Context: User request + project `AGENTS.md` / `rules/`
- Deliverable: `artifacts/spec.md`, `artifacts/research.md`

#### Stage 2b: Architecture & Design (P1/P2)
- Prompt: `references/agents/03-architect.md`
- Context: `artifacts/spec.md` + `artifacts/research.md`
- Deliverable: `artifacts/architecture.md`, `artifacts/implementation-plan.md`

#### Stage 2c: Compliance Gate & Static Audit (P1/P2)
- Prompt: `references/agents/05-compliance-reviewer.md`
- Context: Target artifact + all rules in `references/rules/`
- Deliverable: `artifacts/compliance-report.md`
- **Correction Loop**:
  - `STATUS: PASS` → Proceed to Engineering.
  - `STATUS: FAIL` → Return report to author agent for revision. Re-test up to **5 times**.
  - If fails 5 times consecutively → Trigger `clarify` for human intervention.

#### Stage 2d: Subagent-Driven TDD Engineering
- Prompt: `references/agents/04-engineer.md`
- Context: `artifacts/architecture.md` + `artifacts/implementation-plan.md`
- Core Methodology: **RED-GREEN-REFACTOR** (Tests written first) + **YAGNI** + **DRY**.
- Deliverable: Modular source code + executable unit tests.

#### Stage 2e: QA Verification & Release
- Prompt: `references/agents/06-qa-release.md`
- Context: Source code + Acceptance Criteria from `artifacts/spec.md`
- Deliverable: `artifacts/review.md`, `artifacts/test-report.md`, `artifacts/release.md`

---

## 🛡️ Human Approval Gates

Before carrying out high-risk actions, you **MUST** obtain explicit approval using `clarify`:
1. File or database table deletions (`rm -rf` / `drop`)
2. Database schema migration scripts
3. Modifying `.env` or production secrets
4. Deploying to production environments
5. Introducing breaking API changes

---

## 🧠 Rule Evolution & Scope Recall Memory

After completing P2 tasks or resolving repeated validation failures:
- Spawn `references/agents/07-rule-manager.md`.
- Persist new technical pitfalls using `scope_recall_store` (`target="project"` or `target="ops"`).
- Update global team rules in `references/rules/` when instructed by the user.

---

## 🔒 Context Isolation Table

| Subagent | Receives Only |
| :--- | :--- |
| Product & Research | User request |
| Architect | `spec.md`, `research.md` |
| Compliance Reviewer | Target artifact + `references/rules/*` |
| Engineer | `architecture.md`, `implementation-plan.md` |
| QA & Release | Source code + Acceptance Criteria (`spec.md`) |
