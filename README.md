# 🚀 Hermes Enterprise

A lightweight, git-native, 3-stage AI software engineering team **Master Skill** for **Hermes Agent** — daily-driver edition (v2.0).

---

## ⚡ Quick Skill Installation

Install and use this skill across all your Hermes sessions:

### Method 1: Git Clone into Hermes Global Skills Directory (Recommended)

**Linux / macOS / Git Bash:**
```bash
# Main orchestrator skill
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git ~/.config/hermes/skills/software-engineering-team

# Install sub-agent skills
cp -r ~/.config/hermes/skills/software-engineering-team/skills/* ~/.config/hermes/skills/
```

**Windows (PowerShell / CMD):**
```cmd
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team

xcopy /E /I %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team\skills\* %USERPROFILE%\AppData\Local\hermes\skills\
```

Once cloned, Hermes automatically indexes all skills globally across **all** your chats and profiles!

---

## 📦 Prerequisites & Dependencies

| Dependency | Purpose | Requirement |
|:---|:---|:---|
| Git | Pipeline core (a git ref is the validation) | >= 2.41 |
| Node.js + npm | Install the `ocr` CLI | >= 18 |
| `ocr` CLI (alibaba/open-code-review) | QA-stage LLM review gate | `npm i -g @alibaba-group/open-code-review` |
| Semgrep | QA-stage deterministic scan (zero-token, pattern bugs/security) | `pip install semgrep` |
| Python | `scripts/sync_skills.py` + Semgrep | >= 3.11 |

**One-shot check & install** (idempotent; installs `ocr` via npm and Semgrep via pip, reports hints for system-level deps):

```bash
bash scripts/install-deps.sh
```

**OCR LLM (optional)**: the QA gate works in **delegation mode** out of the box — the host agent's own model performs the review, no OCR LLM key needed. Only if you want OCR to use its own LLM, configure one:

```bash
ocr config provider   # interactive: pick provider, enter key, pick model
ocr config model
```

**QA review pipeline (layered)**: Semgrep scans first (zero-token, deterministic — pattern bugs/security rules are ground truth), then OCR/LLM reviews only the remaining semantic questions, then the manual review issues the verdict.

### Method 2: Preload via CLI Flag
```bash
hermes -s software-engineering-team
```

---

### Method 3: In-Chat Invocation
> *"Load skill software-engineering-team and build a user authentication service for this repository."*

---

## 🌟 Core Highlights

- **3-Stage Pipeline**: `design → engineer → QA`. The Master (Workflow Manager) only does strategy and dispatch — it never writes business code, SQL, or files itself; all execution is done by subagents.
- **Git-Native Trust**: Immutability, lineage, and state tracking are handled entirely by git — subagents self-commit with stage-tagged messages, so `git log` *is* the lineage. No hand-written manifest/SHA machinery.
- **Zero Configuration**: Inherits your active session's LLM provider, API keys, and toolchain directly.
- **Skill-Based Dispatch**: Subagents self-load their role via `skill_view()` — no manual context injection.
- **Soft QA Gate**: OCR mechanical review (advisory) + manual review with `APPROVED / CHANGES_REQUESTED / REJECTED` verdict; the Master decides rework vs. pass, and the user's final acceptance is the backstop.
- **Rework Loop**: QA findings return to the responsible stage (engineer for implementation, design for requirements) with the QA report as input; escalates to the user after repeated failures.
- **Self-Evolving Rules**: QA reports may suggest rule updates; the Master patches `se-team-rules` directly (governance is strategy, not business code).
- **Lightweight**: 4 role skills + 3 templates + 1 sync script. Everything else was cut in v2.0.

---

## 📂 Repository Layout

```text
Hermes-Enterprise/
├── SKILL.md                # Master Orchestrator Entry Point
├── README.md               # Overview & Skill Installation Guide
├── LICENSE                 # MIT License
├── skills/                 # Sub-Agent Skills
│   ├── se-team-design/SKILL.md
│   ├── se-team-engineer/SKILL.md
│   ├── se-team-qa-release/SKILL.md
│   └── se-team-rules/SKILL.md
├── templates/              # Deliverable Templates (spec / report / review)
└── scripts/
    └── sync_skills.py      # Mirror repo skills into the Hermes skills dir
```

---

## 🤖 Agent Matrix (v2.0)

| Agent | Role | Hermes Skill | Main Deliverable |
| :--- | :--- | :--- | :--- |
| **Workflow Manager** | Strategy & Dispatch only | `software-engineering-team` (Master) | 4-field run convention |
| **Design Agent** | Requirements + Architecture | `se-team-design` | single `spec.md` |
| **Engineer Agent** | TDD Code & Unit Tests | `se-team-engineer` | code + `implementation-report` |
| **QA & Release** | OCR gate + Review | `se-team-qa-release` | `review.md` (verdict) |
| — | Shared Project Rules | `se-team-rules` | Loaded by all agents |

### How Dispatch Works (v2.0)

The Master dispatches with a **4-field convention** — no contract file, no script validation; a git ref is the validation:

```
delegate_task(
  goal="Design system architecture for user auth service",
  context="run: design-auth-flow. stage: design. "
          "output: docs/design/design-auth-flow-spec.md. "
          "rule: never overwrite other stages' output, never rewrite git history. "
          "load: Load skill: se-team-design. Load se-team-rules. "
          "Commit your deliverable yourself. Respond in Chinese."
)
```

The subagent calls `skill_view('se-team-design')`, gets its role and template, works from the current git HEAD, and self-commits. `git log` becomes the readable lineage.

---

## 🔄 Self-Correction Loop

```text
[Design Agent] ──► spec.md commit
        │
        ▼
[Engineer Agent] ──► code + report commit (TDD)
        │
        ▼
[QA & Release] ──► OCR review (advisory) + manual review → verdict
        │
   ┌────┴────┐
   ▼         ▼
CHANGES_REQUESTED      APPROVED
   │                   │
   ▼                   ▼
back to responsible    user final acceptance
stage (engineer/design)
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
