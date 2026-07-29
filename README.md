# 🚀 Hermes Enterprise Profile (Software Engineering AI Team)

An enterprise-grade, artifact-driven, self-evolving AI software engineering team profile distribution for **Hermes Agent**.

[中文文档 (Chinese Version)](./PLAN.md)

---

## ⚡ Quick Install

You can install this profile distribution directly into your Hermes Agent with a single command:

```bash
hermes profile install https://github.com/xiajiajun516/hermes-enterprise-profile
```

Or run directly from a local clone:

```bash
hermes profile install .
```

After installation, start using this profile:

```bash
hermes -p software-engineering-team chat
```

---

## 🌟 Core Features

- **Single Profile Architecture**: Multi-agent organization within a single unified profile (`software-engineering-team`).
- **Artifact-Driven Collaboration**: Eliminates dependency on chat history by producing durable Markdown/Code artifacts (`spec.md`, `architecture.md`, `compliance-report.md`, etc.).
- **Minimal Context Policy**: Strictly limits subagent contexts to essential artifacts, reducing token consumption and interference.
- **Compliance Gate & Self-Correction Loop**: Automatically audits specifications against design/tech standards (`rules/*.md`) before coding begins.
- **Self-Evolving Governance**: Features a `Rule Manager Agent` that updates rules and Scope Recall memory (`project` / `ops` scopes) based on post-mortems and user directives.
- **Approval Gates**: High-risk operations (deletions, DB migrations, deployments) require human confirmation via Hermes `clarify`.

---

## 📂 Repository Layout

```text
hermes-enterprise-profile/
├── distribution.yaml       # Hermes Profile Distribution Manifest
├── PLAN.md                 # Complete Architecture & Plan Specification
├── README.md               # Overview & Getting Started Guide
├── LICENSE                 # MIT License
├── agents/                 # Specialized Agent Definitions & Prompts
│   ├── 01-workflow-manager.md
│   ├── 02-product-research.md
│   ├── 03-architect.md
│   ├── 04-engineer.md
│   ├── 05-compliance-reviewer.md
│   ├── 06-qa-release.md
│   └── 07-rule-manager.md
├── rules/                  # Project Design Tokens & Tech Stack Rules
│   ├── design-system.md
│   ├── tech-stack.md
│   └── security.md
├── artifacts/              # Standard Output Artifacts Location
├── kanban/                 # Task Pipeline Kanban Tracking (`kanban.md`)
└── scripts/                # Validation & Helper Scripts
```

---

## 🤖 Agent Matrix

| Agent | Role | Main Output / Deliverable |
| :--- | :--- | :--- |
| **01. Workflow Manager** | Controller & Pipeline Manager | `kanban.md` |
| **02. Product & Research** | Requirements & Feasibility | `spec.md`, `research.md` |
| **03. Architect Agent** | System & DB Architecture | `architecture.md`, `implementation-plan.md` |
| **04. Engineer Agent** | Code & Unit Test Implementation | Source Code |
| **05. Compliance Reviewer**| Static Gatekeeper Audit | `compliance-report.md` |
| **06. QA & Release** | Review, Testing & Deployment | `review.md`, `test-report.md`, `release.md` |
| **07. Rule Manager** | Governance & Evolution | `rules/*.md` & Scope Recall Memory |

---

## 🔄 Self-Correction Loop

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

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
