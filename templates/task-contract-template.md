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