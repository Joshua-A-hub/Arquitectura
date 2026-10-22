# Spec-Driven Development (SDD) Workflow

Spec-Driven Development places **specifications as the primary deliverable** preceding functional implementation. Code is treated as an implementation detail of the specification.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. Specify  │ ──> │  2. Contract │ ──> │ 3. Test Spec │ ──> │ 4. Implement │
│ (Feature Doc)│     │  (Schemas)   │     │ (Acceptance) │     │ (Source Code)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       ▲                                                              │
       └──────────────────── 5. Verify & Sync ────────────────────────┘
```

---

## The 5-Stage Lifecycle

### Stage 1: Specification (`specs/features/`)
- Draft requirements using `specs/templates/feature-spec-template.md`.
- Detail the problem statement, user personas, functional and non-functional requirements.
- Define acceptance criteria in Given-When-Then (BDD) notation.

### Stage 2: Contract Definition & Architecture (`specs/contracts/` & `specs/adr/`)
- If new endpoints or interfaces are introduced, draft contracts (e.g., OpenAPI, Protobuf, JSON Schema) in `specs/contracts/`.
- If high-impact architectural choices or trade-offs arise, author an Architectural Decision Record in `specs/adr/` using `specs/templates/adr-template.md`.
- Review and approve specs before writing code.

### Stage 3: Acceptance Tests First (`tests/acceptance/`)
- Translate the Given-When-Then scenarios from the feature spec into automated acceptance tests.
- Run tests and ensure they fail for the right reasons (Red phase).

### Stage 4: Code Implementation (`src/` & `tests/unit/`)
- Implement domain logic, interfaces, and handlers in `src/`.
- Write unit and integration tests alongside your code.
- Iterate until all unit, integration, and acceptance tests pass (Green phase).

### Stage 5: Verification & Documentation Sync
- Verify edge cases and performance requirements against the spec.
- If requirements adjusted during development, **update the specification** so the spec remains the true living documentation.
- Update the spec status to `Completed`.
