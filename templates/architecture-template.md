# Architecture — <run-id>

## Run Identity
- **run_id**: <run-id>
- **agent_slug**: architect
- **stage**: <2b>
- **contract**: artifacts/runs/<run-id>__contract.md
- **created_at_utc**: <ISO-8601>

## Source Artifacts
- **inputs**: <paths matching contract inputs[]>

## 1. System Design & Module Structure
- **Directory Tree**: <full project directory tree of the proposed structure>
- **Module Responsibilities**: <one line per module — what it owns and what it must not touch>

## 2. Data Flow
- **Request / Data Paths**: <how data flows between modules, end to end>
- **Failure Modes per Module**: <for each module: what breaks, how it fails, and the observable symptom>

## 3. API & Data Model
- **Endpoints / Interfaces**: <exact signatures or route shapes>
- **DB Schema / Data Models**: <fields, types, constraints>

## 4. Implementation Plan & Milestones
- **Milestones**: <M1, M2, … with a short deliverable per milestone>
