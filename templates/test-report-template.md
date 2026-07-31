# Test Report — <run-id>

## Run Identity
- **run_id**: <run-id>
- **agent_slug**: qa-release
- **stage**: <2e>
- **contract**: artifacts/runs/<run-id>__contract.md
- **created_at_utc**: <ISO-8601>

## Source Artifacts
- **inputs**: <paths matching contract inputs[]>

## Test Summary
| Metric | Value |
|:---|:---:|
| **Total Tests** | <number> |
| **Passed** | <number> |
| **Failed** | <number> |
| **Skipped** | <number> |
| **Coverage** | <percentage — stated as a number, not "good"> |

## Acceptance Criteria Verification
| Criteria | Status | Evidence |
|:---|:---:|:---|
| AC1 | ✅/❌ | <exact evidence path + command output> |
| AC2 | ✅/❌ | <exact evidence path + command output> |

> Every AC row carries an evidence path; a checkmark without evidence is a FAIL.

## Regression Check
- [ ] No regressions found <evidence>
- [ ] Performance impact acceptable <evidence>

---
**Test Verdict**: `PASS` / `FAIL`
