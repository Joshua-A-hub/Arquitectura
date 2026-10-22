# Feature Specification: [Feature Name]

- **ID**: `FEAT-[000]`
- **Status**: `Draft | In Review | Approved | In Development | Completed | Deprecated`
- **Owner / Author**: `[Name / Team]`
- **Target Release / Milestone**: `[vX.Y.Z]`
- **Created**: `YYYY-MM-DD`
- **Last Updated**: `YYYY-MM-DD`

---

## 1. Context & Problem Statement

Briefly describe the user problem, business objective, or technical driver. Why does this feature need to exist?

## 2. Goals & Non-Goals

### Goals
- [ ] Primary goal 1
- [ ] Primary goal 2

### Non-Goals
- Scope explicitly excluded from this specification.

## 3. User Personas & Use Cases

### Personas
- **Primary Persona**: Description of who is interacting with this feature.

### User Stories & Scenarios
- **US-1**: As a `[role]`, I want to `[action]`, so that `[benefit]`.
  - **Scenario 1.1**: Happy path description.
  - **Scenario 1.2**: Edge case or failure state description.

## 4. Detailed Requirements & Behavior

### Functional Requirements
- **FR-1**: The system MUST ...
- **FR-2**: When `[trigger]`, the system SHALL ...

### Non-Functional Requirements
- **Performance**: Response time, latency, throughput targets.
- **Security / Privacy**: Authentication, authorization, sensitive data handling.
- **Reliability / Observability**: Metrics, logging, audit trails, error budgets.

## 5. Technical Contracts & Data Schemas

### API / Interface Contract
Refer to or embed API schema (e.g., linked in `specs/contracts/`):
```yaml
# Example: OpenAPI / JSON Schema snippet or reference
```

### Data Model & Persistence
Entities, field types, relationships, constraints, or migration needs.

## 6. Acceptance Criteria (Given-When-Then / BDD)

```gherkin
Scenario: [Title of scenario]
  Given [precondition or initial state]
  When [action or event occurs]
  Then [expected outcome or assertion]
```

## 7. Verification & Test Plan

- **Unit Tests**: Coverage requirements and unit boundaries.
- **Integration Tests**: Integrations with external services or persistence layers.
- **Acceptance / Contract Tests**: Automated validation against `specs/contracts/` and Acceptance Criteria above.

## 8. Rollout & Rollback Strategy

- Feature flags / toggles:
- Rollout phases (e.g., canary, 10%, 100%):
- Failure triggers and rollback procedure:

## 9. Review & Sign-Off

| Role | Reviewer | Status | Date |
|------|----------|--------|------|
| Engineering Lead | | Pending | |
| Product / Stakeholder | | Pending | |
| QA / Testing | | Pending | |
