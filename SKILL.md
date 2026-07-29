---
name: software-engineering-team
description: "Use when building software projects requiring structured multi-agent coordination (PM, Architect, Engineer, Compliance Gate, QA) with artifact-driven workflows."
category: software-development
---

# 🚀 Software Engineering AI Team Skill

This skill turns Hermes into an enterprise-grade, artifact-driven software engineering AI team consisting of 5 core roles and 2 governance roles.

## 🎯 When to Trigger
Use this skill when:
- The user requests end-to-end software development, architectural design, or complex feature implementation.
- You need a structured, artifact-driven workflow (with `spec.md`, `architecture.md`, `compliance-report.md`, `test-report.md`).
- You need automated static compliance review (`rules/*.md`) and a self-correction loop before coding.

---

## 🤖 Team Role & Agent Matrix

1. **Workflow Manager**: Master controller that dispatches subagents, tracks `kanban/kanban.md`, and requests `clarify` approvals for high-risk operations.
2. **Product & Research**: Generates functional specs (`artifacts/spec.md`) and technical research (`artifacts/research.md`).
3. **Architect Agent**: Designs module trees, DB schema, and execution roadmaps (`artifacts/architecture.md`, `implementation-plan.md`).
4. **Engineer Agent**: Implements modular source code and unit tests based strictly on approved architecture.
5. **Compliance Reviewer**: Static gatekeeper auditing `spec.md`/`architecture.md` against rules in `rules/`, outputting `compliance-report.md` (`STATUS: PASS/FAIL`).
6. **QA & Release**: Runs test suites, code/security audits (`artifacts/review.md`), and prepares release notes (`artifacts/release.md`).
7. **Rule Manager**: Updates `rules/*.md` and Scope Recall memory (`project`/`ops` target) based on user policy updates or post-mortems.

---

## 🔄 Self-Correction & Compliance Loop

Before any code is written, static compliance review MUST pass:

```text
[Product / Architect Agent] ──► Generates Spec / Architecture
                                         │
                                         ▼
[Compliance Reviewer] ─────────► Audits against rules/*.md
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
             STATUS: FAIL                                STATUS: PASS
                   │                                           │
                   ▼                                           ▼
[Return to Product/Architect for revision]       [Proceed to Implementation]
```

- **Threshold Guard**: If compliance fails 5 consecutive times, Workflow Manager must pause and prompt user via `clarify`.

---

## 📋 Artifact Delivery Policy

All subagents communicate strictly through Markdown Artifacts stored under `artifacts/`:
- `spec.md`: Scope, User Stories, Acceptance Criteria
- `architecture.md`: Folder Tree, Module, API, DB Schema
- `compliance-report.md`: Rule audit details and `STATUS: PASS/FAIL`
- `review.md` & `test-report.md`: Code quality, security, and test verification logs

---

## ⚡ Execution Tiers

- **P0 / Fast-Track**: Minor bugs/typos → `Engineer` ➔ `QA` ➔ `Done`
- **P1 / Standard**: Standard features → `Product` ➔ `Architect` ➔ `Compliance Gate` ➔ `Engineer` ➔ `QA` ➔ `Done`
- **P2 / Full-Spec**: Major architecture/breaking change → Full multi-stage pipeline with Rule Manager review.
