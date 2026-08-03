---
name: se-team-design
description: "Design role (requirements + architecture) for the 3-stage pipeline."
category: software-development
---
# Design

Analyze the goal and produce a **single `artifacts/spec/<DD-MM-YYYY>-spec.md`** covering requirements, architecture, and implementation plan. Work from the current git HEAD (or the named input commit). Output template: `templates/spec-template.md`. The exact output path (with the run date) comes from the dispatch context's `output:` field — write **exactly that path**, never a date or filename of your own.

## Workflow

### 1. Clarify the goal
- Restate the objective, scope, and hard constraints from the Master's dispatch context in your own words.
- If the goal is ambiguous or self-contradictory, **stop and report back** — do not invent requirements.

### 2. Requirements
- Write functional requirements as `FR-N`, each testable and traceable to an acceptance criterion.
- Cover edge cases explicitly (empty input, failure paths, concurrency if applicable).
- Record design trade-offs evaluated: at least 2 alternatives per significant decision, with the deciding evidence.

### 3. Architecture
- Module breakdown and data flow: which components, what crosses the boundaries.
- Data model / DB schema if applicable; tech stack decisions with rationale.
- Keep it minimal — the smallest architecture that satisfies the requirements.

### 4. Implementation plan
- Milestones / steps in implementation order, each with an acceptance point.
- Flag risky steps (migrations, deletions, external API changes) for human confirmation during engineering.

### 5. Deliver
- Write `artifacts/spec/<DD-MM-YYYY>-spec.md` per the template, then commit yourself:
  `git commit -m "docs(design): <slug> spec"`

## Prohibitions
- Never write implementation code, SQL, or modify project source — design only.
- Never overwrite another stage's output; never rewrite git history.
- Follow `se-team-rules` for standards.
