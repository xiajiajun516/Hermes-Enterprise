---
name: se-team-rules
description: "Combined project rules for se-team pipeline: design-system, git-workflow, security, tech-stack. Loaded by all se-team agents."
category: software-development
---

# Software Engineering Team — Project Rules

This skill contains all project standards and policies. Every agent in the Software Engineering AI Team pipeline loads this skill to ensure consistent compliance.

---

## 1. Design System & UI/UX Standards

### Core Principles
1. **Consistency**: Use unified UI design tokens across all components.
2. **Minimalism**: Clean and responsive UI design without unnecessary elements.
3. **Accessibility**: All interactive elements must be accessible and follow basic ARIA standards.

### Component Guidelines
- **Notifications**: Universal notification standard must use Toast components (avoid browser native `alert()`).
- **Styling**: Prefer modular CSS/Vanilla JS or established design tokens over unstructured inline styles.
- **Theme**: Support unified dark/light themes where specified.

---

## 2. Git Workflow & Commit Guidelines

### Branching Model
- `main`: Production-ready stability branch. All PRs target `main`.
- `feat/*`: Feature development branches.
- `fix/*`: Bug fix branches.

### Commit Message Format
Follow Conventional Commits: `<type>(<scope>): <short description>`

#### Allowed Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `rules`: Updates to core enterprise rules
- `agent`: Updates to subagent prompt configurations
- `chore`: Maintenance tasks

---

## 3. Security & Safety Policy

### Critical Rules (Hard Constraints)
1. **No Credentials in Code**: Never hardcode API keys, passwords, or secrets. Use `.env` or secret stores.
2. **Approval Gate Operations**: The following require explicit user approval:
   - Physical file deletion (`rm -rf` / unrecoverable drop)
   - Database schema migrations & data deletions
   - Production deployments
   - Changing environment variables or core security policies
3. **Input Sanitization**: All user inputs and external API payloads must be validated and sanitized.

---

## 4. Tech Stack & Code Quality Standards

### General Guidelines
1. **Lightweight Preference**: Prefer simple, maintainable vanilla solutions or lightweight frameworks over heavy bloat.
2. **Modular Architecture**: Clean separation of concerns (UI, Business Logic, Data Access).
3. **Testing Requirement**: All new core features must include basic unit test coverage.

### API Standards
- Standard API Error Response format: `{ "code": number, "message": string, "data": object | null }`.
- Restful resource naming conventions (plural nouns, kebab-case URLs).
