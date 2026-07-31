# Compliance Review Report — <run-id>

## Run Identity
- **run_id**: <run-id>
- **agent_slug**: compliance-reviewer
- **stage**: <2c>
- **contract**: artifacts/runs/<run-id>__contract.md
- **created_at_utc**: <ISO-8601>

## Source Artifacts
- **inputs**: <paths matching contract inputs[]>

## Review Metadata
- **Target Artifact**: <path of the audited artifact>
- **Rules Audited**: <exact rule set + version, e.g. `se-team-rules` @ commit>
- **Attempt**: <N/5>

## Violations Identified
1. **[Violation Category]**:
   - **Found**: <what the artifact does>
   - **Rule Citation**: <exact rule id / section — every violation cites the rule>
   - **Required Action**: <what must change to comply>

## Non-Violations Checked
- <rule id>: <evidence that the artifact complies>

---
**Status Line**: `STATUS: PASS` or `STATUS: FAIL`
