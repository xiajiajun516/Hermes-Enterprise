---
name: software-engineering-team
version: 1.4.0
description: "Forward-only Contract-driven Software Engineering AI Team orchestration."
category: software-development
---
# Software Engineering AI Team — Master

## Dispatch Prerequisites

Every future pipeline dispatch must first create
`artifacts/runs/<run-id>__contract.md` with create-new / exclusive-write semantics. The Master
may pass only the Contract's exact path and SHA-256, exact `inputs[]` paths and SHA-256 values,
and declared create-new outputs to a Subagent.

Never select inputs using `latest`, globbing, directory traversal, mtime, filename guessing, or
root-level `artifacts/*.md` legacy files. Future outputs must be Git-tracked, immutable agent
artifacts linked by a Git-tracked manifest. Root-level legacy files are neither migrated nor
runtime inputs.

Every dynamic Task Contract must begin with an environment gate: explicitly `cd` to the repository,
assert `pwd`, and verify that every exact input and required script exists. If the gate fails,
report `BLOCKED` and write no paths.

## Complete Dynamic Task Contract Required for Every Subagent

Copy the following body into `delegate_task` context and replace every `<...>` placeholder with an
actual value; no placeholder may remain after substitution. Front-matter `inputs` / `outputs` may
contain only exact paths and must never rely on inference.

```markdown
---
contract_version: "1.0"
run_id: "<YYYYMMDDTHHmmss-SSS>"
created_at_utc: "<YYYY-MM-DDTHH:mm:ss.SSSZ>"
tier: "<P0|P1|P2>"
stage: "<2a|2b|2c|2d|2e|2f>"
attempt: <positive-integer>
agent_display_name: "<display-name>"
agent_slug: "<product-research|architect|compliance-reviewer|engineer|qa-release|rule-manager>"
parent_run_id: <null-or-YYYYMMDDTHHmmss-SSS>
language: "en-US"
inputs:
  - path: "artifacts/<producer-slug>/<producer-run-id>__<artifact-name>.md"
    artifact_name: "<artifact-name>"
    sha256: "<64-lowercase-hex>"
    producer_run_id: "<producer-run-id>"
outputs:
  - agent_slug: "<agent-slug>"
    artifact_name: "<artifact-name>"
    target_path: "artifacts/<agent-slug>/<run-id>__<artifact-name>.md"
    template: "<exact-template-path>"
    write_mode: "create-new"
---

## Run Identity
run_id: <same-as-frontmatter>
created_at_utc: <same-as-frontmatter>

## Goal & Scope
goal: <specific-deliverable>
scope: <authorized-work-boundary>

## Source of Truth
source: <each-authoritative-input-path-and-SHA-256>

## Environment SOP
command: cd /c/Repository/hermes-enterprise-profile-push && test "$(pwd)" = "/c/Repository/hermes-enterprise-profile-push" && <prerequisite-checks>

## Artifact I/O Contract
inputs: <only-frontmatter-inputs; validate path, Git tracking and recomputed SHA before read>
outputs: <only-frontmatter-outputs; create-new, UTC naming, exclusive write and Git tracking>

## Checksum / Verification
sha256: <recalculate-every-input-and-output-SHA-256>
verification: <exact-commands, expected-exit-codes, and validation criteria>

## Hard Prohibitions
prohibited: legacy inputs, latest, glob, mtime, traversal, guessed inputs, overwrite, undeclared writes, and Git mutations unless explicitly authorized

## Final Report Protocol
report: English; include the Contract run_id, exact input/output paths, SHA-256 values, actual commands and exit codes, verification results, BLOCKED state, risks, and omitted work
```

Before dispatching, the Master must validate the Contract with
`python scripts/validate_artifact.py <exact-contract-path>` and accept only tracked manifest lineage.

| Stage | slug | standard outputs |
|---|---|---|
|2a|product-research|research, spec-draft, spec|
|2b|architect|architecture, implementation-plan|
|2c|compliance-reviewer|compliance-report|
|2d|engineer|implementation-report|
|2e|qa-release|review, test-report, release|
|2f|rule-manager|governance-report|