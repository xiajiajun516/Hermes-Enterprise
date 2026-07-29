# 🚀 Software Engineering AI Team Skill for Hermes

An enterprise-grade, artifact-driven, self-evolving AI software engineering team **Skill** for **Hermes Agent**.

[中文架构方案 (Chinese Specification)](./PLAN.md)

---

## ⚡ Quick Skill Installation

You can install and use this skill across all your Hermes sessions using any of the following methods:

### Method 1: Git Clone into Hermes Global Skills Directory (Recommended)

**Linux / macOS / Git Bash:**
```bash
git clone https://github.com/xiajiajun516/hermes-enterprise-profile.git ~/.hermes/skills/software-engineering-team
```

**Windows (PowerShell / CMD):**
```cmd
git clone https://github.com/xiajiajun516/hermes-enterprise-profile.git %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team
```

Once cloned, Hermes automatically indexes the skill globally across **all** your chats and profiles!

---

### Method 2: Preload via CLI Flag
Run Hermes with the `-s` flag to preload the skill directly from a local clone or URL:
```bash
hermes -s software-engineering-team
```

---

### Method 3: In-Chat Invocation
Once installed, simply invoke the skill in any active Hermes conversation:

> *"Load skill software-engineering-team and build a user authentication service for this repository."*

---

## 🌟 Core Highlights

- **Zero Configuration**: Inherits your active session's LLM provider, API keys, and toolchain directly.
- **Artifact-Driven Collaboration**: Eliminates dependency on chat history by producing durable Markdown/Code artifacts (`spec.md`, `architecture.md`, `compliance-report.md`, etc.).
- **Minimal Context Policy**: Strictly limits subagent contexts to essential artifacts, reducing token consumption.
- **Compliance Gate & Self-Correction Loop**: Automatically audits specifications against design/tech standards (`rules/*.md`) before coding begins.
- **Self-Evolving Governance**: Features a `Rule Manager Agent` that updates rules and Scope Recall memory (`project` / `ops` target scopes) based on post-mortems and user directives.
- **Approval Gates**: High-risk operations (deletions, DB migrations, deployments) require human confirmation via Hermes `clarify`.

---

## 🧠 Memory & Plugin Integration

### Scope Recall Integration (Recommended)
When paired with the `scope-recall-hermes` plugin, this skill automatically stores and retrieves domain-isolated memories:
- **`target="project"`**: Stores repository architecture conventions, module maps, and entity rules.
- **`target="ops"`**: Stores CI/CD parameters, server IPs, and deployment strategies.
- **`target="user"`**: Stores personal/team code style preferences.
- **`target="memory"`**: Stores general technical pitfalls and post-mortem lessons.

---

## 📂 Repository Layout

```text
hermes-enterprise-profile/
├── SKILL.md                # Skill Manifest & Entry Point
├── PLAN.md                 # Complete Architecture & Plan Specification (Chinese)
├── README.md               # Overview & Skill Installation Guide
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
