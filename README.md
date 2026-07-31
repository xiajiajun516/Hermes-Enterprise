# 🚀 Hermes Enterprise

An enterprise-grade, artifact-driven, self-evolving AI software engineering team **Master Skill** for **Hermes Agent**.

[中文版 (Chinese Version)](./README.zh-CN.md)

---

## ⚡ Quick Skill Installation

You can install and use this skill across all your Hermes sessions using any of the following methods:

### Method 1: Git Clone into Hermes Global Skills Directory (Recommended)

**Linux / macOS / Git Bash:**
```bash
# Main orchestrator skill
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git ~/.hermes/skills/software-engineering-team

# Install sub-agent skills (optimized dispatch)
cp -r ~/.hermes/skills/software-engineering-team/skills/* ~/.hermes/skills/
```

**Windows (PowerShell / CMD):**
```cmd
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team

xcopy /E /I %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team\skills\* %USERPROFILE%\AppData\Local\hermes\skills\
```

Once cloned, Hermes automatically indexes all skills globally across **all** your chats and profiles!

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

- **Master Orchestrator Entry Point**: `SKILL.md` acts as an executable step-by-step orchestrator guide for the agent.
- **Skill-Based Dispatch** (v1.1 optimized): Subagents self-load their role, methodology, templates, and rules via `skill_view()` — no more manual context injection of verbose prompt files. Master Agent only needs to specify the skill name + task context.
- **Zero Configuration**: Inherits your active session's LLM provider, API keys, and toolchain directly.
- **Artifact-Driven Collaboration**: Eliminates dependency on chat history by producing durable Markdown/Code artifacts (`spec.md`, `architecture.md`, `compliance-report.md`, etc.).
- **Minimal Context Policy**: Strictly limits subagent contexts to essential artifacts, reducing token consumption.
- **Automated Validation Gates**: Integrates Python scripts (`validate_artifact.py`, `validate_kanban.py`) into execution pipelines for schema enforcement.
- **Compliance Gate & Self-Correction Loop**: Automatically audits specifications against design/tech standards before coding begins.
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
Hermes-Enterprise/
├── SKILL.md                # Master Orchestrator Entry Point
├── PLAN.md                 # Complete Architecture & Plan Specification (Chinese)
├── README.md               # Overview & Skill Installation Guide
├── LICENSE                 # MIT License
├── skills/                 # Standalone Sub-Agent Skills (v1.1)
│   ├── se-team-product-research/SKILL.md
│   ├── se-team-architect/SKILL.md
│   ├── se-team-engineer/SKILL.md
│   ├── se-team-compliance-reviewer/SKILL.md
│   ├── se-team-qa-release/SKILL.md
│   ├── se-team-rule-manager/SKILL.md
│   └── se-team-rules/SKILL.md
├── references/             # Linked References & Prompt Configurations (legacy)
│   ├── agents/             # Agent Prompt Configurations (01 to 07)
│   └── rules/              # Project Design Tokens & Security Rules (legacy)
├── templates/              # Standard Deliverable Artifact Templates
├── artifacts/              # Standard Output Artifacts Location
├── kanban/                 # Task Pipeline Kanban Tracking (`kanban.md`)
└── scripts/                # Validation & Helper Scripts
```

---

## 🤖 Agent Matrix (v1.1 — Skill-Based)

| Agent | Role | Hermes Skill | Main Deliverable |
| :--- | :--- | :--- | :--- |
| **01. Workflow Manager** | Controller & Pipeline Manager | `software-engineering-team` (Master) | `kanban.md` |
| **02. Product & Research** | Requirements & Feasibility | `se-team-product-research` | `spec.md`, `research.md` |
| **03. Architect Agent** | System & DB Architecture | `se-team-architect` | `architecture.md`, `implementation-plan.md` |
| **04. Engineer Agent** | Code & Unit Test Implementation | `se-team-engineer` | Source Code |
| **05. Compliance Reviewer**| Static Gatekeeper Audit | `se-team-compliance-reviewer` | `compliance-report.md` |
| **06. QA & Release** | Review, Testing & Deployment | `se-team-qa-release` | `review.md`, `test-report.md`, `release.md` |
| **07. Rule Manager** | Governance & Evolution | `se-team-rule-manager` | Rules update & Scope Recall |
| — | Shared Project Rules | `se-team-rules` | Loaded by all agents |

### How Dispatch Works (Optimized)

**Before (v1.0):** Master Agent manually reads 3-6 files, concatenates them into a giant context string.

**After (v1.1):** Master Agent tells the subagent which skill to load:
```
delegate_task(
  goal="Design system architecture for user auth service",
  context="Load skill: se-team-architect. Load se-team-rules for standards. Read artifacts/spec.md. Output artifacts/architecture.md. Respond in Chinese."
)
```

The subagent calls `skill_view('se-team-architect')` and gets its role, methodology, templates, and prohibitions — all self-contained. Rules are loaded via `skill_view('se-team-rules')`.

---

## 🔄 Self-Correction Loop

```text
[Product / Architect Agent] ──► Generates Spec / Architecture
                                         │
                                         ▼
[Compliance Reviewer] ─────────► Audits against se-team-rules
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
