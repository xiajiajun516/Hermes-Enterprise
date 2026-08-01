---
name: se-team-qa-release
description: "QA role for Contract-only forward artifacts."
category: software-development
---
# QA & Release
Verify only exact tracked Contract inputs and their SHA. Create-new immutable `review`, `test-report`, or `release` under `artifacts/qa-release/`; never discover legacy or latest artifacts. Put actual command outcomes, tracking and risks in the manifest.
Output templates: `templates/review-template.md` (review), `templates/test-report-template.md` (test-report), `templates/release-template.md` (release).

## Optional Tool: OCR Mechanical Review (advisory)

If the `ocr` CLI (alibaba/open-code-review) is available, run it as a first-pass mechanical review. Optional — never a gate; Contract verification and SHA checks always take precedence.

```bash
command -v ocr || echo "ocr NOT INSTALLED"   # install: npm install -g @alibaba-group/open-code-review

# OCR-managed LLM (requires a configured LLM)
ocr review --audience agent -b "<business context>"

# or delegation mode (no OCR LLM needed; the QA agent reviews with its own model)
ocr delegate preview
ocr delegate rule <paths...>
```

- Treat High/Medium findings as input signals for the manual review; verify each against the exact Contract inputs before acting — never trust blindly.
- Optionally archive the raw OCR JSON output as a new immutable artifact under `artifacts/qa-release/` (e.g. `review-ocr-<run-id>.json`) and record it in the manifest like any other artifact.
- OCR operates on the Git repo at cwd; use `--repo <path>` if the repository root differs.
