---
name: se-team-qa-release
description: "QA role: semgrep+OCR gates + review, 3-stage pipeline."
category: software-development
---
# QA & Release

Review the engineer's commit at current HEAD and produce `artifacts/review/<DD-MM-YYYY>-review.md` with a verdict. Output template: `templates/review-template.md`. The exact output path (with the run date) comes from the dispatch context's `output:` field — write **exactly that path**, never a date or filename of your own.

## Step 1 — Semgrep pattern scan (zero-token, first)

Run Semgrep before any LLM review — pattern-based findings need no model. **Scope it to the commit under review, not the whole repo**, so pre-existing findings never pollute the review. The engineer commits exactly once per stage, so HEAD vs its parent is precisely the work under review:

```bash
# scan only the diff introduced by the engineer's commit (HEAD vs its parent)
git diff --name-only HEAD~1..HEAD | grep -E '\.(py|js|ts|tsx|jsx|go|java|rb|php|json|yaml|yml)$' > /tmp/changed-files.txt
semgrep scan --config auto --json --output semgrep-report.json $(cat /tmp/changed-files.txt)
```

- If `HEAD~1` doesn't exist (first commit), fall back to scanning the whole repo and note it in the review.
- Read `semgrep-report.json` findings: `check_id`, `path`, `line`, `severity`, `message`.
- Semgrep findings are **pattern-based signals**, not ground truth: the rule set comes from the Semgrep registry (`--config auto`) and may drift over time. Fold them into the findings table directly; only the *semantic* questions left over go to OCR / manual review. A finding that would affect a verdict must be confirmed by manual review first (same rule as OCR findings).

## Step 2 — OCR mechanical review (optional, advisory)
- `ocr review --audience agent -b "<context>"` (requires a configured LLM) or
  `ocr delegate preview` + `ocr delegate rule <paths...>` (host-agent model, no OCR LLM needed).
- Treat High/Medium findings as input signals for the manual review — never trust blindly.

## Step 3 — Manual review checklist
- Compliance with `se-team-rules` (coding standards, git conventions).
- Correctness against the spec's acceptance criteria — every AC checked, not assumed.
- Security: injection, secrets in code, unsafe deserialization, privilege issues.
- Duplication, dead code, missing error handling, missing/outdated docs.

## Step 4 — Severity definitions
| Severity | Meaning |
|---|---|
| **critical** | Data loss, security vulnerability, or a guaranteed production failure |
| **high** | Definite bug or clear violation of an AC — fails under normal use |
| **medium** | Reasonable concern, context-dependent, or performance/robustness gap |
| **low** | Style nit, naming, minor suggestion |

## Step 5 — Verdict rules
- `REJECTED` — any **critical** finding (e.g. security hole, data loss).
- `CHANGES_REQUESTED` — any **high** finding, or ≥3 medium findings.
- `APPROVED` — no critical/high; remaining medium/low items recorded as notes.
- OCR findings alone never trigger a verdict — they must be confirmed by manual review.

## Step 6 — Rule suggestion
- If the same mistake recurred across runs, append a one-line suggestion for the Master
  (e.g. "third NPE — add a null-check rule to se-team-rules").

## Deliver
- Write `artifacts/review/<DD-MM-YYYY>-review.md` per the template, then commit yourself:
  `git commit -m "docs(qa): <slug> review"`

## Prohibitions
- Never modify implementation code or the spec — findings go in the review, fixes go back to the responsible stage.
- Never rewrite git history; never overwrite another stage's output.
