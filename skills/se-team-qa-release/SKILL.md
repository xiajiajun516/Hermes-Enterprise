---
name: se-team-qa-release
description: "QA role: OCR gate + review for the 3-stage pipeline."
category: software-development
---
# QA & Release
Review the engineer's commit at current HEAD.

1. **OCR mechanical review (optional, advisory)**: `ocr review --audience agent -b "<context>"` (requires a configured LLM) or `ocr delegate preview` + `ocr delegate rule <paths...>` (host-agent model, no OCR LLM needed). Treat High/Medium findings as input signals for the manual review — never trust blindly.
2. **Manual review** against `se-team-rules` → `review.md` with verdict `APPROVED` / `CHANGES_REQUESTED` / `REJECTED` and per-finding severity (critical/high/medium/low).
3. **Rule suggestion**: if the same mistake recurred across runs, append a one-line rule suggestion for the Master (e.g. "third NPE — add a null-check rule to se-team-rules").

Commit the review yourself: `git commit -m "docs(qa): <slug> review"`. Never rewrite git history or overwrite another stage's output.
Output template: `templates/review-template.md`.
