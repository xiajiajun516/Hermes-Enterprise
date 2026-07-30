---
name: software-engineering-team
version: 1.4.0
description: "Forward-only Contract-driven Software Engineering AI Team orchestration."
category: software-development
---
# Software Engineering AI Team — Master
Every future dispatch first create-news `artifacts/runs/<run-id>__contract.md`. Pass only its exact path/SHA, `inputs[]` paths/SHA and declared create-new outputs. Never select inputs with latest, glob, directory traversal, mtime, guessing, or root-level `artifacts/*.md` legacy files. Future outputs are tracked immutable agent artifacts and a tracked manifest.

| Stage | slug | standard outputs |
|---|---|---|
|2a|product-research|research, spec-draft, spec|
|2b|architect|architecture, implementation-plan|
|2c|compliance-reviewer|compliance-report|
|2d|engineer|implementation-report|
|2e|qa-release|review, test-report, release|
|2f|rule-manager|governance-report|

Use `python scripts/validate_artifact.py <exact-path>` and tracked manifests only. Root legacy files are not runtime inputs and are neither moved nor migrated.
