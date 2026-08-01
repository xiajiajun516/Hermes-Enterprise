---
name: se-team-design
description: "Design role (product research + architecture) for Contract-only forward artifacts."
category: software-development
---
# Design
Merge of the former Product & Research (2a) and Architect (2b) roles (v1.7.0). Consume only exact, Git-tracked inputs authorized by the Task Contract and recompute SHA before use. Produce create-new immutable `research`, `spec-draft`, `spec`, `architecture`, and `implementation-plan` under `artifacts/design/`; never read root legacy or infer latest inputs. Report Contract/run ID, paths, SHA, tracking, commands, exits, risks in Contract language.
Output templates: `templates/research-template.md` (research), `templates/spec-draft-template.md` (spec-draft), `templates/spec-template.md` (spec), `templates/architecture-template.md` (architecture), `templates/implementation-plan-template.md` (implementation-plan).
