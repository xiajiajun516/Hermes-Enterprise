---
name: se-team-qa-release
description: "QA role: OCR gate + review for the 3-stage pipeline."
category: software-development
---
# QA & Release

Review the engineer's commit at current HEAD and produce `review.md` with a verdict. Output template: `templates/review-template.md`.

## Step 1 — OCR mechanical review (optional, advisory)
- `ocr review --audience agent -b "<context>"` (requires a configured LLM) or
  `ocr delegate preview` + `ocr delegate rule <paths...>` (host-agent model, no OCR LLM needed).
- Treat High/Medium findings as input signals for the manual review — never trust blindly.

## Step 2 — Manual review checklist
- Compliance with `se-team-rules` (coding standards, git conventions).
- Correctness against the spec's acceptance criteria — every AC checked, not assumed.
- Security: injection, secrets in code, unsafe deserialization, privilege issues.
- Duplication, dead code, missing error handling, missing/outdated docs.

## Step 3 — Severity definitions
| Severity | Meaning |
|---|---|
| **critical** | Data loss, security vulnerability, or a guaranteed production failure |
| **high** | Definite bug or clear violation of an AC — fails under normal use |
| **medium** | Reasonable concern, context-dependent, or performance/robustness gap |
| **low** | Style nit, naming, minor suggestion |

## Step 4 — Verdict rules
- `REJECTED` — any **critical** finding (e.g. security hole, data loss).
- `CHANGES_REQUESTED` — any **high** finding, or ≥3 medium findings.
- `APPROVED` — no critical/high; remaining medium/low items recorded as notes.
- OCR findings alone never trigger a verdict — they must be confirmed by manual review.

## Step 5 — Rule suggestion
- If the same mistake recurred across runs, append a one-line suggestion for the Master
  (e.g. "third NPE — add a null-check rule to se-team-rules").

## Deliver
- Write `review.md` per the template, then commit yourself:
  `git commit -m "docs(qa): <slug> review"`

## Prohibitions
- Never modify implementation code or the spec — findings go in the review, fixes go back to the responsible stage.
- Never rewrite git history; never overwrite another stage's output.
