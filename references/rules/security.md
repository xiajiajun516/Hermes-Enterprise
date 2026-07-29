# Security & Safety Policy

## Critical Rules (Hard Constraints)
1. **No Credentials in Code**: Never hardcode API keys, passwords, or secrets. Use `.env` or secret stores.
2. **Approval Gate Operations**: The following actions require explicit user approval (`clarify`):
   - Physical file deletion (`rm -rf` / unrecoverable drop)
   - Database schema migrations & data deletions
   - Production deployments
   - Changing environment variables or core security policies
3. **Input Sanitization**: All user inputs and external API payloads must be validated and sanitized.
