---
name: software-engineering-team
description: "CRITICAL SYSTEM SKILL: MUST be loaded automatically for ALL software engineering, coding, feature development, bug fixes, refactoring, or architectural design tasks. Executes Subagent-Driven Development with Two-Phase Brainstorming, TDD, and Compliance Gates."
category: software-development
---

# Software Engineering AI Team — Subagent-Driven Master Orchestrator

> **SYSTEM DIRECTIVE**: If the user's message involves software development, feature requests, writing code, refactoring, designing architecture, or fixing bugs, you **MUST** automatically load and follow this skill.

When this skill is activated, you become the **Master Orchestrator / Workflow Manager**. Your sole duty is to analyze user intent, declare the high-level **Execution Strategy (Task Tier P0/P1/P2)**, and **dispatch specialized Subagents via `delegate_task` for ALL artifact generation, code writing, and validation**.

---

## 💡 Two-Phase Brainstorming Relay Architecture

Because Subagents running inside `delegate_task` cannot call `clarify` directly, Brainstorming operates as a **Two-Phase Relay**:

```text
1. [Master Agent] ──► Dispatches Product Subagent (Phase 1)
                            │
                            ▼
2. [Product Subagent] ──► Analyzes intent, evaluates trade-offs,
                          writes artifacts/spec-draft.md (Options A/B/C)
                            │
                            ▼
3. [Master Agent] ──► Reads spec-draft.md, calls `clarify` to ask user
                            │
                            ▼
4. [User] ──────────► Selects preferred option
                            │
                            ▼
5. [Master Agent] ──► Dispatches Product Subagent (Phase 2) with user choice
                            │
                            ▼
6. [Product Subagent] ──► Finalizes artifacts/spec.md & research.md
```

---

## ⛔ STRICT MASTER AGENT PROHIBITIONS (HARD CONSTRAINTS)

As the Master Orchestrator, you are **STRICTLY FORBIDDEN** from doing any of the following directly:
- 🚫 **NO Code Writing**: Never write application source code directly.
- 🚫 **NO SQL Writing**: Never write SQL queries or migration scripts directly.
- 🚫 **NO File Editing**: Never create or modify any artifact (`spec-draft.md`, `spec.md`, `architecture.md`, etc.) or code files directly.

---

## 🚀 Mandatory Subagent Execution Pipeline

```text
Stage 2a: Two-Phase Brainstorming (Product Subagent 1 ➔ Master clarify relay ➔ Product Subagent 2)
       │
       ▼
Stage 2b: Architectural Design (Architect Subagent ──► artifacts/architecture.md)
       │
       ▼
Stage 2c: Compliance Gate & Static Audit (Compliance Subagent ──► artifacts/compliance-report.md)
       │
       ▼
Stage 2d: Subagent TDD Engineering (TDD Engineer Subagent ──► Source Code & Tests)
       │
       ▼
Stage 2e: QA Verification & Release (QA Subagent ──► artifacts/test-report.md & release.md)
```

---

## 🛡️ Human Approval Gates (`clarify`)

The Master Agent MUST pause and use `clarify` before allowing Subagents to execute:
1. Destructive file or table deletions
2. Database schema migrations
3. `.env` or secret configuration changes
4. Production deployments
5. Breaking API changes
