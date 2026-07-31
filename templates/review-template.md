# Review — <run-id>

## Run Identity
- **run_id**: <run-id>
- **agent_slug**: qa-release
- **stage**: <2e>
- **contract**: artifacts/runs/<run-id>__contract.md
- **created_at_utc**: <ISO-8601>

## Source Artifacts
- **inputs**: <paths matching contract inputs[]>

## Review Metadata
- **Reviewer**: <agent slug>
- **Target Artifact**: <path of the reviewed artifact>
- **Review Date**: <ISO date>

## 1. Code Quality Check
| Check | Status | Notes |
|:---|:---:|:---|
| Coding Standards | ✅/❌ | <evidence> |
| Code Duplication | ✅/❌ | <evidence> |
| Documentation | ✅/❌ | <evidence> |

## 2. Security Audit (mandatory)
- **Vulnerabilities Found**: <none, or list>
- **Severity**: <critical / major / minor per finding>
- **Recommendations**: <required fixes>

## 3. Diff Assessment
- **Files Changed**: <exact paths>
- **Lines Added/Removed**: <numbers>
- **Risk Level**: Low / Medium / High <justification>

> The verdict below must follow from the diff assessment and security audit.

---
**Review Verdict**: `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`
