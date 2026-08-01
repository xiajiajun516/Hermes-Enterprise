# Review — <run>

## Run Identity
- **run**: <stage-slug>
- **stage**: qa
- **input commit**: <git ref>
- **created_at_utc**: <ISO-8601>

## OCR Mechanical Review (optional, advisory)
- **Command**: <ocr review ... / ocr delegate preview>
- **High findings**: <count + top items>
- **Medium findings**: <count + top items>

## 1. Code Quality Check
| Check | Status | Notes |
|:---|:---:|:---|
| Coding Standards (se-team-rules) | ✅/❌ | <evidence> |
| Code Duplication | ✅/❌ | <evidence> |
| Documentation | ✅/❌ | <evidence> |

## 2. Security Audit
- **Vulnerabilities Found**: <none, or list>
- **Severity**: <critical / major / minor per finding>

## 3. Findings
| # | Severity | Path:Line | Issue | Suggestion |
|:---|:---|:---|:---|:---|
| 1 | high | <path>:<line> | <issue> | <suggestion> |

## 4. Rule Suggestion (optional)
- <one-line suggestion for the Master, if the same mistake recurred across runs>

---
**Review Verdict**: `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`
