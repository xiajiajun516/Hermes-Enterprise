# Tech Stack & Code Quality Standards

## General Guidelines
1. **Lightweight Preference**: Prefer simple, maintainable vanilla solutions or lightweight frameworks over heavy bloat.
2. **Modular Architecture**: Clean separation of concerns (UI, Business Logic, Data Access).
3. **Testing Requirement**: All new core features must include basic unit test coverage.

## API Standards
- Standard API Error Response format: `{ "code": number, "message": string, "data": object | null }`.
- Restful resource naming conventions (plural nouns, kebab-case URLs).
